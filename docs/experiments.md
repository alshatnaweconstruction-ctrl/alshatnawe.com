# Bazaraki experiment log

One row per experiment. Change one variable at a time; the other arm runs over the same dates as the control.

## EXP-001: Greek vs English titles

| Field | Value |
|---|---|
| Status | **Pending approval.** Starts when this change is merged and Bazaraki re-imports the feed |
| Hypothesis | Greek titles match how most Cypriot homeowners search, so Greek-title ads get more views and enquiries per ad than English-title ads |
| Variable | Title language only. Greek titles are close translations of the English ones (same service, same location word) |
| Arms | Within each topic cluster (by ID order) alternate ads get a Greek title. **Greek (39):** 002 004 006 008 010 012 014 016 018 021 022 024 026 028 030 032 034 036 038 040 042 044 046 048 050 052 054 056 059 061 062 064 066 069 071 072 074 076 078. **English control (34):** 003 005 007 009 013 015 017 020 023 025 027 029 031 033 035 037 039 041 043 045 047 049 051 053 055 058 060 063 065 067 070 073 075 077 |
| Same-day change in both arms | The bilingual trust block was added to all 73 ads, so it affects both arms equally |
| Data needed | Views and enquiries per ad, exported by hand from the Bazaraki dashboard at day 0 and day 30 → `docs/bazaraki/data/YYYY-MM-DD.csv` (`external_id,views,enquiries`) |
| Primary metric | Views per ad over 30 days, Greek arm vs control arm |
| Secondary | Enquiries per ad; enquiry/view rate |
| Decision rule | Roll Greek titles out to all ads if the Greek arm is ≥ 20% higher on views per ad **and** higher in at least 5 of the 8 clusters. Otherwise keep English and log the result |
| Rollback | `git revert` the title commit and rebuild the feed. Original English titles are kept in git history |
| Result | UNKNOWN (not started) |

## Lessons learned

| Date | Problem | Cause | Rule added |
|---|---|---|---|
| 2026-09-30 | Claim filter flagged "καλύτερη ηχομόνωση" ("better sound insulation") | Greek comparative and superlative share a stem | Only article + καλύτερ- ("the best") is blocked, matched on accent-folded text (`validate.py`) |
