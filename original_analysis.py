from pathlib import Path
import json,datetime as dt,numpy as np
import csv,gzip
W=Path(__file__).resolve().parent
spec=json.loads((W/'specification.json').read_text())
with (W/'source_manifest.csv').open(newline='') as f: sources=list(csv.DictReader(f))
names=sorted(r['subreddit'] for r in sources);source={r['subreddit']:r for r in sources};hours={n:{} for n in names}
for r in sources:r['current_partial_hours']=r['partial_hours'].split('|')
with gzip.open(W/'hourly_activity.csv.gz','rt',newline='') as f:
 for r in csv.DictReader(f):hours[r['subreddit']][r['timestamp_utc']]=int(r['posts_plus_comments'])
def stamp(t):return t.isoformat(timespec='minutes')
events=spec['events'];H=dt.timedelta(hours=1);D=dt.timedelta(days=1)
def times(e,k,w):
 t=dt.datetime.fromisoformat(e['anchor_utc'])+k*H
 a=[t+i*H for i in range(-w,w)];return [x for x in a if stamp(x) not in spec['excluded_hours_utc']],t
alltimes=sorted({t for e in events for k in e['offset_hours'] for w in [10,12] for t in times(e,k,w)[0]});ix={t:i for i,t in enumerate(alltimes)}
v=np.full((len(names),len(alltimes)),np.nan);expect=v.copy();z=v.copy()
for i,n in enumerate(names):
 partial=min(source[n]['current_partial_hours'])
 for t,jj in ix.items():
  ss=stamp(t);hist=[stamp(t-d*D) for d in spec['reference_lags_days']]
  if ss>=partial or ss not in hours[n] or any(h not in hours[n] for h in hist):continue
  vv=hours[n][ss];bb=np.array([hours[n][h] for h in hist]);v[i,jj]=vv;expect[i,jj]=bb.mean();z[i,jj]=np.log1p(vv)-np.log1p(bb).mean()
baseline=np.array([sum(vv for ss,vv in hours[n].items() if '2026-09-12'<=ss[:10]<='2026-10-06')/25 for n in names]);bench=np.where(baseline>=100)[0]
med=np.nanmedian(z[bench],axis=0);m=np.tile(med,(len(names),1))
for i in bench:m[i]=np.nanmedian(z[bench[bench!=i]],axis=0)
zb=z-m;eb=expect*np.exp(m)
def stat(e,k,w,adj=False):
 tt,t=times(e,k,w);idx=[ix[a] for a in tt];post=np.array([a>=t for a in tt]);x=post.astype(float);xc=x-x.mean();yy=(zb if adj else z)[:,idx];exp=(eb if adj else expect)[:,idx];obs=v[:,idx]
 yc=yy-yy.mean(axis=1,keepdims=True);cov=(yc*xc).mean(axis=1);vx=float(np.mean(xc*xc));vy=np.mean(yc*yc,axis=1)
 op=obs[:,post].sum(axis=1);ob=obs[:,~post].sum(axis=1);ep=exp[:,post].sum(axis=1);ee=exp[:,~post].sum(axis=1)
 with np.errstate(divide='ignore',invalid='ignore'):r=cov/np.sqrt(vx*vy);pct=100*((op/ep)/(ob/ee)-1)
 good=np.isfinite(r)&np.isfinite(pct)&(ee>=20)&(ep>=20)&(ob>0)
 return dict(r=r,pct=pct,cov=cov,vx=vx,vy=vy,good=good,op=op,ob=ob,ep=ep,eb=ee,n=len(tt),idx=idx,post=post.tolist())
cache={}
for ei,e in enumerate(events):
 for k in e['offset_hours']:
  for w in [10,12]:
   for adj in [False,True]:cache[(ei,k,w,adj)]=stat(e,k,w,adj)
def pooled(w,adj):
 a=[cache[(i,0,w,adj)] for i in range(3)]
 return np.mean([x['cov'] for x in a],axis=0)/np.sqrt(np.mean([x['vx'] for x in a])*np.mean([x['vy'] for x in a],axis=0))
r12=pooled(12,False);r10=pooled(10,False);rbench=pooled(12,True)
records=[];detail=[]
for i,n in enumerate(names):
 nom=[cache[(ei,0,12,False)] for ei in range(3)];nomok=baseline[i]>=100 and all(a['good'][i] for a in nom);nd=sum(a['good'][i] and a['r'][i]<0 and a['pct'][i]<0 for a in nom)
 stable={}
 for mode,settings in [('time_only',[(w,False) for w in [10,12]]),('time_and_benchmark',[(w,a) for w in [10,12] for a in [False,True]])]:
  stable[mode]=bool(nomok and all(cache[(ei,k,w,adj)]['good'][i] and cache[(ei,k,w,adj)]['r'][i]<0 and cache[(ei,k,w,adj)]['pct'][i]<0 for ei,e in enumerate(events) for k in e['offset_hours'] for w,adj in settings))
 r=dict(subreddit=n,baseline_day=float(baseline[i]),eligible=bool(nomok),decreases=int(nd),pooled_r=float(r12[i]),pooled_r_10h=float(r10[i]),pooled_r_benchmark=float(rbench[i]),**stable,events=[])
 for ei,e in enumerate(events):
  a=nom[ei];scenarios=[cache[(ei,k,w,False)] for k in e['offset_hours'] for w in [10,12]]
  rec=dict(event=e['event'],r=float(a['r'][i]),pct=float(a['pct'][i]),observed_pre=float(a['ob'][i]),observed_post=float(a['op'][i]),expected_pre=float(a['eb'][i]),expected_post=float(a['ep'][i]),n_hours=a['n'],pct_min=float(min(b['pct'][i] for b in scenarios)),pct_max=float(max(b['pct'][i] for b in scenarios)),all_timing_down=bool(all(b['good'][i] and b['r'][i]<0 and b['pct'][i]<0 for b in scenarios)))
  r['events'].append(rec)
  for k in e['offset_hours']:
   for w in [10,12]:
    for adj in [False,True]:
     b=cache[(ei,k,w,adj)];detail.append(dict(subreddit=n,event=e['event'],offset_hours=k,window_hours=w,benchmark_adjusted=adj,r=float(b['r'][i]),pct=float(b['pct'][i]),eligible=bool(b['good'][i])))
 records.append(r)
ranked=sorted([r for r in records if r['eligible'] and r['decreases']==3],key=lambda r:r['pooled_r'])
summary=dict(targets=len(records),eligible=sum(r['eligible'] for r in records),nominal_three_decreases=len(ranked),timing_stable=sum(r['time_only'] for r in ranked),timing_and_benchmark_stable=sum(r['time_and_benchmark'] for r in ranked),benchmark_series=len(bench))
def clean(obj):
 if isinstance(obj,float) and not np.isfinite(obj):return None
 if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items()}
 if isinstance(obj,list):return [clean(v) for v in obj]
 return obj
computed=clean(dict(summary=summary,results=records,ranked=ranked))
if __name__=='__main__':
 (W/'recomputed_analysis.json').write_text(json.dumps(computed,indent=2,allow_nan=False))
 print(summary)
