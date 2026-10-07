"""STEP 10: safe XML build, validation, preview and diff (local only).

Builds master_plan/xml_preview/proposed_bazaraki.xml from catalog_proposed.json and the ad
engine output. Only ads that are ready_to_publish (5 photos APPROVED individually by the
owner, approved price, 0 problems, no compliance hold) can enter. candidate/proposed/on_hold
photos never enter. If nothing qualifies, a valid empty <root/> is written: no data is invented.

Never writes bazaraki.xml (the live file), catalog.json, rates.json or manifest.csv, never
changes the XML URL, never pushes or publishes.

    python -m bazaraki_agent.xml_preview
"""
from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from bazaraki_agent.feed import LIVE_FEED, RAW_PREFIX, catalog_to_feed, feed_to_catalog, write_feed
from bazaraki_agent.plan import diff_feeds
from bazaraki_agent.registry import load_registry
from bazaraki_agent.validate import LEDGER, load_ledger

WS = Path(__file__).resolve().parents[2]
OUT = WS / "master_plan" / "xml_preview"
CATALOG_PROPOSED = WS / "master_plan" / "catalog_system" / "catalog_proposed.json"
ADS = WS / "master_plan" / "ads" / "ads_proposed.json"
PHOTO_V3 = WS / "master_plan" / "photo_system" / "photo_manifest_v3.csv"
MIN_APPROVED = 5
MAX_IMAGES = 16
XML_FIELDS_DROP = ("price_meta", "registry_status", "coverage", "notes", "group", "publish")   # feed.FIELDS decides what is written


def _approved(photos, key):
    seen, out = set(), []
    for p in photos:
        if p["service_key"] == key and p.get("status") == "approved" and p.get("approved") == "yes" and p["checksum_sha256"] not in seen:
            seen.add(p["checksum_sha256"]); out.append(p)
    return out


def eligibility(entry, ad, photos, svc) -> list[str]:
    key, why = entry["service_key"], []
    if ad is None:
        return ["no ad for this service"]
    if ad.get("status") != "ready_to_publish":
        why.append(f"ad status {ad.get('status')!r} (needs ready_to_publish)")
    if ad.get("problems"):
        why.append(f"ad has {len(ad['problems'])} problem(s)")
    if ad.get("quality_passed") is not True:
        why.append("Advanced Ad Standard not passed (STEP 13.1 quality gate)")
    pm = entry.get("price_meta", {})
    if pm.get("approval_status") != "approved" or float(entry.get("price") or 0) <= 0:
        why.append("no approved price")
    if (svc or {}).get("hospitality", {}).get("compliance_required"):
        why.append("compliance gate (documents required)")
    if (svc or {}).get("ad_status") == "research_required":
        why.append("registry: research_required")
    n = len(_approved(photos, key))
    if n < MIN_APPROVED:
        why.append(f"only {n} approved photos (need {MIN_APPROVED}; candidate/proposed/on_hold never count)")
    return why


def _xml_row(entry, ad, photos):
    row = {k: v for k, v in entry.items() if k not in XML_FIELDS_DROP}
    row["title"], row["description"] = ad["title_en"], ad["description"]
    row["images"] = [RAW_PREFIX + f"photos/{entry['service_key']}/{Path(p['file']).name}" for p in _approved(photos, entry["service_key"])][:MAX_IMAGES]
    row["attrs"] = {"language": "10,20"}            # D-041: service languages Greek + English
    return row


def build_preview(entries, ads_by_key, photos, services, ledger, live_xml) -> dict:
    included, explicit, excluded = [], [], {}
    led_live = {l["external_id"] for l in ledger if l.get("status", "live") == "live"}
    for e in entries:
        key = e["service_key"]
        if e.get("status") in ("archive", "remove"):
            if e["external_id"] in led_live:              # official: archive/remove only for ads already on Bazaraki
                explicit.append({k: v for k, v in e.items() if k not in XML_FIELDS_DROP})
            else:
                excluded[key] = [f"status {e['status']} is only allowed for ads already uploaded"]
            continue
        why = eligibility(e, ads_by_key.get(key), photos, services.get(key))
        if why:
            excluded[key] = why
        else:
            included.append(_xml_row(e, ads_by_key[key], photos))
    xml = catalog_to_feed(included + explicit)
    ET.fromstring(xml)                                    # must parse
    ids = {i["external_id"] for i in included + explicit}
    errors = [f"ledger: live external_id {x} would disappear without an explicit archive/remove (official: removal deletes the ad)"
              for x in sorted(led_live - ids)]
    return {"included": included, "explicit": explicit, "excluded": excluded, "xml": xml, "errors": errors,
            "diff": diff_feeds(live_xml, xml)}


def additive_merge(live_xml: str, new_xml: str) -> dict:
    """D-072: additive-only feed (+new, -0). Every list-item of the current feed is carried over unchanged;
    new list-items are appended. An external_id that already exists is refused (no silent overwrite)."""
    live_root = ET.fromstring(live_xml)
    new_root = ET.fromstring(new_xml)
    old_ids = [i.findtext("external_id") for i in live_root.findall("list-item")]
    added = []
    for item in new_root.findall("list-item"):
        eid = item.findtext("external_id")
        if eid in old_ids:
            raise ValueError(f"external_id {eid} already in the live feed: additive publish may not overwrite it")
        live_root.append(item)
        added.append(eid)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(live_root, encoding="unicode")
    merged_ids = [i.findtext("external_id") for i in ET.fromstring(xml).findall("list-item")]
    removed = sorted(set(old_ids) - set(merged_ids))
    if removed:
        raise AssertionError(f"additive merge lost ids: {removed}")
    return {"xml": xml, "added": added, "removed": removed, "kept": len(old_ids)}


def _load_photos():
    with open(PHOTO_V3, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run(write: bool = True, data: dict | None = None) -> dict:
    """data (sandbox, STEP 12) may supply: entries, ads (dict), services, photos, ledger, live_xml. Default = real files."""
    data = data or {}
    entries = data.get("entries") or json.loads(CATALOG_PROPOSED.read_text(encoding="utf-8"))
    ads = data.get("ads") or {a["service_key"]: a for a in json.loads(ADS.read_text(encoding="utf-8"))}
    services = data.get("services") or {s["service_key"]: s for s in load_registry()["services"]}
    live_xml = data.get("live_xml") or LIVE_FEED.read_text(encoding="utf-8")
    photos = data["photos"] if "photos" in data else _load_photos()
    ledger = data["ledger"] if "ledger" in data else load_ledger()
    if write and data:
        raise ValueError("sandbox data must not be written to the real preview folder")
    res = build_preview(entries, ads, photos, services, ledger, live_xml)
    res["live_items"] = feed_to_catalog(live_xml)
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        write_feed(res["xml"], OUT / "proposed_bazaraki.xml")        # atomic + parse check; NEVER the live file
        from bazaraki_agent.xml_reports import write_reports
        write_reports(res, entries, ads, services)
    return res


def main() -> int:
    r = run(write=True)
    print(f"included {len(r['included'])} | explicit archive/remove {len(r['explicit'])} | excluded {len(r['excluded'])} | "
          f"ledger errors {len(r['errors'])} | diff: +{len(r['diff']['added'])} ~{len(r['diff']['changed'])} -{len(r['diff']['removed'])}")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
