"""Offline replication: python reproduce.py (Python 3.10+ and numpy).
Verifies source snapshots, every hourly count, outputs, sensitivity rows,
and pooled correlations via an independent weighted residual calculation.
"""
from pathlib import Path
import csv,gzip,hashlib,re,datetime as dt,json
import numpy as np
P=Path(__file__).resolve().parent
for line in (P/'SHA256SUMS.txt').read_text().splitlines():
 sha,name=line.split('  ',1);assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,name
import analysis as a
cells=0
for r in a.sources:
 body=gzip.decompress((P/r['snapshot_file']).read_bytes());assert hashlib.sha256(body).hexdigest()==r['source_sha256'];parsed={}
 for match in re.finditer(r'<div[^>]*title="((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \w+ \d+ \d{2}:00 - [\d,]+)"[^>]*>',body.decode()):
  label,count=match[1].split(' - ');t=dt.datetime.strptime(r['window_end'][:4]+' '+label,'%Y %a, %b %d %H:%M')
  if t.date()>dt.date.fromisoformat(r['window_end']):t=t.replace(year=t.year-1)
  assert t.strftime('%a')==label[:3];parsed[t.isoformat(timespec='minutes')]=int(count.replace(',',''))
 assert parsed==a.hours[r['subreddit']];assert len(parsed)==744==int(r['hour_count'])
 assert sum(parsed.values())==int(r['posts'])+int(r['comments']);cells+=len(parsed)
def compare(x,y,path=''):
 if isinstance(x,dict):
  assert x.keys()==y.keys(),path
  for k in x:compare(x[k],y[k],path+'/'+k)
 elif isinstance(x,list):
  assert len(x)==len(y),path
  for i,(u,v) in enumerate(zip(x,y)):compare(u,v,path+'/'+str(i))
 elif isinstance(x,float):assert np.isclose(x,y,atol=1e-10,rtol=1e-10),(path,x,y)
 else:assert x==y,(path,x,y)
compare(a.computed,json.loads((P/'results.json').read_text()))
with gzip.open(P/'sensitivity.csv.gz','rt',newline='') as f:
 published=list(csv.DictReader(f))
assert len(published)==len(a.detail)
for raw,pub in zip(a.detail,published):
 for k,x in raw.items():
  y=pub[k]
  if isinstance(x,float):
   if np.isfinite(x):assert np.isclose(x,float(y),atol=1e-10,rtol=1e-10)
   else:assert y==''
  else:assert str(x)==y
# Independent weighted least-squares residualization, equal total event weights.
pieces=[a.cache[(i,0,12,False)] for i in range(3)]
x=np.concatenate([p['post'] for p in pieces]).astype(float)
Z=np.zeros((len(x),3));wt=np.zeros(len(x));off=0
for i,p in enumerate(pieces):
 nn=p['n'];Z[off:off+nn,i]=1;wt[off:off+nn]=1/nn;off+=nn
sw=np.sqrt(wt);zw=Z*sw[:,None]
def residual(v):return v-Z@np.linalg.lstsq(zw,v*sw,rcond=None)[0]
xr=residual(x)
for i,n in enumerate(a.names):
 y=np.concatenate([a.z[i,p['idx']] for p in pieces]);yr=residual(y)
 if np.isfinite(y).all() and np.sum(wt*yr**2)>1e-20:
  rr=np.sum(wt*xr*yr)/np.sqrt(np.sum(wt*xr*xr)*np.sum(wt*yr*yr))
  assert np.isclose(rr,a.r12[i],atol=1e-10,rtol=1e-10),n
print('PASS:',len(a.names),'source snapshots;',cells,'hourly cells;',len(published),'sensitivity rows; all results and weighted r values reproduced.')
print(a.summary)
