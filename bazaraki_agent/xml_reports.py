"""Report writers for xml_preview.py (STEP 10)."""
from __future__ import annotations

import collections
import hashlib
import csv

from bazaraki_agent import xml_preview as xp

ORDER = ["new-build", "extensions", "structural", "full-renovation", "bathroom", "kitchen", "ceilings", "partitions", "painting",
         "tiling", "waterproofing", "remote-owner", "repairs", "pool-care", "pool-renovation", "concrete-repairs", "retaining-walls",
         "damp-repairs", "etics", "joinery", "electrical", "light-steel"]


def _w(name, lines):
    (xp.OUT / name).write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def write_reports(res, entries, ads, services):
    photos = xp._load_photos()
    cnt = collections.defaultdict(collections.Counter)
    for p in photos:
        cnt[p["service_key"]][p["status"]] += 1
    xml_md5 = hashlib.md5(res["xml"].encode("utf-8")).hexdigest()
    n_inc, n_exc = len(res["included"]), len(res["excluded"])
    live = res["live_items"]

    # ---- validation
    _w("XML_VALIDATION_REPORT.md", [
        "# XML validation report (STEP 10, 2026-10-03)", "",
        "**Source:** `master_plan/catalog_system/catalog_proposed.json` + `master_plan/ads/ads_proposed.json` + `photo_system/photo_manifest_v3.csv`. "
        "The real `catalog.json` was **not** used. **Official reference:** https://www.bazaraki.com/business-xml-guide/ (snapshot `official-docs/OFFICIAL_RULES_SNAPSHOT_2026-10-03.md`).", "",
        f"**Result:** {n_inc} listing(s) qualify. `proposed_bazaraki.xml` is a **valid empty `<root>`** (md5 {xml_md5})." if n_inc == 0 else
        f"**Result:** {n_inc} listing(s) in `proposed_bazaraki.xml` (md5 {xml_md5}).",
        "**Why:** no service has 5 photos approved individually by the owner yet (D-031: Top 5 = proposed only). Nothing was invented to fill the file.", "",
        "| Gate (all must pass) | Source |", "|---|---|",
        "| ad status `ready_to_publish` (0 problems; 5 unique APPROVED photos; approved price) | INTERNAL (D-028, D-044) |",
        "| price approved in rates.json and > 0 | INTERNAL (D-009) |",
        "| not research_required; no compliance hold (electrical) | INTERNAL (D-034/D-048) |",
        "| only approved photos; candidate / proposed / on_hold never enter; max 16 URLs; JPG/PNG | OFFICIAL (0-16, JPG/PNG) + INTERNAL |",
        "| one rubric + one district from the official list | OFFICIAL |",
        "| title ≤ 70, text and digits, no stop words / doubled words / price | OFFICIAL (checked by `ad_engine`) |",
        "| description ≤ 10,000; ' \" & < > escaped; no CDATA | OFFICIAL (`feed.catalog_to_feed`) |",
        "| `attrs.language = 10,20` | OFFICIAL attribute; value D-041 |",
        "| new ads `status=active`; archive/remove only for IDs already uploaded (ledger) | OFFICIAL |",
        "| no live external_id disappears without explicit archive/remove | OFFICIAL consequence + ledger |",
        "| XML parses (atomic write refuses malformed XML) | `feed.write_feed` |", "",
        f"**Ledger errors:** {len(res['errors'])} (ledger is empty: this system has never published).",
        f"**Excluded:** {n_exc} services (see `XML_LISTING_PREVIEW.md`).",
        "", "Live `bazaraki.xml`, `catalog.json`, `rates.json` and `manifest.csv` were not modified (verified by md5 in tests)."])

    # ---- diff
    rub = collections.Counter(i.get("rubric") for i in live)
    st = collections.Counter(i.get("status") for i in live)
    D = ["# XML diff report (STEP 10, 2026-10-03)", "",
         "Compared: `proposed_bazaraki.xml` (new) vs `feed-repo/bazaraki.xml` (the live file the Bazaraki profile URL points to; identical to GitHub main at d843c5f).", "",
         f"| | Count |", "|---|---|", f"| Live listings (old XML) | {len(live)} |", f"| New listings | {len(res['included']) + len(res['explicit'])} |",
         f"| Added | {len(res['diff']['added'])} |", f"| Changed | {len(res['diff']['changed'])} |", f"| **Removed = would be DELETED on Bazaraki** | **{len(res['diff']['removed'])}** |",
         f"| Unchanged | {len(res['diff']['unchanged'])} |", "",
         f"Old XML profile: statuses {dict(st)}; rubrics {dict(rub)}. ID series: LEO-SV ×{sum(1 for i in live if i['external_id'].startswith('LEO-SV'))}, "
         f"LEO-PB ×{sum(1 for i in live if i['external_id'].startswith('LEO-PB'))}, LEO-INS ×{sum(1 for i in live if i['external_id'].startswith('LEO-INS'))}.", "",
         "## What this means",
         "- **Official rule:** if an `external_id` of an existing Bazaraki ad is removed from the XML, that ad is deleted from Bazaraki.",
         "- If the profile XML URL served `proposed_bazaraki.xml` now, Bazaraki would try to **delete all 386 LEO-* ads**. Earlier analysis: they are already inactive or deleted on Bazaraki (216 titles match inactive ads; none matches the 31 active ads). The result would be cleanup, not a loss, but it is irreversible and must be a separate owner decision.",
         "- **The 31 live manual ads are NOT affected:** they have no `external_id`, so no XML can delete or change them.",
         "- **Why the XML link must not be changed now:**",
         "  - (1) 0 listings qualify, so the switch would only delete things;",
         "  - (2) the 386-ID deletion needs its own decision;",
         "  - (3) W1 (deactivating the 13 archive ads) is postponed (D-049), and replacements must go live service by service right after each manual deactivation;",
         "  - (4) every change goes through approval (STEP 13/14).",
         "", "## Full list of potential deletions (old XML IDs absent from the new XML)", "", "| # | external_id | status | rubric | title |", "|---|---|---|---|---|"]
    by = {i["external_id"]: i for i in live}
    for k, x in enumerate(res["diff"]["removed"], 1):
        i = by.get(x, {})
        D.append(f"| {k} | {x} | {i.get('status', '')} | {i.get('rubric', '')} | {(i.get('title') or '')[:70].replace('|', '/')} |")
    _w("XML_DIFF_REPORT.md", D)

    # ---- listing preview
    ad_by = ads
    P = ["# XML listing preview (STEP 10, 2026-10-03)", "",
         f"**Qualifying listings: {n_inc} of 22.** Each row shows what blocks the service from entering the XML.", "",
         "| # | Service | Ad status | Price | Photos approved / proposed / on_hold | In XML? | Blocking reasons |", "|---|---|---|---|---|---|---|"]
    ent = {e["service_key"]: e for e in entries}
    for i, k in enumerate(ORDER, 1):
        e, a = ent.get(k, {}), ad_by.get(k, {})
        pm = e.get("price_meta", {})
        price = pm.get("display_en") or "no approved price"
        c = cnt[k]
        inc = any(r["service_key"] == k for r in res["included"])
        P.append(f"| {i} | {k} | {a.get('status')} | {price} | {c['approved']} / {c['proposed']} / {c['on_hold']} | {'YES' if inc else 'no'} | "
                 f"{'; '.join(res['excluded'].get(k, [])) or '—'} |")
    P += ["", "**To make a service qualify:**",
          "1. The owner approves 5 photos individually (`photo_pipeline.py approve`).",
          "2. Copy them to `feed-repo/photos/<service>/` + production manifest rows (separate approved migration).",
          "3. Re-run `ad_engine` (→ ready_to_publish).",
          "4. Re-run `xml_preview`.",
          "Services without a price also need an approved price in `rates.json`."]
    _w("XML_LISTING_PREVIEW.md", P)

    # ---- risk register
    _w("XML_RISK_REGISTER.md", [
        "# XML risk register (STEP 10, 2026-10-03)", "",
        "| # | Risk | Likelihood | Impact | Control in the system | Owner action |", "|---|---|---|---|---|---|",
        "| 1 | Switching the profile XML now deletes the 386 old LEO-* ads | certain if switched | high, irreversible | the diff lists all 386; no switch without a decision | decide: delete them (cleanup) or first archive them |",
        "| 2 | New ad declined as a duplicate because the old manual ad of the same service is still active | high | medium | transition plan W3: deactivate first, push the same hour; 48 h check; reactivate on decline | follow the wave order |",
        "| 3 | An ad publishes with unapproved (candidate/on_hold) photos | blocked | high | `xml_preview` uses approved photos only (test) | approve photos individually |",
        "| 4 | Unapproved or zero price | blocked | high | price gate (test) | approve prices for the 8 drafts |",
        "| 5 | Electrical ad without legal basis | blocked | high (legal) | compliance gate; no licence words | provide EMS documents |",
        "| 6 | A live external_id disappears later by mistake | blocked | high | ledger rule: error unless explicit archive/remove (test) | — |",
        "| 7 | Photo URL changed after upload is ignored (Bazaraki fetches once per URL) | medium | low | new file name per changed photo (photo rules) | — |",
        "| 8 | Hospitality variant published together with its main ad = duplicate | medium | medium | variants are separate drafts, never in the XML | choose one per service |",
        "| 9 | Images not reachable at the raw GitHub URL at publish time | medium | medium | STEP 12/13: HTTP 200 check of every image URL before the push | approve the push |",
        "| 10 | Moderation delay (official: ≥ 1 h, depends on moderators) | certain | low | 48 h monitoring window | — |",
        "| 11 | Wrong district/category | low | medium | official ID validation (registry + validate) | — |",
        "| 12 | Old XML URL still set while no new XML exists: the stale 386 'active' items keep being offered to the importer | ongoing | low–medium | none in this step (URL unchanged by instruction) | decide the URL with risk 1 |"])

    # ---- rollback plan
    _w("XML_ROLLBACK_PLAN.md", [
        "# XML rollback plan (STEP 10, 2026-10-03)", "",
        "**Current state, nothing to roll back:** no XML was published, the profile URL is unchanged, and no live ad was touched. `proposed_bazaraki.xml` exists only in `master_plan/xml_preview/`.", "",
        "## Before any future publish (STEP 13/14)",
        "1. Back up the live `bazaraki.xml` (copy + md5 1284b8fbfa5f385935db2e5a02c5fa46) and the git commit (d843c5f).",
        "2. Record the profile XML URL value and a screenshot (owner).",
        "3. Save the full-text copy of all live ads (D-015, Chrome).",
        "4. Run `plan.py` and `xml_preview` and keep the diff report with the release.", "",
        "## Rollback cases",
        "| Case | Rollback |", "|---|---|",
        "| New XML pushed, ads declined | Revert the commit (`git revert`) to the previous XML. Reactivate the manual ads that were deactivated for the replacement (within about 14 days). Record the decline reason |",
        "| Wrong content in a published ad | Fix the catalog/ad, bump `last_update` (official: unchanged `last_update` is skipped), push. If urgent: set `status=archive` for that external_id (official), never just delete it from the XML |",
        "| An external_id removed by mistake (ad deleted on Bazaraki) | It cannot be undone on Bazaraki: re-add it as a new ad (moderated as new). This is why the ledger blocks removal without explicit archive/remove |",
        "| XML URL switched by mistake | Owner restores the previous URL in profile settings. Bazaraki re-reads within about 1 hour; the deletions already done can't be reversed (see risk 1) |",
        "| Photos wrong | Upload under NEW file names (Bazaraki fetches once per URL), update the URLs, bump `last_update` |", "",
        "## Verification after rollback",
        "- Read-only account check (active / declined / inactive counts)",
        "- `feed check`",
        "- md5 of the restored XML"])
