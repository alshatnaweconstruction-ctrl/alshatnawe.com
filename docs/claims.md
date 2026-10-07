# Claims register

An ad may only make a claim that is listed here with evidence. `validate.py` blocks
common unsupported claims (warranty, "best", "free", licensed, insured, …) until they are listed here
and taken off its block list.

| Claim | Status | Evidence | Used in ads |
|---|---|---|---|
| Brand Al Shatnawe Construction, operated by VERTEKS S.A. CONSTRUCTION LTD, HE 495105 | Verified | `src/data/company.ts` (owner, 29 Sep 2026); public registry at efiling.drcor.mcit.gov.cy | All 73 (trust block) |
| Office at Agapinoros 8-6, 8049 Paphos | Verified | `src/data/company.ts` | All 73 (trust block) |
| "26 years of experience" | **Needs owner confirmation**: whose experience? The company was registered in 2023 | `company.ts` stats only | None |
| Warranty on work | **Unknown**: terms needed | none | None |
| Material brands (Knauf, Siniat, Gyproc…) | **Unknown**: which brands are actually used? | none | None |
