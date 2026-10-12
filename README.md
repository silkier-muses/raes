# Reddit activity around three reported Yandex attacks

**Exploratory, AI-assisted analysis for independent review.** This repository examines public hourly subreddit activity around three reported attacks on Russian Yandex data centers on October 8, 9 and 11, 2026. The source data was retrieved October 12, 2026 UTC. It has not had independent statistical validation.

## Main result

| Screen | Communities |
|---|---:|
| Examined | 1,221 |
| Eligible under the primary activity/data rules | 968 |
| Decreased in all three selected 12-hour comparisons | 90 |
| Retained decreases across every tested start hour and both window lengths | **0** |

**All displayed rankings are provisional.** The analysis does not establish that the attacks caused Reddit activity changes, identify bots, locate users, or demonstrate use of Yandex servers. Zero passes under a strict timing rule also does not prove that no effect occurred.

## Start here

- [Methods and definitions](METHODS.md): exactly what `r` and percentage change measure, windows, historical reference hours, and limitations.
- [Readable results](RESULTS.md): US/European matches and all 90 nominal matches, including each incident's percentage change.
- [Compact results for every examined subreddit](summary.csv): retains positive and excluded series.
- [Full results](results.csv): event-level counts, expected counts, correlations and sensitivity flags.
- [Review questions](REVIEW_QUESTIONS.md): unresolved concerns, including carryover and multiple comparisons.
- [Infographic](infographic.png): the previously published mobile graphic, with US/Europe first.
- [Sources and citations](sources.csv) and [source manifest](source_manifest.csv).

## What was counted?

Syften's public, provider-observed **hourly posts plus comments in UTC**. These are not site visits, separate comment-only counts, or individual-user records. The 1,221-target set is a broad popular-subreddit screen supplemented with political and geographic communities, not a random sample or all of Reddit. Provider coverage and deletion handling cannot be independently established from aggregate snapshots.

## What was calculated?

For each incident, compare the selected 12-hour post-window with the immediately preceding 12 hours. Adjust each hour against the same UTC hour 7, 14 and 21 days earlier. Combine the within-incident correlations with equal total weight per incident. Repeat direction checks with 10-hour windows and a range of possible start hours; examine a broad-activity benchmark as an additional sensitivity check.

The start times are **analyst-selected proxies, not verified strike times**. A recorded Reddit outage removes two hourly bins from the first nominal pre-window. [METHODS.md](METHODS.md) explains the exact implementation.

This is a **descriptive stacked before-after comparison**, not a causally identified difference-in-differences estimate. It reports no inferential p-values or confidence intervals. The code was produced with ChatGPT and is included for scrutiny.

## Reproduce offline

Tested with Python 3.12 and NumPy 2.3.5. Download the repository files together, then run:

```bash
python -m pip install -r requirements.txt
python run_reproduction.py
```

After NumPy is installed, reproduction needs no network connection, account, API key or credentials. The runner checks the original source-archive SHA-256, verifies that the readable code/results copies match that archive, extracts to a temporary directory, and runs the original verifier. It checks:

- 1,221 source snapshots and 908,424 hourly cells;
- source totals against post-plus-comment counts;
- all results and 131,868 event-specific sensitivity rows;
- pooled correlations through an independent weighted-regression residual calculation.

`original_analysis.py` and `original_reproduce.py` are readable, unchanged copies of the original scripts. Run `run_reproduction.py` to supply their archived inputs automatically. Some constant/zero-volume series yield undefined correlations; these are excluded, and NumPy can emit an expected invalid-division warning before the verification passes.

Reproducing the arithmetic does not validate the data provider, event timing, causal assumptions, or interpretation.

## Original archive and provenance

[source_data.zip](source_data.zip) contains the complete, unchanged first release: original source HTML snapshots, all hourly data, methods, results, sensitivity scenarios, and hashes. It remains below GitHub's browser-upload per-file limit. The compressed archive keeps a browser upload to a small number of files while making the key material browsable separately.

- Original anonymous archive: <https://files.catbox.moe/eqj4gh.zip>
- Archive SHA-256: `bf93862bd93b17bc5fdea74e1dae84024b96e0dfa33010e057e678afbf8a5ed2`
- Original public infographic: <https://files.catbox.moe/3xe10s.png>

The original bundle's `geographic_selection.csv` includes a prior-model `analysis_status` field. For this study, use the current `eligible` field in `summary.csv` or `results.csv`. The old status is not current short-window eligibility.

No requester account details, credentials or personal/business metadata are included. Public provider boilerplate remains in preserved source snapshots. The original flag-art license is retained in [flag_icons_LICENSE.txt](flag_icons_LICENSE.txt). Original source content remains attributable to its providers; this repository makes no claim to ownership of it.

## Contributing a review

Please identify the file, formula or timing assumption you are examining. Useful contributions include independent replication, verified outage onset/recovery times, data-coverage checks, alternative controls, and a null/placebo design that accounts for serial dependence and searching many communities. Corrections should preserve the original release for comparison rather than silently replace its results.
