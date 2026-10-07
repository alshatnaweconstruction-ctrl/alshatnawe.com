"""Bazaraki's official reference data: category IDs, location IDs, title stop words.

Source: bazaraki_agent/data/bazaraki_official_list.txt, a verbatim copy of the
list published at https://www.bazaraki.com/business-xml-guide/ (saved by the
owner on 2026-10-02). Nothing here is guessed: if an ID is not in that file,
validate.py rejects it.

    python -m bazaraki_agent.official        # print a summary
"""

from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "data" / "bazaraki_official_list.txt"

_CATEGORY = re.compile(r"^(?P<name>[^|]*\S)\s+(?P<id>\d+)$")
_LOCATION = re.compile(r"^(?P<id>\d+)\s*\|\s*(?P<name>.+)$")


@lru_cache(maxsize=None)
def load(path: Path = SOURCE) -> dict:
    """Parse the official list into {"stopwords", "rubrics", "districts"}."""
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()]
    stopwords: list[str] = []
    rubrics: dict[str, str] = {}
    districts: dict[str, str] = {}
    for i, line in enumerate(lines):
        if not line:
            continue
        if line.lower().startswith("stop words for title"):
            stopwords = [w.strip() for w in lines[i + 1].split(",") if w.strip()]
            continue
        m = _LOCATION.match(line)
        if m:
            districts[m["id"]] = m["name"].strip()
            continue
        m = _CATEGORY.match(line)
        if m and ("/" in m["name"] or m["name"] in {"Services", "Other"}):
            rubrics[m["id"]] = m["name"].strip()
    if not stopwords or not rubrics or not districts:
        raise ValueError(f"{path}: could not parse the official list")
    return {"stopwords": stopwords, "rubrics": rubrics, "districts": districts}


def main() -> int:
    d = load()
    print(f"{len(d['rubrics'])} categories, {len(d['districts'])} locations, "
          f"{len(d['stopwords'])} title stop words")
    for rid, name in sorted(d["rubrics"].items(), key=lambda x: x[1]):
        if name.startswith("Services / Property, maintenance"):
            print(f"  {rid:>5}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
