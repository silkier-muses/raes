# Methods: what the numbers mean

This document makes the first-release code easier to inspect. It does not introduce a new analysis or revise any numerical result. The full original description is [ORIGINAL_METHODS.txt](ORIGINAL_METHODS.txt), and the machine-readable choices are in [specification.json](specification.json).

## Outcome and historical reference

Let `C(s,t)` be the provider-observed number of posts plus comments in subreddit `s` during UTC hour `t`.

For each hour, use exactly three historical matches, not all hours in a rolling three-week window:

```text
E(s,t) = mean(C(s,t-7 days), C(s,t-14 days), C(s,t-21 days))

Y(s,t) = log(1 + C(s,t))
         - mean(log(1 + C(s,t-k days))) for k in {7,14,21}
```

`E` is the arithmetic expected count used for percentages. `Y` is the adjusted log activity used for correlations. These two quantities are intentionally different; a large count spike can affect them differently.

For example, an October 11 hour is matched to the same hour on October 4, September 27 and September 20. All historical reference hours in this study precede the first reported October 8 incident. However, the immediately preceding comparison window for a later incident can still contain lingering disruption from an earlier incident. **That carryover is not resolved by the historical adjustment.**

## Timing and window definitions

| Reported facility | Nominal anchor, UTC | Tested start hours, UTC, inclusive |
|---|---|---|
| Sasovo | 2026-10-08 00:00 | Oct 7 21:00 through Oct 8 03:00 |
| Kaluga | 2026-10-09 03:00 | Oct 8 21:00 through Oct 9 09:00 |
| Vladimir | 2026-10-11 01:00 | Oct 10 21:00 through Oct 11 03:00 |

The anchors are analyst-selected proxies based on reporting and company alerts. An alert time is not a strike time. The sweeps are sensitivity scenarios, not confidence intervals or claims that each possible time is equally likely. See [sources.csv](sources.csv) and [specification.json](specification.json).

For an anchor `T` and window length `w`:

- pre-window: `[T-w, T)`;
- post-window: `[T, T+w)`;
- primary length: 12 hours per side;
- sensitivity length: 10 hours per side.

UTC hours October 7 19:00 and 20:00 are excluded because of a documented Reddit status incident. Nominal Sasovo therefore has 10 usable pre-hours and 12 post-hours. The other two nominal comparisons have 12 + 12. Expected counts use only retained hours, so percentage calculations account for the unequal retained lengths.

Nominal windows do not overlap. Some shifted sensitivity windows can overlap. Even non-overlapping windows are not necessarily independent: continuing outages and shared news can connect them. Recovery after 10 or 12 hours is not assumed or established.

## Exactly what `r` correlates

For each hour, define `X = 0` before the selected anchor and `X = 1` after it. A binary indicator has variance when both values occur. Pearson correlation can compare a binary indicator with a numerical outcome; the simple unadjusted case is commonly called point-biserial correlation. [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pointbiserialr.html) explains this equivalence.

Here, the published combined statistic is a **weighted within-incident Pearson correlation** between `X` and adjusted log activity `Y`. It controls for incident intercepts by subtracting each incident's own means from both variables. Each incident gets the same total weight; each retained hour in incident `e` gets weight `1/n_e`.

```text
xc = X - mean_e(X)
yc = Y - mean_e(Y)

cov_e = mean_e(xc * yc)
vx_e  = mean_e(xc * xc)
vy_e  = mean_e(yc * yc)

combined_r = mean_over_events(cov_e)
             / sqrt(mean_over_events(vx_e) * mean_over_events(vy_e))
```

This is a weighted partial correlation controlling for incident intercepts. The verifier also obtains it by weighted least-squares residualization.

- Negative `r`: lower adjusted log activity tends to occur in the selected post-windows.
- `r` near -1: stronger negative linear association after adjustment.
- `r` near zero: weak linear association in this comparison.
- `r` does not measure users, bot prevalence, percent lost, or a continuing decline as time passes.

The calculation is mathematically defined, but that alone does not establish reliable statistical inference or causal identification. Serially correlated hours are not independent replications of an attack. We do not report naive hourly-observation p-values.

## Percentage changes

Calculate each incident's percentage separately:

```text
100 * [(observed_post / expected_post)
       / (observed_pre / expected_pre) - 1]
```

Observed and expected values are sums across the retained hours of each half-window. This measures a seasonally normalized before/after change, not a raw difference between two totals. The log-based `r` and count-based percentage can have different signs. Both must be negative for an incident to count as a decrease.

## Eligibility and rankings

- At least 100 posts + comments per day on average over September 12-October 6 UTC.
- Complete required hourly data and historical matches in every nominal incident.
- At least 20 expected counts in each half-window, positive observed pre-count, and finite correlation/percentage.
- A nominal repeated decline requires negative `r` and negative percentage in all three nominal 12-hour comparisons.
- The infographic ranks nominal matches by lowest combined `r` and separately shows the selected geographic/political matches.

Out of 1,221 examined series, 968 qualify and 90 match all three nominal comparisons. Positive and excluded results remain available in [summary.csv](summary.csv) and [results.csv](results.csv). Selecting extreme negative results from many communities is not a significance test and can amplify chance patterns.

## Sensitivity checks

Test all hourly start options in the timing table and both 10/12-hour lengths. The `time_only` flag requires both decrease signs and eligibility at every event-specific scenario. This is a deliberately strict rule, not a calibrated hypothesis test.

An additional benchmark check subtracts each hour's median adjusted log activity among the 972 series with sufficient baseline volume. The target is excluded from its own benchmark where applicable. Expected counts are multiplied by the exponentiated median adjustment. This checks dependence on broad activity changes, but the benchmark is not a verified untreated control and could absorb part of a genuine widespread effect.

There are 54 timing-only event-specific scenarios per target and 108 when including both benchmark options: 131,868 sensitivity rows overall. These are alternative scenarios, not 108 independent events.

**All 90 nominal matches fail at least one timing-only direction check.** Their failure is not solely a low-volume eligibility issue. Zero passes do not prove a null effect; they show that the selected pattern is not stable under this particular sensitivity definition.

## Limits of the design

This is a descriptive stacked before-after comparison. It is not an application of a causally identified stacked difference-in-differences ATT estimator, and no credible untreated group or known treatment exposure has been established.

Unresolved issues include only three nearby incidents, uncertain onset and recovery, serial dependence, carryover into later pre-windows, possible overlap in shifted windows, sparse historical matches, news/sports/holiday/moderation effects, provider coverage, and exploratory selection across many series. No held-out validation, community-specific news audit, formal multiplicity-adjusted inference or causal confidence interval is supplied.

Relevant methodological background is listed in [sources.csv](sources.csv), including Wing et al. on stacked DiD weighting, Cameron and Miller on clustered inference, and Lopez Bernal et al. on interrupted time series. These references inform caution; citing them does not establish their identification assumptions here.
