"""Pre-publish gate for the Bazaraki catalog.

Every change to bazaraki_agent/catalog.json must pass this before the feed is
rebuilt and pushed. ERRORs block publishing; WARNINGs are reported only.

Listings with "publish": true get every rule. Drafts ("publish": false) only get
format checks, and anything still missing is reported as a WARNING so you can
see what each draft needs before it can go live.

Sources of the rules:
  - Bazaraki official XML spec + list (bazaraki_agent/data/bazaraki_official_list.txt)
  - Owner requirements (2 Oct 2026): one ad per service, >= 5 photos with a
    recorded source, approved prices only, Greek + English, no invented claims

    python -m bazaraki_agent.validate
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from bazaraki_agent.audit import shingles
from bazaraki_agent.feed import CATALOG, REPO, load_catalog, local_image_path
from bazaraki_agent.official import load as load_official

BUSINESS_LINE = "+35795553931"  # src/data/company.ts: the only public number
REQUIRED = ["last_update", "external_id", "status", "rubric", "district", "title",
            "description", "price", "chosen_phone", "images"]
# Official spec also has active_b2b, but that is for real-estate B2B: not allowed for service ads.
STATUSES = {"active", "archive", "remove"}
MAX_TITLE = 70          # official spec: 70 chars
MAX_DESCRIPTION = 10000  # official spec
MIN_IMAGES = 5          # owner requirement
MAX_IMAGES = 16         # official spec (24 only on Business Premium)
MAX_AI_IMAGES = 2       # owner decision D-004: at most 2 AI images per ad (the "never the cover" rule was lifted by D-084, D-111)
MAX_AI_IMAGES_BY_SERVICE = {"bathroom": 5, "repairs": 5, "remote-owner": 5}  # owner decision D-124: all-AI ads
NEAR_DUPLICATE = 0.5    # same threshold audit.py reports on
TITLE_EXTRA_CHARS = set(" ,.-'")  # spec: "text and digits only"
AI_SOURCES = {"ai_nano_banana_pro", "ai_meta_ai"}  # ai_meta_ai: D-100 (Gemini blocked on the Workspace account)
PHOTO_SOURCES = {"own", "stock"} | AI_SOURCES
STOCK_LICENCES = {"unsplash", "pexels"}  # licences that allow commercial use
# Manifest v2: rights_status must agree with source; "unverified" can never go live.
RIGHTS_FOR_SOURCE = {"own": "owned", "stock": "licensed", "ai_nano_banana_pro": "generated", "ai_meta_ai": "generated"}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")  # official spec: JPG, PNG
IMAGE_SIGNATURES = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A number next to a currency word/sign in a title (official: no price in the title).
PRICE_IN_TITLE = re.compile(r"(?:€|\beur\b|\beuros?\b|ευρω)\s*\d|\d+(?:[.,]\d+)?\s*(?:€|eur\b|euros?\b|ευρω)", re.IGNORECASE)

# Claims that need evidence on file before they may appear in an ad.
# Matched against accent-folded text (see fold), so patterns carry no accents.
UNSUBSTANTIATED = [r"\bbest\b", r"\bcheapest\b", r"\b#1\b", r"\bnumber one\b",
                   r"\bguarantee(d)?\b", r"\bwarranty\b", r"\bfree\b", r"\bcertified\b",
                   r"\blicensed\b", r"\binsured\b", r"\b24/7\b", r"\bspecialists?\b",
                   r"\bexperts?\b", r"\b\d+\+? years?\b",
                   r"εγγυηση", r"δωρεαν", r"φθηνοτερ", r"\b\d+\+? χρονια",
                   # article + καλύτερ- is the superlative ("the best"); bare καλύτερη is "better"
                   r"\b(?:ο|η|οι|το|τον|την|τα|τους|τις)\s+καλυτερ"]
PHONE = re.compile(r"(?:\+?357[\s-]?)?\b(?:9\d|2\d)\s?\d{2}\s?\d{2}\s?\d{2}\b")
LINK = re.compile(r"https?://|www\.|\S+@\S+\.\w+")
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
GREEK = re.compile("[Ͱ-Ͽἀ-῿]")  # Greek and Coptic + Greek Extended
LATIN = re.compile(r"[A-Za-z]")
ARABIC = re.compile("[؀-ۿݐ-ݿﭐ-﷿ﹰ-ﻼ]")  # Arabic blocks, no BOM

RATES = REPO / "bazaraki_agent/data/rates.json"
MANIFEST = REPO / "photos/manifest.csv"
LEDGER = REPO / "bazaraki_agent/data/published_ids.json"   # every external_id ever made live
DENYLIST = REPO / "photos/denylist.txt"                    # sha256 of images that may never be used


def fold(text: str) -> str:
    """Strip accents so ΚΑΛΥΤΕΡΗ, καλύτερη and καλυτερη all match one pattern."""
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def load_rates(path: Path = RATES) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def load_manifest(path: Path = MANIFEST) -> dict[str, dict]:
    """photos/manifest.csv rows keyed by repo-relative file path."""
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {r["file"].strip(): r for r in csv.DictReader(f)}


def load_ledger(path: Path = LEDGER) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []


def load_denylist(path: Path = DENYLIST) -> dict[str, str]:
    """Lines: '<sha256>  <reason>  [path]'; '#' starts a comment."""
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("#", 1)[0].split()
        if len(parts) >= 2 and re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            out[parts[0]] = parts[1]
    return out


def doubled_words(title: str) -> list[str]:
    words = re.findall(r"\w+", fold(title).lower())
    return sorted({a for a, b in zip(words, words[1:]) if a == b})


def stopword_hits(title: str, stopwords: list[str]) -> list[str]:
    t = fold(title).lower()
    return [w for w in stopwords if re.search(rf"(?<!\w){re.escape(fold(w).lower())}(?!\w)", t)]


def validate(listings: list[dict], root: Path = REPO, rates: dict | None = None,
             manifest: dict | None = None, official: dict | None = None,
             ledger: list[dict] | None = None,
             denylist: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    rates = load_rates() if rates is None else rates
    manifest = load_manifest() if manifest is None else manifest
    on_hold = {r.get("checksum_sha256", "").strip().lower() for r in manifest.values()
               if r.get("approved", "").strip().lower() == "on_hold"} - {""}
    official = load_official() if official is None else official
    ledger = load_ledger() if ledger is None else ledger
    denylist = load_denylist() if denylist is None else denylist
    errors: list[str] = []
    warnings: list[str] = []

    # --- published-ID ledger: a live external_id may never silently disappear ------
    # (official spec: an external_id missing from the feed is DELETED on Bazaraki)
    by_id = {l.get("external_id"): l for l in listings}
    for entry in ledger:
        eid = entry.get("external_id")
        if entry.get("status", "live") != "live":
            continue
        l = by_id.get(eid)
        if l is None:
            errors.append(f"{eid}: was published (published_ids.json) but is missing from the catalog; "
                          "dropping it deletes the live ad. Keep it, or set status archive/remove explicitly")
            continue
        if l.get("service_key") != entry.get("service_key"):
            errors.append(f"{eid}: service_key changed for a published external_id "
                          f"({entry.get('service_key')!r} -> {l.get('service_key')!r})")
        if l.get("publish") is not True and l.get("status") != "remove":
            errors.append(f"{eid}: was published and cannot become a draft (publish:false drops it from the feed "
                          "and deletes the ad). Use status archive or remove")

    ids = Counter(l.get("external_id") for l in listings)
    keys = Counter(l.get("service_key") for l in listings if l.get("status") != "remove")
    titles = Counter(l.get("title", "").strip().lower() for l in listings)
    live = [l for l in listings if l.get("publish") is True and l.get("status") in ("active", "active_b2b")]
    live_ids = {id(l) for l in live}
    hash_owner: dict[str, str] = {}

    for l in listings:
        lid = l.get("external_id", "?")
        is_live = id(l) in live_ids
        e = lambda msg: errors.append(f"{lid}: {msg}")
        w = lambda msg: warnings.append(f"{lid}: {msg}")
        need = e if is_live else (lambda msg: w(f"draft needs: {msg}"))

        # --- identity and one-ad-per-service -------------------------------------
        if not l.get("service_key"):
            e("missing service_key (one ad per service needs a key)")
        elif keys[l["service_key"]] > 1:
            e(f"service_key {l['service_key']!r} used by more than one ad (duplicate ad)")
        if ids[lid] > 1:
            e("duplicate external_id")
        if "publish" not in l or not isinstance(l["publish"], bool):
            e("publish must be true or false")

        # --- required fields and official values ---------------------------------
        for f in REQUIRED:
            if f not in l or l[f] in ("", []):
                need(f"missing {f}")
        if l.get("status") not in STATUSES:
            e(f"status {l.get('status')!r} not in {sorted(STATUSES)}")
        if l.get("last_update") and not STAMP.match(l["last_update"]):
            e("last_update must be 'YYYY-MM-DD HH:MM:SS'")
        if l.get("rubric") and str(l["rubric"]) not in official["rubrics"]:
            e(f"rubric {l['rubric']} is not an official Bazaraki category ID")
        if l.get("district") and str(l["district"]) not in official["districts"]:
            e(f"district {l['district']} is not an official Bazaraki location ID")

        if l.get("status") == "remove":
            continue  # a removal only needs its identity

        # --- title -----------------------------------------------------------------
        title = l.get("title", "")
        if len(title) > MAX_TITLE:
            e(f"title {len(title)} chars > {MAX_TITLE}")
        if title and titles[title.strip().lower()] > 1:
            e("duplicate title")
        if title.isupper() or "!!" in title:
            e("title shouting (all caps or '!!')")
        bad = sorted({c for c in title if not (c.isalpha() or c in "0123456789" or c in TITLE_EXTRA_CHARS)})
        if bad:
            e(f"title has characters Bazaraki does not allow (text and digits only): {''.join(bad)!r}")
        for word in stopword_hits(title, official["stopwords"]):
            e(f"title contains Bazaraki stop word {word!r}")
        for word in doubled_words(title):
            e(f"title has a doubled word {word!r} (official: replace doubled words)")
        if PRICE_IN_TITLE.search(fold(title)):
            e("price in title (official: do not put the price into the title)")

        # --- description -----------------------------------------------------------
        desc = l.get("description", "")
        if len(desc) > MAX_DESCRIPTION:
            e(f"description {len(desc)} chars > {MAX_DESCRIPTION}")
        if ARABIC.search(title + desc):
            e("Arabic text: Bazaraki ads must be Greek and English only")
        if desc and not (GREEK.search(desc) and LATIN.search(desc)):
            need("description in both Greek and English")
        if desc and GREEK.search(desc) and LATIN.search(desc):
            first = next((c for c in desc if c.isalpha()), "")
            if not GREEK.match(first):
                w("description should start with the Greek text")
        if "bazaraki" in desc.lower():
            e("description mentions Bazaraki (not allowed in ad text)")
        text = fold(f"{title}\n{desc}")
        for pat in UNSUBSTANTIATED:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                e(f"unsubstantiated claim {m.group(0)!r}: add evidence to docs/claims.md and remove it from this list, or reword")
        if LINK.search(desc):
            e("link or email in description (use the Bazaraki contact buttons)")
        for m in PHONE.finditer(desc):
            if re.sub(r"\D", "", m.group(0))[-8:] != BUSINESS_LINE[-8:]:
                e(f"non-business phone number in description: {m.group(0)!r}")
        for f in ("chosen_phone", "whatsapp"):
            if l.get(f) and l[f] != BUSINESS_LINE:
                e(f"{f} {l[f]} is not the business line {BUSINESS_LINE}")
        if (l.get("attrs") or {}).get("language") != "10,20":
            need("attrs.language must be '10,20' (Greek + English)")

        # --- price: only owner-approved -------------------------------------------
        try:
            price = float(l.get("price", ""))
        except ValueError:
            e(f"price {l.get('price')!r} is not a number")
            price = None
        rate = rates.get(l.get("service_key", ""), {})
        if price is not None and price <= 0:
            need("price must be above 0.00")
        if not rate.get("approved_by"):
            need("price not approved yet (bazaraki_agent/data/rates.json: approved_by)")
        elif price is not None and abs(float(rate.get("approved_price", -1)) - price) > 0.001:
            e(f"price {price:.2f} differs from approved price {rate.get('approved_price')}")

        # --- photos -----------------------------------------------------------------
        imgs = l.get("images", [])
        if len(imgs) < MIN_IMAGES:
            need(f"{len(imgs)} photos < {MIN_IMAGES}")
        if len(imgs) > MAX_IMAGES:
            e(f"{len(imgs)} photos > {MAX_IMAGES}")
        if len(set(imgs)) != len(imgs):
            e("same photo URL listed twice")
        ai = 0
        for n, url in enumerate(imgs):
            path = local_image_path(url, root)
            if path is None:
                e(f"photo not hosted in this repo: {url}")
                continue
            rel = path.relative_to(root).as_posix()
            if not rel.lower().endswith(IMAGE_EXTENSIONS):
                e(f"{rel}: image must be JPG or PNG (official spec)")
                continue
            if not path.is_file():
                e(f"photo file missing: {rel}")
                continue
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if not data.startswith(IMAGE_SIGNATURES):
                e(f"{rel}: not a real JPG/PNG file (file signature)")
            if digest in denylist:
                e(f"{rel}: image is on the deny-list ({denylist[digest]}) and may never be used")
            if digest in on_hold:
                e(f"{rel}: photo is on hold in photos/manifest.csv (owner decision) and may not be used")
            row = manifest.get(rel)
            if row is None:
                e(f"photo not recorded in photos/manifest.csv: {rel}")
                continue
            src = row.get("source", "").strip()
            if src not in PHOTO_SOURCES:
                e(f"{rel}: source {src!r} not in {sorted(PHOTO_SOURCES)}")
            rights = row.get("rights_status", "").strip()
            if rights not in RIGHTS_FOR_SOURCE.values():
                need(f"{rel}: rights_status {rights!r} cannot be used (needs owned/licensed/generated)")
            elif src in RIGHTS_FOR_SOURCE and RIGHTS_FOR_SOURCE[src] != rights:
                e(f"{rel}: rights_status {rights!r} does not match source {src!r}")
            if not row.get("relevance_reason", "").strip():
                need(f"{rel}: relevance_reason missing (why this photo fits this ad)")
            if not ISO_DATE.match(row.get("capture_date", "").strip()):
                need(f"{rel}: capture_date must be YYYY-MM-DD (capture or download date)")
            if row.get("checksum_sha256", "").strip().lower() != digest:
                e(f"{rel}: checksum does not match the file (re-record it; a changed photo needs a new file name)")
            if row.get("approved", "").strip().lower() == "yes" and not (
                    row.get("approved_by", "").strip() and ISO_DATE.match(row.get("approved_date", "").strip())):
                e(f"{rel}: approved=yes needs approved_by and approved_date")
            if src == "stock" and (row.get("licence", "").strip().lower() not in STOCK_LICENCES
                                   or not row.get("source_url", "").startswith("https://")):
                e(f"{rel}: stock photo needs licence unsplash/pexels and its source_url")
            if src in AI_SOURCES:             # illustrative only; any role incl. the cover (D-084)
                ai += 1
            if row.get("service_key", "").strip() != l.get("service_key"):
                e(f"{rel}: recorded for service {row.get('service_key')!r}, not this ad")
            if row.get("approved", "").strip().lower() != "yes":
                need(f"{rel}: photo not approved by the owner (manifest approved=yes)")
            if is_live:
                other = hash_owner.setdefault(digest, lid)
                if other != lid:
                    e(f"{rel}: same photo file already used by {other}")
        ai_cap = MAX_AI_IMAGES_BY_SERVICE.get(l.get("service_key"), MAX_AI_IMAGES)
        if ai > ai_cap:
            e(f"{ai} AI photos > {ai_cap}")

    # --- near-duplicate descriptions between live ads ---------------------------------
    sh = {l["external_id"]: shingles(l.get("description", "")) for l in live}
    order = list(sh)
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            union = sh[a] | sh[b]
            if union and len(sh[a] & sh[b]) / len(union) >= NEAR_DUPLICATE:
                errors.append(f"{a}: description near-duplicate of {b} (moderators decline duplicates)")
    return errors, warnings


def main() -> int:
    listings = load_catalog()
    errors, warnings = validate(listings)
    for msg in warnings:
        print(f"WARNING {msg}")
    for msg in errors:
        print(f"ERROR   {msg}")
    live = sum(1 for l in listings if l.get("publish") is True)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s) in {CATALOG.relative_to(REPO)} "
          f"({live} published, {len(listings) - live} draft)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
