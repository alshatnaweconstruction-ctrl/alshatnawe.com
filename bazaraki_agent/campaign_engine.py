"""Campaign engine: planning and uniqueness gates for campaign-level ad variants.

PLANNING ONLY. This module checks and plans variants; it has no capability to build feeds,
publish, push or contact any website. Variants are always publish:false here.

Uniqueness limit between any two ads: 0.40 (titles, descriptions, service scope).
Images: own / Unsplash / Pexels only; 5 unique per ad; no reuse or near-duplicates.

    python -m bazaraki_agent.campaign_engine          # check the campaign catalog
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import imagehash

from bazaraki_agent.ad_engine import SMALL, _title_problems, _words
from bazaraki_agent.official import load as load_official
from bazaraki_agent.validate import REPO, UNSUBSTANTIATED, fold, load_rates, shingles

CATALOG = REPO.parent / "master_plan" / "campaigns" / "CAMPAIGN_CATALOG.json"
MAX_SIMILARITY = 0.40
PHASH_NEAR = 10
MIN_IMAGES = 5
ALLOWED_SOURCES = {"own", "unsplash", "pexels"}
ALLOWED_DOMAINS = {"unsplash.com", "www.unsplash.com", "images.unsplash.com", "pexels.com", "www.pexels.com", "images.pexels.com"}
FORBIDDEN_DOMAINS = ("pinterest", "pinimg", "google", "gstatic", "bazaraki", "facebook", "fbcdn", "instagram", "cdninstagram")


def load_catalog(path: Path = CATALOG) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def _title_words(t):
    return [w for w in _words(t) if w not in SMALL]


def _norm(s):
    return re.sub(r"\s+", " ", fold(s or "").lower()).strip()


# ---------------------------------------------------------------- single variant
def check_variant(v: dict, official: dict, rates: dict, extra_prohibited: list[str] | None = None) -> list[str]:
    e = []
    e += [f"title: {x}" for x in _title_problems(v["title_en"], official, "EN")]
    e += [f"title: {x}" for x in _title_problems(v["title_el"], official, "EL", min_len=20)]
    if str(v.get("rubric")) not in official["rubrics"]:
        e.append(f"rubric {v.get('rubric')} is not an official category")
    text = fold(" ".join([v.get("title_en", ""), v.get("title_el", ""), v.get("description_en", ""), v.get("description_el", "")]))
    for pat in UNSUBSTANTIATED + list(extra_prohibited or []):
        m = re.search(pat, text, re.I)
        if m:
            e.append(f"prohibited claim {m.group(0)!r}")
    if v.get("price_status") == "approved":
        r = rates.get(v.get("rates_key") or "", {})
        if not r.get("approved_by"):
            e.append(f"price_status approved but no approved rate for {v.get('rates_key')!r}")
    imgs = v.get("images", [])
    for im in imgs:
        host = (urlparse(im.get("source_url", "")).hostname or "").lower()
        if any(b in host for b in FORBIDDEN_DOMAINS):
            e.append(f"forbidden image source {host} ({im.get('file')})")
        if im.get("source") not in ALLOWED_SOURCES:
            e.append(f"image source {im.get('source')!r} not allowed (own / unsplash / pexels only)")
        elif im.get("source") != "own" and host not in ALLOWED_DOMAINS:
            e.append(f"stock image must link to its Unsplash/Pexels page, got {host!r}")
    if len({im.get("checksum_sha256") for im in imgs}) < MIN_IMAGES:
        e.append(f"needs {MIN_IMAGES} unique images, has {len({im.get('checksum_sha256') for im in imgs})}")
    for a, b in itertools.combinations(imgs, 2):
        if a.get("phash") and b.get("phash") and imagehash.hex_to_hash(a["phash"]) - imagehash.hex_to_hash(b["phash"]) <= PHASH_NEAR:
            e.append(f"near-duplicate image within the ad: {a.get('file')} / {b.get('file')}")
    if v.get("publish") is not False:
        e.append("variants are planning items: publish must be false")
    return e


def readiness(v: dict, rates: dict) -> str:
    if v.get("price_status") != "approved" or not rates.get(v.get("rates_key") or "", {}).get("approved_by"):
        return "needs_price"
    if len({im.get("checksum_sha256") for im in v.get("images", [])}) < MIN_IMAGES:
        return "needs_images"
    return "ready_for_generation"


# ---------------------------------------------------------------- between variants
def uniqueness(variants: list[dict], limit: float = MAX_SIMILARITY) -> list[str]:
    errs, seen_img = [], {}
    for v in variants:
        for im in v.get("images", []):
            k = im.get("checksum_sha256")
            if k in seen_img and seen_img[k] != v["variant_key"]:
                errs.append(f"image reused: {im.get('file')} in {seen_img[k]} and {v['variant_key']}")
            seen_img.setdefault(k, v["variant_key"])
    for a, b in itertools.combinations(variants, 2):
        pair = f"{a['variant_key']} vs {b['variant_key']}"
        if a.get("primary_scope") == b.get("primary_scope"):
            errs.append(f"{pair}: same primary_scope {a.get('primary_scope')!r}")
        sj = _jac([_norm(x) for x in a.get("scope_tags", [])], [_norm(x) for x in b.get("scope_tags", [])])
        if sj > limit:
            errs.append(f"{pair}: service-scope overlap {sj:.2f} > {limit}")
        tj = _jac(_title_words(a["title_en"]), _title_words(b["title_en"]))
        if tj > limit:
            errs.append(f"{pair}: title similarity {tj:.2f} > {limit}")
        if _norm(a.get("customer_problem")) and _norm(a.get("customer_problem")) == _norm(b.get("customer_problem")):
            errs.append(f"{pair}: same customer_problem")
        for lang in ("en", "el"):
            da, db = a.get(f"description_{lang}", ""), b.get(f"description_{lang}", "")
            if da and db:
                dj = _jac(shingles(da), shingles(db))
                if dj > limit:
                    errs.append(f"{pair}: description ({lang}) similarity {dj:.2f} > {limit}")
        for ia in a.get("images", []):
            for ib in b.get("images", []):
                if ia.get("checksum_sha256") != ib.get("checksum_sha256") and ia.get("phash") and ib.get("phash") and \
                        imagehash.hex_to_hash(ia["phash"]) - imagehash.hex_to_hash(ib["phash"]) <= PHASH_NEAR:
                    errs.append(f"{pair}: near-duplicate image {ia.get('file')} / {ib.get('file')}")
    return errs


def plan_uniqueness(variants: list[dict]) -> list[str]:
    """Planning stage (no images or full text yet): scope, problem and title gates only."""
    return uniqueness([{k: v for k, v in x.items() if k not in ("images", "description_en", "description_el")} for x in variants])


def main() -> int:
    cat, official, rates = load_catalog(), load_official(), load_rates()
    bad = 0
    for c in cat["campaigns"]:
        vs = c.get("variants", [])
        errs = plan_uniqueness(vs) if vs else []
        titles = [x for v in vs for x in _title_problems(v["title_en"], official, "EN") + _title_problems(v["title_el"], official, "EL", 20)]
        bad += len(errs) + len(titles)
        print(f"{c['campaign_key']:22} rubric {c['rubric']:>5} planned {c['planned_variants']:>3} detailed {len(vs):>2} "
              f"uniqueness {len(errs)} title {len(titles)} | {c['approval_status']}")
        for x in errs + titles:
            print("   ", x)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
