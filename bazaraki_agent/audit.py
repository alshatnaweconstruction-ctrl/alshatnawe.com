"""Read-only forensic audit of the Bazaraki XML import feed.

The feed at bazaraki.xml (repo root) is what Bazaraki imports into the
account, so it is the source of truth for every published listing. This tool
never touches the Bazaraki account: it parses the feed, checks the images on
disk, and writes an inventory plus findings to an output directory.

Scores are transparent rule-based heuristics (see score_listing), not
performance data. Bazaraki views/enquiries are not available to this tool and
are reported as UNKNOWN rather than estimated.

Usage:
    python3 -m bazaraki_agent.audit [--feed PATH] [--public-dir DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlparse

try:  # Pillow is optional; without it image dimensions are UNKNOWN.
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

SITE_HOST = "alshatnawe.com"
RAW_PREFIX = "https://raw.githubusercontent.com/alshatnaweconstruction-ctrl/alshatnawe.com/main/"
GREEK = re.compile(r"[Ͱ-Ͽ]")
LOCATIONS = ["paphos", "cyprus", "limassol", "larnaca", "nicosia", "peyia",
             "geroskipou", "chloraka", "kissonerga", "polis", "tala", "emba"]
BRAND_TERMS = ["al shatnawe", "shatnawe", "verteks", "he 495105"]
TRUST_TERMS = ["warranty", "guarantee", "εγγύηση", "years", "χρόνια",
               "experience", "εμπειρία", "insured", "ασφάλιση", "knauf",
               "siniat", "gyproc", "registered", "portfolio"]
MIN_IMAGE_WIDTH = 800


@dataclass
class Listing:
    external_id: str
    status: str
    rubric: str
    district: str
    title: str
    description: str
    price: float | None
    negotiable: bool
    phone: str
    whatsapp: str
    chat_allowed: bool
    languages: str
    last_update: str
    images: list[str] = field(default_factory=list)


@dataclass
class ImageInfo:
    url: str
    path: str
    exists: bool
    md5: str | None = None
    width: int | None = None
    height: int | None = None
    kb: int | None = None


def _text(el: ET.Element, tag: str) -> str:
    return (el.findtext(tag) or "").strip()


def parse_feed(path: Path) -> list[Listing]:
    root = ET.parse(path).getroot()
    out = []
    for it in root.findall("list-item"):
        raw_price = _text(it, "price")
        try:
            price = float(raw_price)
        except ValueError:
            price = None
        out.append(Listing(
            external_id=_text(it, "external_id"),
            status=_text(it, "status"),
            rubric=_text(it, "rubric"),
            district=_text(it, "district"),
            title=_text(it, "title"),
            description=_text(it, "description"),
            price=price,
            negotiable=_text(it, "negotiable_price") == "1",
            phone=_text(it, "chosen_phone"),
            whatsapp=_text(it, "whatsapp"),
            chat_allowed=_text(it, "disallow_chat") != "1",
            languages=_text(it, "attrs/language"),
            last_update=_text(it, "last_update"),
            images=[(i.text or "").strip() for i in it.findall("images/list-item")],
        ))
    return out


def inspect_image(url: str, public_dir: Path) -> ImageInfo:
    parsed = urlparse(url)
    if url.startswith(RAW_PREFIX):  # photos served from this repo on GitHub
        local, hosted_here = public_dir / url[len(RAW_PREFIX):], True
    else:
        local, hosted_here = public_dir / parsed.path.lstrip("/"), parsed.hostname == SITE_HOST
    if not hosted_here or not local.is_file():
        return ImageInfo(url, str(local), False)
    data = local.read_bytes()
    info = ImageInfo(url, str(local), True, hashlib.md5(data).hexdigest(),
                     kb=round(len(data) / 1024))
    if Image is not None:
        try:
            with Image.open(local) as im:
                info.width, info.height = im.size
        except OSError:  # unreadable/corrupt file: dimensions stay UNKNOWN
            pass
    return info


def shingles(text: str, k: int = 5) -> set[str]:
    words = re.findall(r"\w+", text.lower())
    return {" ".join(words[i:i + k]) for i in range(max(len(words) - k + 1, 0))}


def score_listing(l: Listing, imgs: list[ImageInfo], md5_uses: Counter) -> dict:
    """Rule-based 0-100 scores. Each deduction is recorded as a finding."""
    title, desc = l.title, l.description
    tl, dl = title.lower(), desc.lower()
    findings: list[str] = []

    seo = 100
    if not any(loc in tl for loc in LOCATIONS):
        seo -= 25; findings.append("title has no location keyword")
    if not GREEK.search(title):
        seo -= 25; findings.append("title is English-only (no Greek search terms)")
    if len(title) > 65:
        seo -= 10; findings.append(f"title long ({len(title)} chars), may truncate on mobile")

    copy = 100
    if len(desc) < 600:
        copy -= 30; findings.append("description short")
    if not GREEK.search(desc):
        copy -= 30; findings.append("description has no Greek")
    if "enquiry" not in dl and "message" not in dl and "μήνυμα" not in dl:
        copy -= 15; findings.append("no clear call to action")

    trust = 100
    if not any(b in dl for b in BRAND_TERMS):
        trust -= 40; findings.append("no company/brand name in description")
    if not any(t in dl for t in TRUST_TERMS):
        trust -= 40; findings.append("no trust signals (experience, warranty, materials brand, registration)")

    price = 100
    if not l.price:
        price -= 60; findings.append("price is 0.00 (no price anchor, 'from' price or rate)")

    unique = [i for i in imgs if i.exists and md5_uses[i.md5] == 1]
    cover = imgs[0] if imgs else None
    visual = 100
    missing = [i for i in imgs if not i.exists]
    if missing:
        visual -= 40; findings.append(f"{len(missing)} image(s) missing on disk")
    if cover and cover.exists and md5_uses[cover.md5] > 1:
        visual -= 30; findings.append("cover image (01) is reused in other listings")
    if len(unique) == 0:
        visual -= 30; findings.append("no image unique to this listing")
    elif len(unique) < 3:
        visual -= 10; findings.append(f"only {len(unique)} unique image(s)")
    small = [i for i in imgs if i.width and i.width < MIN_IMAGE_WIDTH]
    if small:
        visual -= 10; findings.append(f"{len(small)} image(s) under {MIN_IMAGE_WIDTH}px wide")

    scores = {"seo": seo, "copy": copy, "trust": trust, "pricing": price,
              "visual": max(visual, 0)}
    overall = round(sum(scores.values()) / len(scores))
    if overall < 50:
        priority, action = "P1", "rewrite title/trust block + replace reused photos"
    elif overall < 70:
        priority, action = "P2", "add trust block + Greek title variant"
    else:
        priority, action = "P3", "monitor"
    return {**scores, "overall": overall, "priority": priority,
            "unique_images": len(unique), "cover_reused": bool(cover and cover.exists and md5_uses[cover.md5] > 1),
            "recommended_action": action, "findings": findings}


def run(feed: Path, public_dir: Path, out: Path) -> dict:
    listings = parse_feed(feed)
    images = {l.external_id: [inspect_image(u, public_dir) for u in l.images] for l in listings}
    md5_uses = Counter(i.md5 for imgs in images.values() for i in imgs if i.md5)
    md5_where = defaultdict(list)
    for lid, imgs in images.items():
        for n, i in enumerate(imgs, 1):
            if i.md5:
                md5_where[i.md5].append(f"{lid}#{n:02d}")

    rows = []
    for l in listings:
        s = score_listing(l, images[l.external_id], md5_uses)
        rows.append({"external_id": l.external_id, "status": l.status, "rubric": l.rubric,
                     "district": l.district, "title": l.title, "title_len": len(l.title),
                     "desc_len": len(l.description), "price": l.price,
                     "image_count": len(l.images), **{k: v for k, v in s.items() if k != "findings"},
                     "views": "UNKNOWN", "enquiries": "UNKNOWN",
                     "findings": "; ".join(s["findings"])})

    sh = {l.external_id: shingles(l.description) for l in listings}
    ids = list(sh)
    near_dupes = []
    for a_i, a in enumerate(ids):
        for b in ids[a_i + 1:]:
            union = sh[a] | sh[b]
            j = len(sh[a] & sh[b]) / len(union) if union else 0
            if j >= 0.5:
                near_dupes.append({"a": a, "b": b, "jaccard": round(j, 3)})

    all_imgs = [i for imgs in images.values() for i in imgs]
    summary = {
        "feed": feed.name,
        "listings": len(listings),
        "status": dict(Counter(l.status for l in listings)),
        "rubrics": dict(Counter(l.rubric for l in listings)),
        "districts": dict(Counter(l.district for l in listings)),
        "priced_zero": sum(1 for l in listings if not l.price),
        "phones": dict(Counter(l.phone for l in listings)),
        "image_slots": len(all_imgs),
        "images_missing": sum(1 for i in all_imgs if not i.exists),
        "unique_image_files": len(md5_uses),
        "reused_image_files": sum(1 for c in md5_uses.values() if c > 1),
        "covers_reused": sum(1 for r in rows if r["cover_reused"]),
        "listings_without_unique_image": sum(1 for r in rows if r["unique_images"] == 0),
        "images_under_min_width": sum(1 for i in all_imgs if i.width and i.width < MIN_IMAGE_WIDTH),
        "titles_with_greek": sum(1 for l in listings if GREEK.search(l.title)),
        "descriptions_with_brand": sum(1 for l in listings if any(b in l.description.lower() for b in BRAND_TERMS)),
        "description_near_duplicate_pairs": len(near_dupes),
        "priority": dict(Counter(r["priority"] for r in rows)),
        "mean_overall_score": round(sum(r["overall"] for r in rows) / len(rows), 1) if rows else None,
        "performance_data": "UNAVAILABLE (Bazaraki stats not reachable from this environment)",
    }

    out.mkdir(parents=True, exist_ok=True)
    with (out / "listing_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["external_id"])
        w.writeheader(); w.writerows(rows)
    with (out / "image_reuse.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["md5", "uses", "slots"])
        for md5, where in sorted(md5_where.items(), key=lambda kv: -len(kv[1])):
            if len(where) > 1:
                w.writerow([md5, len(where), " ".join(where)])
    (out / "audit_summary.json").write_text(
        json.dumps({"summary": summary, "near_duplicate_descriptions": near_dupes},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--feed", type=Path, default=repo / "bazaraki.xml")
    p.add_argument("--public-dir", type=Path, default=repo)
    p.add_argument("--out", type=Path, default=repo / "docs/audit")
    a = p.parse_args(argv)
    print(json.dumps(run(a.feed, a.public_dir, a.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
