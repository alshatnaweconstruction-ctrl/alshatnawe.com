"""Catalog <-> Bazaraki XML feed conversion.

bazaraki_agent/catalog.json is the editable source of truth for every listing.
The feed is generated into build/bazaraki.xml (local, not tracked by git).

The LIVE feed is LIVE_FEED = bazaraki.xml at the repo root: Bazaraki downloads it
every hour from the URL set in the account's XML settings
(https://raw.githubusercontent.com/alshatnaweconstruction-ctrl/alshatnawe.com/main/bazaraki.xml).
This tool never writes the live file. Replacing it is a separate, owner-approved
step, because removing a published external_id from the live XML makes Bazaraki
DELETE that ad (official XML spec).

Only listings with "publish": true are written. Catalog-only fields
(service_key, publish, notes, ...) never reach the XML.

    python -m bazaraki_agent.feed build     # catalog.json -> build/bazaraki.xml
    python -m bazaraki_agent.feed check     # fail if build/bazaraki.xml is stale
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "bazaraki_agent/catalog.json"
FEED = REPO / "build" / "bazaraki.xml"   # generated locally; not the live file
LIVE_FEED = REPO / "bazaraki.xml"         # read by Bazaraki hourly: never written here
RAW_PREFIX = "https://raw.githubusercontent.com/alshatnaweconstruction-ctrl/alshatnawe.com/main/"

# Field order of a <list-item>, as Bazaraki's import format lays it out.
FIELDS = ["last_update", "external_id", "status", "rubric", "district", "title",
          "description", "price", "negotiable_price", "exchange", "phone_hide",
          "chosen_phone", "whatsapp", "disallow_chat", "images", "attrs", "geometry"]

# The official spec asks for ' and " as HTML entities too, not only & < >.
ENTITIES = {"'": "&apos;", '"': "&quot;"}


def atomic_write_text(path: Path, text: str) -> None:
    """Write via a temp file in the same folder, then os.replace: no half-written files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_feed(xml: str, path: Path) -> None:
    """Refuse to write XML that does not parse; otherwise write atomically."""
    try:
        ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ValueError(f"generated XML does not parse, nothing written: {exc}") from exc
    atomic_write_text(path, xml)


def local_image_path(url: str, root: Path = REPO) -> Path | None:
    """Map a published image URL to its file in this repo (None if hosted elsewhere)."""
    if url.startswith(RAW_PREFIX):
        return root / url[len(RAW_PREFIX):]
    return None


def published(listings: list[dict]) -> list[dict]:
    return [l for l in listings if l.get("publish") is True]


def feed_to_catalog(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    out = []
    for it in root.findall("list-item"):
        row: dict = {}
        for child in it:
            if child.tag == "images":
                row["images"] = [(i.text or "") for i in child.findall("list-item")]
            elif child.tag == "attrs":
                row["attrs"] = {a.tag: (a.text or "") for a in child}
            else:
                row[child.tag] = child.text or ""
        unknown = set(row) - set(FIELDS)
        if unknown:
            raise ValueError(f"{row.get('external_id')}: unsupported fields {sorted(unknown)}")
        out.append(row)
    return out


def catalog_to_feed(listings: list[dict]) -> str:
    """Write the given listings (already filtered) as a Bazaraki XML feed."""
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<root>"]
    for row in listings:
        lines.append("  <list-item>")
        for f in FIELDS:
            if f not in row:
                continue
            v = row[f]
            if f == "images":
                lines.append("    <images>")
                lines += [f"      <list-item>{escape(u)}</list-item>" for u in v]
                lines.append("    </images>")
            elif f == "attrs":
                lines.append("    <attrs>")
                lines += [f"      <{k}>{escape(x, ENTITIES)}</{k}>" for k, x in v.items()]
                lines.append("    </attrs>")
            else:
                lines.append(f"    <{f}>{escape(v, ENTITIES)}</{f}>")
        lines.append("  </list-item>")
    lines.append("</root>")
    return "\n".join(lines) + "\n"


def load_catalog(path: Path = CATALOG) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_catalog(listings: list[dict], path: Path = CATALOG) -> None:
    atomic_write_text(path, json.dumps(listings, indent=2, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["build", "check"])
    a = p.parse_args(argv)
    listings = published(load_catalog())
    xml = catalog_to_feed(listings)
    if a.command == "check":
        if not FEED.is_file() or FEED.read_text(encoding="utf-8") != xml:
            print(f"{FEED.relative_to(REPO).as_posix()} is out of date: run python -m bazaraki_agent.feed build")
            return 1
        print("feed is up to date")
        return 0
    write_feed(xml, FEED)
    print(f"wrote {FEED.relative_to(REPO).as_posix()} ({len(listings)} published listings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
