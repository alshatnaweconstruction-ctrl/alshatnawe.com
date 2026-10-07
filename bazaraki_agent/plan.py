"""Plan-only mode: what WOULD change on Bazaraki if the feed were published now.

Compares the LIVE feed (bazaraki.xml at the repo root, which Bazaraki reads
hourly) with the feed that would be built from catalog.json now. Writes nothing.

Official XML spec: an external_id that disappears from the feed is DELETED on
Bazaraki, so every "removed" id below is an ad that would be deleted.

    python -m bazaraki_agent.plan            # summary + first ids of each group
    python -m bazaraki_agent.plan --all      # list every id
"""

from __future__ import annotations

import argparse
import sys

from bazaraki_agent.feed import LIVE_FEED, catalog_to_feed, feed_to_catalog, load_catalog, published
from bazaraki_agent.validate import load_ledger, validate


def _by_id(xml: str) -> dict[str, dict]:
    return {row.get("external_id", ""): row for row in feed_to_catalog(xml)}


def diff_feeds(live_xml: str, new_xml: str) -> dict[str, list[str]]:
    live, new = _by_id(live_xml), _by_id(new_xml)
    return {
        "added": sorted(set(new) - set(live)),
        "removed": sorted(set(live) - set(new)),
        "changed": sorted(i for i in set(new) & set(live) if new[i] != live[i]),
        "unchanged": sorted(i for i in set(new) & set(live) if new[i] == live[i]),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--all", action="store_true", help="list every id, not only the first 10")
    a = p.parse_args(argv)

    catalog = load_catalog()
    new_xml = catalog_to_feed(published(catalog))
    live_xml = LIVE_FEED.read_text(encoding="utf-8") if LIVE_FEED.is_file() else "<root></root>"
    d = diff_feeds(live_xml, new_xml)
    errors, warnings = validate(catalog)
    ledger_live = sum(1 for e in load_ledger() if e.get("status", "live") == "live")

    print("PLAN ONLY: nothing is written, pushed or published.\n")
    print(f"live feed  : {LIVE_FEED.name} ({len(_by_id(live_xml))} listings)")
    print(f"new feed   : from catalog ({len(published(catalog))} published of {len(catalog)} entries)")
    print(f"ledger     : {ledger_live} external_id(s) recorded as live by this system")
    print(f"validation : {len(errors)} error(s), {len(warnings)} warning(s)\n")
    for key, label in (("added", "NEW ads (go to moderation)"), ("changed", "UPDATED ads"),
                       ("removed", "WILL BE DELETED on Bazaraki"), ("unchanged", "unchanged")):
        ids = d[key]
        shown = ids if a.all else ids[:10]
        more = "" if a.all or len(ids) <= 10 else f" ... (+{len(ids) - 10} more, use --all)"
        print(f"{label:30}: {len(ids)}  {', '.join(shown)}{more}")
    if d["removed"]:
        print(f"\nWARNING: publishing now would DELETE {len(d['removed'])} ad(s) on Bazaraki. Owner approval required.")
    if errors:
        print("BLOCKED: fix validation errors before any publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
