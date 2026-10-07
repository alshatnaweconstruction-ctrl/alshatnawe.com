"""Rejection advisor (owner decision D-129): read-only advice for every declined ad.

Input is the same read-only "My ads" snapshot Q-LIVE-DUP uses (master_plan/release_gates/evidence/
live_inventory_*.psv). For each declined ad it finds the service family, the active ads of that family
and the catalog service, and recommends ONE of:

- KEEP_ACTIVE      an ad of the same service is already active: do not repost; the declined one stays as history
- FROM_CATALOG     no active ad for the service, the catalog has it: prepare it through the normal pipeline
                   (quality validator, Q-LIVE-DUP, owner approval, one ad per import cycle)
- OWNER_DECIDES    the service is not in the catalog, or the title matches no family

By design it NEVER rewrites a declined ad's title or text, never reposts, edits, deletes or deactivates
anything, and never contacts Bazaraki. Rewording a declined duplicate to get it past moderation is the
pattern that produced the declined ads in the first place.

    python -m bazaraki_agent.rejection_advisor                     # latest snapshot
    python -m bazaraki_agent.rejection_advisor --inventory <psv>
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
from pathlib import Path

from bazaraki_agent import live_dup as L
from bazaraki_agent.feed import load_catalog

REPORT_DIR = L.WS / "master_plan" / "release_gates"
ACTIONS = ("KEEP_ACTIVE", "FROM_CATALOG", "OWNER_DECIDES")


def catalog_families(catalog: list[dict]) -> dict[str, list[str]]:
    """family -> catalog service keys (a service maps to its SERVICE_FAMILY entry, else to its own key)."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    for l in catalog:
        out[L.SERVICE_FAMILY.get(l["service_key"], l["service_key"])].append(l["service_key"])
    return dict(out)


def advise(inv: dict, catalog: list[dict]) -> list[dict]:
    active = [a for a in inv["ads"] if a["state"] == "A"]
    fams = catalog_families(catalog)
    published = {l["service_key"] for l in catalog if l.get("publish") is True}
    rows = []
    for a in inv["ads"]:
        if a["state"] == "A":
            continue
        fam = L.family_of(a["title"])
        same = [b["id"] for b in active if fam and L.family_of(b["title"]) == fam]
        services = fams.get(fam, []) if fam else []
        if same:
            action, why = "KEEP_ACTIVE", f"service already active as #{', #'.join(map(str, same[:3]))}" + (" …" if len(same) > 3 else "")
        elif services:
            todo = [s for s in services if s not in published]
            action, why = "FROM_CATALOG", f"no active ad; catalog service {', '.join(todo or services)} goes through the normal pipeline"
        else:
            action, why = "OWNER_DECIDES", "title matches no service family" if not fam else f"family {fam!r} is not in the catalog"
        rows.append({"id": a["id"], "title": a["title"], "category": a["category"], "created": a["created"],
                     "family": fam or "", "action": action, "why": why})
    return rows


def write_report(rows: list[dict], inv: dict, path: Path) -> None:
    by = collections.Counter(r["action"] for r in rows)
    fam = collections.Counter((r["family"] or "(none)", r["action"]) for r in rows)
    lines = [f"# Rejection advice ({dt.date.today().isoformat()})", "",
             f"Snapshot captured {inv['captured_at'].isoformat(timespec='minutes')}: "
             f"{sum(1 for a in inv['ads'] if a['state'] == 'A')} active, {len(rows)} declined.", "",
             "Read-only. Nothing is reworded, reposted, edited or deleted. A declined duplicate is never "
             "resubmitted with new wording; a missing service is prepared from the catalog through the "
             "normal pipeline with owner approval.", "",
             "| Action | Declined ads |", "|---|---|"] + [f"| {k} | {by.get(k, 0)} |" for k in ACTIONS]
    lines += ["", "## By service family", "", "| Family | Action | Ads |", "|---|---|---|"]
    lines += [f"| {f} | {a} | {n} |" for (f, a), n in sorted(fam.items())]
    lines += ["", "## Every declined ad", "", "| # | Title | Family | Action | Why |", "|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['title'].replace('|', '/')} | {r['family']} | {r['action']} | {r['why']} |" for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inventory", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    try:
        inv = L.load_inventory(a.inventory or L._latest_snapshot())
    except L.InventoryError as e:
        print(f"STOP: {e}")
        return 1
    rows = advise(inv, load_catalog())
    out = a.out or REPORT_DIR / f"REJECTION_ADVICE_{dt.date.today().isoformat()}.md"
    write_report(rows, inv, out)
    (out.with_suffix(".json")).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(dict(collections.Counter(r["action"] for r in rows)), "->", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
