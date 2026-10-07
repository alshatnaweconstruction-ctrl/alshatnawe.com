# Q-LIVE-DUP: duplicate prevention against the live account (D-086)

**Why:** all 127 declined ads in the account carry one moderator reason, "Duplicate ad: the same ad is already active in your account or a different account". Our own checks compared drafts with each other, but not with what is already live.

**What it is:** `bazaraki_agent/live_dup.py`, an offline, read-only analyzer. It never contacts Bazaraki and never edits, deletes, deactivates, reactivates or publishes anything. It writes two files only:
- `master_plan/release_gates/LIVE_DUP_DRYRUN.md`: dry-run result per proposed ad
- `master_plan/services/LIVE_SERVICE_REGISTRY.csv`: one row per active ad (service family, category, location, claims, price, risk, wrong category, declined twins, active twins, text fingerprint, last verified, owner approval)

## Input: the live inventory snapshot
`master_plan/release_gates/evidence/live_inventory_<date>.psv`, captured read-only from the logged-in "My ads" list (GET `/api/items/front_my/?ordering=newest&page=N&status=all`). Header line `# captured_at: <ISO time>`; fields `id|state|category|title|price|created|views|phone_clicks|images|city`.

**Fail closed:** a missing, unreadable or empty snapshot, or one older than 24 h, blocks every proposal (`Q-LIVE-DUP-INV`). Capture a fresh snapshot before any publish decision.

## Rules
| Code | Type | When |
|---|---|---|
| Q-LIVE-DUP | block | an ACTIVE ad has the same service family as the proposal (family comes from the catalog `service_key`, so rewording the title, changing the town, price, category or punctuation does not change it), or the titles are ≥0.5 similar after removing towns, claims and filler words |
| Q-LIVE-DUP-IMG | block | a proposal image matches an active ad's image (sha256, or pHash ≤10), in any order |
| Q-LIVE-DUP-INV | block | inventory problem (fail closed) |
| W-LIVE-DECLINED | warning | the same service was declined before as a duplicate |
| W-LIVE-RELATED | warning | a related service is active (e.g. ceilings vs partitions, bathroom vs tiling): keep text and photos clearly different |
| W-LIVE-TITLE | warning | the title reads as another service than its service_key |
| X-OWNER-EXCEPTION | info | the owner approved this exact pair in `master_plan/release_gates/live_dup_exceptions.json` |

Pool work is split into `pool-care` and `pool-renovation`. The moderator declined skimmer, drain, leak and coping ads while a pool-care ad was active.

## Owner exception (the only bypass)
Add an object to `live_dup_exceptions.json`, with every field filled:
```json
[{"service_key": "partitions", "active_id": 6200619, "approved_by": "owner", "date": "2026-10-06", "reason": "..."}]
```
An exception covers only that service_key against that one active ad.

## Run
```
python -m bazaraki_agent.live_dup                     # latest snapshot vs master_plan/ads/ads_proposed.json
python -m bazaraki_agent.live_dup --inventory <psv> --proposed <json>
```
Tests: `bazaraki_agent/tests/test_live_dup.py`.
