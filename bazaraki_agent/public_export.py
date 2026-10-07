"""Public export (owner decision D-129): the parts of the local data that may go into the PUBLIC repo.

The GitHub repository is public. This module builds, under build/public/:

- rates.json                  owner-approved prices with their public market sources, WITHOUT internal fields
                              (internal_evidence: signed contract rates, costs, project references)
- PUBLIC_PHOTO_MANIFEST.csv   one row per photo used by the live feed: file, service, source type, licence,
                              public source URL (stock only), sha256, size. No project refs, paths or notes.

Every output is scanned for leaks (project codes, local paths, own:// references, internal field names and the
private terms listed in data/private_terms.txt, which is local and git-ignored); any hit stops the export.
It never writes the live bazaraki.xml, photos/manifest.csv, catalog.json or data/rates.json.

    python -m bazaraki_agent.public_export [--feed <bazaraki.xml>]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

from bazaraki_agent.feed import LIVE_FEED, RAW_PREFIX
from bazaraki_agent.validate import REPO, load_manifest, load_rates

OUT = REPO / "build" / "public"
PRIVATE_TERMS = REPO / "bazaraki_agent" / "data" / "private_terms.txt"
INTERNAL_RATE_FIELDS = {"internal_evidence"}
PHOTO_FIELDS = ("file", "service_key", "source_type", "licence", "source_url", "checksum_sha256", "width", "height")
SOURCE_TYPE = {"own": "own photo", "stock": "stock photo", "ai_meta_ai": "AI illustration (Meta AI)",
               "ai_nano_banana_pro": "AI illustration (Nano Banana Pro)"}
LEAK_PATTERNS = [r"\b(?:ASC|VSC|CLI|INQ)-\d+", r"own://", r"\b[A-Za-z]:[\\/]", r"Organized_Files", r"photos-inbox",
                 r"internal_evidence", r"proposed_margin", r"\bmargin_pct\b"]


def private_terms(path: Path = PRIVATE_TERMS) -> list[str]:
    if not path.is_file():
        return []
    return [t.strip() for t in path.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")]


def leaks(text: str, terms=()) -> list[str]:
    hits = [p for p in LEAK_PATTERNS if re.search(p, text)]
    hits += [f"private term #{i + 1}" for i, t in enumerate(terms) if t.lower() in text.lower()]
    return hits


def _public_rate(r: dict) -> dict:
    out = {f: v for f, v in r.items() if f not in INTERNAL_RATE_FIELDS}
    if isinstance(out.get("sources"), list):     # internal working sets are listed as sources too: keep public links only
        out["sources"] = [s for s in out["sources"] if str(s.get("url", "")).startswith("https://")]
    return out


def public_rates(rates: dict) -> dict:
    return {k: (_public_rate(r) if isinstance(r, dict) else r) for k, r in rates.items()}


def feed_photos(xml_text: str) -> list[str]:
    return sorted(set(re.findall(re.escape(RAW_PREFIX) + r"(photos/[^<\s]+)", xml_text)))


def public_manifest(manifest: dict[str, dict], files: list[str]) -> list[dict]:
    rows = []
    for f in files:
        r = manifest.get(f)
        if r is None:
            raise ValueError(f"{f}: used by the feed but not recorded in photos/manifest.csv")
        src = r.get("source", "").strip()
        url = r.get("source_url", "").strip()
        rows.append({"file": f, "service_key": r.get("service_key", ""), "source_type": SOURCE_TYPE.get(src, src),
                     "licence": {"own": "owned", "ai_meta_ai": "generated", "ai_nano_banana_pro": "generated"}.get(src, r.get("licence", "")),
                     "source_url": url if src == "stock" and url.startswith("https://") else "",
                     "checksum_sha256": r.get("checksum_sha256", ""), "width": r.get("width", ""), "height": r.get("height", "")})
    return rows


def render(rates: dict, photos: list[dict]) -> dict[str, str]:
    buf = io.StringIO()
    w = csv.DictWriter(buf, PHOTO_FIELDS, lineterminator="\n")
    w.writeheader(); w.writerows(photos)
    return {"rates.json": json.dumps(public_rates(rates), ensure_ascii=False, indent=2) + "\n",
            "PUBLIC_PHOTO_MANIFEST.csv": buf.getvalue()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--feed", type=Path, default=LIVE_FEED, help="feed whose photos are listed (e.g. a copy of origin/main)")
    a = ap.parse_args(argv)
    files = render(load_rates(), public_manifest(load_manifest(), feed_photos(a.feed.read_text(encoding="utf-8"))))
    terms = private_terms()
    bad = {name: leaks(text, terms) for name, text in files.items()}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        print(f"STOP: possible leaks {bad}; nothing written")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"written {sorted(files)} -> {OUT} ({len(terms)} private terms checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
