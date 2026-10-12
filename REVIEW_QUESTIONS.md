# Questions for independent review

The intent is to make the assumptions inspectable, not to invite confirmation of a predetermined bot-farm explanation.

1. **Timing:** Are there reliable, independently sourced outage-onset and recovery timestamps? Company notices and first user complaints are not exact strike timestamps.
2. **Carryover:** How should continuing disruption from the first incident be handled in the pre-windows of the second and third? Would treating this as one disruption episode be more defensible?
3. **Null comparisons:** With longer pre-event data, what matched-date or block-based placebo scheme would preserve hour-of-week rhythms and serial dependence? Three nearby incidents offer limited independent information.
4. **Selection:** How should searching across 1,221 series and publishing the most negative nominal matches be accounted for? A held-out period or pre-specified subset would help avoid selecting on noise.
5. **Controls:** Is there a credible unaffected comparison series? A median of broad Reddit activity is only a sensitivity benchmark, not proof of an untreated counterfactual.
6. **Provider data:** Can hourly counts, collection coverage, deletions and outages be checked against an independent source? Reconstructing the provider's own totals is not independent coverage validation.
7. **Presentation:** Would per-incident observed/expected plots convey the limitations better than ranking by pooled `r`? All ranks should retain the timing caveat.

Reports of code errors should name the relevant file and provide a minimal reproducible example. Reanalysis should keep the original release available and identify any changed inputs or assumptions. No user-level data is needed to review this package.
