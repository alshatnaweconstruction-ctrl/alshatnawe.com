"""STEP 13: prepare the first publishing batch (bathroom, ceilings, repairs: no competing live ad).

Builds one PUBLISH_PACKAGE.md per service + FIRST_BATCH_READINESS.md in master_plan/first_batch/.
Read-only for everything else: no photo moves, no manifest/catalog/rates/XML change, no publish.
The dashboard approval queue is read read-only; queued approvals are reported but NOT treated as
approved (applying them is a separate, explicitly approved migration).

    python -m bazaraki_agent.first_batch
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from bazaraki_agent import ad_engine
from bazaraki_agent.registry import load_registry
from bazaraki_agent.validate import REPO

WS = REPO.parent
OUT = WS / "master_plan" / "first_batch"
QUEUE_DB = WS / "master_plan" / "dashboard" / "data" / "dashboard.db"
BATCH = ("repairs", "ceilings", "bathroom")       # proposed order inside the batch
MIN = 5


def _queued(queue_db: Path | None) -> dict:
    """{photo file: last pending action} from the dashboard DB, opened read-only."""
    if not queue_db or not Path(queue_db).is_file():
        return {}
    c = sqlite3.connect(f"file:{Path(queue_db).as_posix()}?mode=ro", uri=True)
    try:
        rows = c.execute("select item_id, action from approval_queue where item_type='photo' and status='pending' order by id").fetchall()
    finally:
        c.close()
    return dict(rows)


def _guard(out: Path) -> Path:
    o = Path(out).resolve()
    allowed = [OUT.resolve()]
    import tempfile
    allowed.append(Path(tempfile.gettempdir()).resolve())
    if not any(o == a or a in o.parents for a in allowed):
        raise ValueError(f"first_batch writes only to {OUT} (or a temp folder in tests), not {o}")
    return o


def build(out: Path = OUT, queue_db: Path | None = QUEUE_DB) -> dict:
    out = _guard(out)
    reg = {s["service_key"]: s for s in load_registry()["services"]}
    res = ad_engine.run(write=False)
    ads = {a["service_key"]: a for a in res["ads"]}
    queued = _queued(queue_db)
    services = {}
    for k in BATCH:
        a, s = ads[k], reg[k]
        photos = []
        for p in a["images"][:MIN]:
            stock = p.get("source") != "own"
            kind = "ai_illustrative" if p.get("source") == "ai_illustrative" else ("stock" if stock else "own")   # D-110
            photos.append({"file": p["file"], "name": Path(p["file"]).name, "type": kind,
                           "source": p.get("source"), "licence": p.get("licence") or ("own" if not stock else ""),
                           "source_url": p.get("source_url", ""), "relevance_reason": p.get("relevance_reason", ""),
                           "faces": p.get("people_or_faces", ""), "logos": p.get("logos_or_trademarks", ""),
                           "status": p.get("status"), "approved": p.get("status") == "approved" and p.get("approved") == "yes",
                           "queued": queued.get(p["file"], "")})
        approved = sum(ph["approved"] for ph in photos)
        n_queued = sum(1 for ph in photos if ph["queued"] == "approve" and not ph["approved"])
        comp = [x for x in a["problems"] if "near-duplicate" not in x and "reject:" not in x]
        dups = [x for x in a["problems"] if "near-duplicate" in x or "reject:" in x] + \
               [d for d in res["duplicates"] if d.startswith(k + ":")]
        missing = []
        if approved < MIN:
            missing.append(f"Owner must approve {MIN - approved} more photo(s) individually in the dashboard (Photos → Approve)")
        if n_queued:
            missing.append(f"{n_queued} approval(s) are queued: they still need the approved photo migration "
                           "(copy to feed-repo/photos/<service>/ + production manifest rows); this is not done in STEP 13")
        missing += ["Owner final review of the text, the photos and the price (D-044)",
                    "Decision on the 386 old XML IDs and on the XML URL (risk 1, XML_RISK_REGISTER.md)",
                    "Full-text backup of the 31 live ads (D-015) before the first push",
                    "Image URL check (HTTP 200) after the photos are pushed, before the XML switch (STEP 14)"]
        status = "blocked" if (comp or dups) else ("ready_to_publish" if a["status"] == "ready_to_publish" else "ready_to_review")
        cp = a.get("price_meta", {})
        services[k] = {"title_en": a["title_en"], "title_el": a["title_el"], "description": a["description"],
                       "price_en": cp.get("display_en"), "price_el": cp.get("display_el"), "unit": s["pricing"].get("unit"),
                       "rubric": str(a.get("rubric")), "district": str(a.get("district")), "language": (a.get("attrs") or {}).get("language"),
                       "photos": photos, "approved_photos": approved, "queued_approvals": n_queued, "compliance_problems": comp,
                       "duplicate_problems": dups, "live_ads": s.get("live_ads", {}), "status": status, "missing": missing}
    _write(out, services)
    return {"services": services, "out": str(out)}


def _write(out: Path, services: dict):
    for k, p in services.items():
        d = out / k; d.mkdir(parents=True, exist_ok=True)
        ph = "\n".join(f"| {i} | `{x['name']}` | {x['type']} | {x['source']} | {x['licence']} | {x['source_url']} | "
                       f"{x['relevance_reason'].replace('|', '/')[:90]} | {x['faces']} / {x['logos']} | {x['status']}"
                       f"{' · queued: ' + x['queued'] if x['queued'] else ''} | {'yes' if not x['approved'] else 'approved'} |"
                       for i, x in enumerate(p["photos"], 1))
        el, _, en = p["description"].partition("\n\nENGLISH\n\n")
        L = [f"# Publish package: {k} (STEP 13, NOT published)", "",
             f"**Status:** `{p['status']}` · approved photos {p['approved_photos']}/5 · queued {p['queued_approvals']}", "",
             "| Field | Value |", "|---|---|",
             f"| EN title (XML title) | {p['title_en']} ({len(p['title_en'])} chars) |", f"| Greek title | {p['title_el']} |",
             f"| Price | {p['price_en']} / {p['price_el']} |", f"| Unit | {p['unit']} |",
             "| VAT | excluded (Prices exclude VAT / Οι τιμές δεν περιλαμβάνουν ΦΠΑ) |",
             f"| Category (rubric) | {p['rubric']} |", f"| Location (district) | {p['district']} (Kato Paphos; all-Cyprus availability wording) |",
             f"| attrs.language | {p['language']} (Greek + English service languages, D-041) |",
             f"| Live ads of this service | {p['live_ads'].get('relationship')} {p['live_ads'].get('ids') or ''} (none, so no duplicate conflict) |", "",
             "## Photos (5 proposed)", "", "| # | File | Stock/own | Source | Licence | Source page | Why it fits | Faces / logos | Status | Needs owner approval |",
             "|---|---|---|---|---|---|---|---|---|---|", ph, "",
             "Stock photos are illustrative only. The ad text says so; it never calls them our work.", "",
             "## Compliance check", "", "- " + ("; ".join(p["compliance_problems"]) or "no problems (official title, description, image and attribute rules + claims, contacts, price, parity)"),
             "", "## Duplicate check", "", "- " + ("; ".join(p["duplicate_problems"]) or "no duplicates (other drafts, live titles, full-text similarity < 0.40)"),
             "", "## Missing before ready_to_publish", "", *[f"{i}. {m}" for i, m in enumerate(p["missing"], 1)],
             "", "In the XML `<description>` the Greek text comes first, then a separator line `ENGLISH`, then the English text "
             f"(total {len(p['description'])} / 10,000 characters).",
             "", "## Greek description (exact)", "", "```text", el, "```", "", "## English description (exact)", "", "```text", en, "```"]
        (d / "PUBLISH_PACKAGE.md").write_bytes(("\n".join(L) + "\n").encode("utf-8"))

    R = ["# First batch readiness (STEP 13, 2026-10-03)", "",
         "**Batch:** repairs, ceilings, bathroom. These services have **no live manual ad**, so the duplicate risk is low (transition plan W2a).",
         "**Nothing is published.** No photo moved, no production file changed.", "",
         "| Service | Status | Approved photos (owner) | Queued (not applied) | Needs approval | Compliance | Duplicates |", "|---|---|---|---|---|---|---|"]
    for k, p in services.items():
        R.append(f"| {k} | {p['status']} | {p['approved_photos']}/5 | {p['queued_approvals']} | {5 - p['approved_photos']} | "
                 f"{'OK' if not p['compliance_problems'] else 'PROBLEMS'} | {'none' if not p['duplicate_problems'] else 'FOUND'} |")
    R += ["", "## Photos that need your approval", ""]
    for k, p in services.items():
        R.append(f"- **{k}**: " + ", ".join(f"`{x['name']}`" for x in p["photos"] if not x["approved"]))
    R += ["", "## What blocks publishing (in order)",
          "1. **Photo approvals:** 15 photos (5 per service) approved individually in the dashboard. This blocks publishing.",
          "2. **Approved photo migration** (separate approval): copy the 15 files to `feed-repo/photos/<service>/` + production manifest v2 rows; re-run `ad_engine` → ready_to_publish; `validate` with publish:true = 0 errors (proven in the STEP 12 sandbox).",
          "3. **The 386 old XML IDs:** the first push of a new `bazaraki.xml` at the current URL deletes them (cleanup of ads that are already inactive). An explicit owner decision is needed.",
          "4. **Backups:** the full-text copy of the 31 live ads (D-015) + git/XML backup (XML_ROLLBACK_PLAN.md).",
          "5. **STEP 14 checks:** image URLs HTTP 200 after the photos are pushed; `plan.py` shows exactly +3 and the decided removals.", "",
          "## Proposed publishing order (after the approvals)",
          "- **One push with the 3 ads** (max 3 per batch rule): repairs → ceilings → bathroom in the catalog order.",
          "- **Monitoring:** 48 h read-only check (active / declined + reason).",
          "- **If declined:** fix and retry. There's no live ad to reactivate, because these services had none.",
          "- **Then:** W2b (remote-owner, kitchen after #30 is off), and then W3 replacements service by service."]
    (out / "FIRST_BATCH_READINESS.md").write_bytes(("\n".join(R) + "\n").encode("utf-8"))


def main() -> int:
    r = build()
    for k, p in r["services"].items():
        print(f"{k:10} {p['status']:16} approved {p['approved_photos']}/5 queued {p['queued_approvals']} "
              f"compliance {len(p['compliance_problems'])} duplicates {len(p['duplicate_problems'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
