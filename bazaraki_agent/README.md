# bazaraki_agent (v0.2.0)

Local tooling for the Bazaraki ads of Al Shatnawe Construction / VERTEKS. **Nothing here logs in to Bazaraki, calls an API, or pushes to GitHub.** Bazaraki reads the LIVE feed `bazaraki.xml` (repo root) every hour; this tool never writes that file.

| File | Purpose |
|---|---|
| `catalog.json` | Source of truth for every ad (`publish:false` = draft) |
| `data/rates.json` | Owner-approved prices only (`approved_by`/`approved_date`) |
| `data/rates_draft.json` | Price research proposals (not used by the feed) |
| `data/published_ids.json` | Ledger of every external_id made live, so a live ID can never silently disappear |
| `data/bazaraki_official_list.txt` | Bazaraki's official categories, locations and title stop words |
| `../photos/manifest.csv` | Photo provenance, manifest v2 (see below) |
| `../photos/denylist.txt` | sha256 of images that may never be used (Pinterest origin, placeholders, AI renders) |
| `../docs/claims.md` | The only factual claims an ad may make |
| `feed.py` | `build` writes `build/bazaraki.xml` atomically (refuses malformed XML); `check` fails if stale |
| `validate.py` | Pre-publish gate (official and house rules) |
| `plan.py` | **Plan only**: what would be added, updated or DELETED on Bazaraki if published now |
| `official.py` | Parses the official list |
| `audit.py` | Heuristic image/inventory audit (read-only) |

## Commands (inside `feed-repo/`)
```bash
python -m unittest discover -s bazaraki_agent/tests -t .   # all tests
python -m bazaraki_agent.validate                          # 0 errors required
python -m bazaraki_agent.feed build                        # -> build/bazaraki.xml
python -m bazaraki_agent.feed check
python -m bazaraki_agent.plan [--all]                      # dry-run diff against the live feed
```

## Manifest v2 columns
`file, service_key, source (own|stock|ai_nano_banana_pro), rights_status (owned|licensed|generated|unverified), source_url, licence, project_ref, capture_date (YYYY-MM-DD), stage (before|during|after), relevance_reason, checksum_sha256, width, height, consent, approved (yes|no), approved_by, approved_date`

## Rules the validator enforces (summary)
- **Official:** valid category and location IDs; status `active`/`archive`/`remove` (`active_b2b` is off for services); title ≤ 70 characters, letters and digits only, no stop words, **no doubled words, no price in the title**; description ≤ 10,000; images JPG/PNG (extension and file signature), ≤ 16.
- **House:** one ad per `service_key`; no near-duplicate descriptions; Greek + English, no Arabic; no contacts, links or "Bazaraki"; claims only from `docs/claims.md`; price must equal the approved rate; ≥ 5 photos, each recorded in the manifest with matching source/rights, relevance, date, checksum and approval; no deny-listed image; AI images ≤ 2 and never the cover; the same photo is never used in two ads.
- **Lifecycle:** an external_id in `published_ids.json` can't be dropped, can't become a draft, and can't change its `service_key`. End it with `archive` or `remove`.

## Approval levels
Prices, new or removed ads, new photos and any publish need explicit owner approval. Publishing (copying `build/bazaraki.xml` over the live `bazaraki.xml` and pushing) is a separate, manual, owner-approved step. Check `plan` first.
