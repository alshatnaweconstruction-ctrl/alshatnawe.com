"""STEP 8: advertisement content engine (Greek first, then English).

Official source first: https://www.bazaraki.com/business-xml-guide/ (saved copy:
official-docs/ + data/bazaraki_official_list.txt; snapshot checked 2026-10-03).
Official rules used here: title text and digits only, max 70 chars, no stop words
(EN + GR list), no doubled words, no price in title; description max 10,000 chars;
0-16 images, JPG/PNG; required attrs per category (language).
Internal rules (NOT from the guide) are marked INTERNAL below.

Reads registry, catalog_proposed.json, photo_manifest_v3.csv, content_blocks.json,
live-ad snapshot. Writes ONLY master_plan/ads/. Never writes catalog.json,
rates.json, manifest.csv or XML, and never publishes.

    python -m bazaraki_agent.ad_engine
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from bazaraki_agent.ad_quality_validator import build_description, gate_status, load_gate, passed
from bazaraki_agent.official import load as load_official
from bazaraki_agent.registry import claims_for_generation, load_registry
from bazaraki_agent.validate import shingles
from bazaraki_agent.validate import (ARABIC, GREEK, LATIN, LINK, MAX_DESCRIPTION, MAX_TITLE, PHONE, PRICE_IN_TITLE,
                                     UNSUBSTANTIATED, fold, stopword_hits)

WS = Path(__file__).resolve().parents[2]
ADS = WS / "master_plan" / "ads"
CONTENT = ADS / "content_blocks.json"
REMEDIATED = WS / "master_plan" / "quality" / "remediated_drafts" / "drafts.json"   # STEP 13.1 review-only drafts
CATALOG_PROPOSED = WS / "master_plan" / "catalog_system" / "catalog_proposed.json"
PHOTO_V3 = WS / "master_plan" / "photo_system" / "photo_manifest_v3.csv"
LIVE_META = WS / "master_plan" / "phase_b" / "live_ads_snapshot_2026-10-03_meta.csv"

MIN_TITLE = 50                      # INTERNAL (official max is 70)
MIN_PHOTOS = 5                      # INTERNAL house rule
MAX_IMAGES = 16                     # official (standard account)
NEAR_DUP_FULL = 0.40                # INTERNAL: full-description shingle similarity limit (validate.py blocks live ads at 0.50)
TITLE_CHARS = set(" ,.-'")          # official: text and digits only (plus basic separators)
OWNER_HOLD: dict = {}   # D-038 (2026-10-03): electrical and light-steel confirmed as offered; drafts until price + photos are approved

# D-057 (STEP 13.1): no company name, legal entity, HE number or office line in any description.
COVERAGE_EL = ("Εξυπηρετούμε όλη την Κύπρο. Η διαθεσιμότητα της υπηρεσίας επιβεβαιώνεται ανάλογα με την τοποθεσία "
               "του ακινήτου και τις απαιτήσεις του έργου.")
COVERAGE_EN = ("We serve all of Cyprus. Service availability is confirmed depending on the property location and "
               "project requirements.")
PROCESS_EL = "Πώς δουλεύουμε: επικοινωνία και φωτογραφίες, αυτοψία όπου χρειάζεται, γραπτή προσφορά με το εύρος εργασιών, εκτέλεση και παράδοση."
PROCESS_EN = "How we work: your message and photos, a site visit where needed, a written quotation with the scope of work, execution and handover."
PHOTO_NOTE_EL = "Οι φωτογραφίες είναι ενδεικτικές και δείχνουν παραδείγματα αυτού του είδους εργασιών."
PHOTO_NOTE_EN = "The photos are illustrative examples of this type of work."
CTA_EL = "Στείλτε μας μήνυμα με την τοποθεσία, φωτογραφίες και μια σύντομη περιγραφή."
CTA_EN = "Send us a message with the location, photos and a short description."
RESEARCH_PRICE_EL = "Τιμή: μετά από αυτοψία και γραπτή προσφορά."
RESEARCH_PRICE_EN = "Price: after a site visit and a written quotation."

CITY_WORDS = {"paphos", "pafos", "limassol", "lemesos", "larnaca", "larnaka", "nicosia", "lefkosia", "famagusta",
              "ammochostos", "παφος", "λεμεσος", "λαρνακα", "λευκωσια", "αμμοχωστος", "ayia", "napa", "protaras",
              "peyia", "pegeia", "polis", "tala", "chloraka", "emba", "geroskipou"}   # INTERNAL: no city copies
STOCK_AS_OWN = [r"\bour (?:completed )?(?:work|works|projects?|jobs?)\b", r"\bcompleted by us\b", r"\bwe (?:completed|built|did) (?:this|these)\b",
                r"τα\s+εργα\s+μας", r"η\s+δουλεια\s+μας", r"(?:εργα|εργασιες)\s+που\s+(?:ολοκληρωσαμε|κανα?με)"]
INTERNAL_WORDS = [r"\bmargin\b", r"\bmark-?up\b", r"\bcost price\b", r"\binternal cost\b", r"περιθωρι", r"κοστος\s+αγορας",
                  r"εσωτερικο\s+κοστος"]
WHATSAPP = re.compile(r"whats\s?app|viber|telegram", re.I)
EURO = re.compile(r"€\s*([\d.,]+)")
SMALL = {"and", "for", "the", "of", "in", "with", "to", "a", "και", "για", "σε", "με", "του", "της", "των", "την", "το"}


# ---------------------------------------------------------------- build
def _has_stock(photos):
    return any(p.get("source") not in ("own",) for p in photos)


def _block(lang, c, price, photos):
    t = c["title_el"] if lang == "el" else c["title_en"]
    s = c[lang]
    head = "Περιλαμβάνει:" if lang == "el" else "Includes:"
    if price.get("approval_status") == "approved":
        pline = ("Τιμή: " if lang == "el" else "Price: ") + price["display_" + lang]
    else:
        pline = RESEARCH_PRICE_EL if lang == "el" else RESEARCH_PRICE_EN
    lines = [t, "", s["intro"]] + ([s["audience"]] if s.get("audience") else []) + ["", head] + [f"- {x}" for x in s["includes"]] + [""] + s.get("notes", []) + ["", pline,
             COVERAGE_EL if lang == "el" else COVERAGE_EN]
    if _has_stock(photos):
        lines += ["", PHOTO_NOTE_EL if lang == "el" else PHOTO_NOTE_EN]
    lines += ["", CTA_EL if lang == "el" else CTA_EN]
    return "\n".join(lines)


def build_ad(key: str, content: dict, price: dict, photos: list[dict]) -> dict:
    use = [p for p in photos if p.get("status") in ("approved", "proposed")][:MAX_IMAGES]
    desc = _block("el", content, price, use) + "\n\nENGLISH\n\n" + _block("en", content, price, use)
    return {"service_key": key, "title_en": content["title_en"], "title_el": content["title_el"], "description": desc,
            "sections": {"el": content["el"], "en": content["en"]}, "price_meta": price, "images": use,
            "photo_counts": {"approved": sum(1 for p in photos if p.get("status") == "approved"),
                             "proposed": sum(1 for p in photos if p.get("status") == "proposed"),
                             "stock": sum(1 for p in use if p.get("source") != "own")},
            "status": None, "problems": []}


def build_ad_v2(key: str, draft: dict, price: dict, photos: list[dict]) -> dict:
    """STEP 13.1: PASTOR layout from master_plan/quality/remediated_drafts/drafts.json (review only)."""
    use = [p for p in photos if p.get("status") in ("approved", "proposed")][:MAX_IMAGES]
    d = dict(draft, price_meta=price if price.get("approval_status") == "approved" else {}, stock_photos=_has_stock(use))
    return {"service_key": key, "title_en": draft["title_en"], "title_el": draft["title_el"], "description": build_description(d),
            "sections": draft["sections"], "fee_scope": draft.get("fee_scope"), "price_meta": price, "images": use,
            "layout": "pastor_v2", "review_only": True,
            "photo_counts": {"approved": sum(1 for p in photos if p.get("status") == "approved"),
                             "proposed": sum(1 for p in photos if p.get("status") == "proposed"),
                             "stock": sum(1 for p in use if p.get("source") != "own")},
            "status": None, "problems": []}


def _load_remediated() -> dict:
    return {d["service_key"]: d for d in json.loads(REMEDIATED.read_text(encoding="utf-8"))["ads"]} if REMEDIATED.is_file() else {}


# ---------------------------------------------------------------- checks
def _words(text):
    return re.findall(r"[^\W\d_]+", fold(text).lower())


def _title_problems(title, official, label, min_len=MIN_TITLE):
    out = []
    if not (min_len <= len(title) <= MAX_TITLE):
        out.append(f"{label} title length {len(title)} (allowed {min_len}-{MAX_TITLE}; official max {MAX_TITLE})")
    bad = sorted({ch for ch in title if not (ch.isalpha() or ch.isdigit() or ch in TITLE_CHARS)})
    if bad:
        out.append(f"{label} title has characters not allowed (official: text and digits only): {''.join(bad)!r}")
    for w in stopword_hits(title, official["stopwords"]):
        out.append(f"{label} title contains official stop word {w!r}")
    if PRICE_IN_TITLE.search(fold(title)) or "€" in title:
        out.append(f"{label} price in title (official rule)")
    ws = [w for w in _words(title) if w not in SMALL]
    rep = sorted({w for w in ws if ws.count(w) > 1})
    if rep:
        out.append(f"{label} title repeated word(s) {rep} (official: no doubled words; INTERNAL: no repeats at all)")
    allw = set(_words(title))
    if allw & CITY_WORDS:
        out.append(f"{label} title names a city {sorted(allw & CITY_WORDS)} (INTERNAL: no per-city copies; use Cyprus)")
    if title.isupper():
        out.append(f"{label} title in capitals")
    return out


def _numbers(sec):
    text = " ".join([sec.get("intro", ""), sec.get("audience", "")] + sec.get("includes", []) + sec.get("notes", []))
    return sorted(re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d.,]*", text))


def parity_problems(el, en):
    out = []
    for k in ("includes", "notes"):
        if len(el.get(k, [])) != len(en.get(k, [])):
            out.append(f"parity: {k} has {len(el.get(k, []))} items in Greek but {len(en.get(k, []))} in English")
    for k in ("intro", "audience"):
        if bool(el.get(k)) != bool(en.get(k)):
            out.append(f"parity: {k} missing in one language")
    if _numbers(el) != _numbers(en):
        out.append(f"parity: numbers differ between Greek {_numbers(el)} and English {_numbers(en)}")
    return out


def check_ad(ad: dict, official: dict, extra_prohibited: list[str] | None = None) -> list[str]:
    errs = []
    errs += _title_problems(ad["title_en"], official, "EN")
    errs += _title_problems(ad["title_el"], official, "EL", min_len=20)
    d = ad["description"]
    if len(d) > MAX_DESCRIPTION:
        errs.append(f"description {len(d)} chars > {MAX_DESCRIPTION} (official)")
    first = next((ch for ch in d if ch.isalpha()), "")
    if not GREEK.match(first):
        errs.append("description must start with Greek (Greek first, then English)")
    if not (GREEK.search(d) and LATIN.search(d)):
        errs.append("description must contain Greek and English")
    if ARABIC.search(d):
        errs.append("Arabic text not allowed")
    if "bazaraki" in d.lower():
        errs.append("description mentions Bazaraki")
    if LINK.search(d) or PHONE.search(d) or WHATSAPP.search(d):
        errs.append("contact details (phone, e-mail, link or messenger) in description")
    text = fold(d)
    for pat in UNSUBSTANTIATED + list(extra_prohibited or []):
        m = re.search(pat if any(c in pat for c in "\\[]()+*?|^$") else re.escape(fold(pat)), text, re.I)
        if m:
            errs.append(f"unsubstantiated or prohibited claim {m.group(0)!r}")
    for pat in INTERNAL_WORDS:
        m = re.search(pat, text, re.I)
        if m:
            errs.append(f"internal cost/margin wording {m.group(0)!r}")
    stock = ad["photo_counts"]["stock"] > 0
    if stock:
        for pat in STOCK_AS_OWN:
            m = re.search(pat, text, re.I)
            if m:
                errs.append(f"stock photos presented as company work: {m.group(0)!r}")
        if PHOTO_NOTE_EL not in d or PHOTO_NOTE_EN not in d:
            errs.append("stock photos used but the illustrative-photo note is missing")
    pm = ad["price_meta"]
    allowed = set()
    if pm.get("approval_status") == "approved":
        allowed = {re.sub(r"[.,]", "", f"{float(pm['price']):.0f}")}
    for amt in EURO.findall(d):
        if re.sub(r"[.,]", "", amt.rstrip(".,")) not in allowed:
            errs.append(f"price €{amt} not from rates.json/price_meta")
    errs += parity_problems(ad["sections"]["el"], ad["sections"]["en"])
    if len(ad["images"]) > MAX_IMAGES:
        errs.append(f"{len(ad['images'])} images > {MAX_IMAGES} (official)")
    return errs


def core_text(sec) -> str:
    """Intro + included items; works for the legacy layout and the STEP 13.1 PASTOR layout."""
    return " ".join([sec.get("intro") or sec.get("solution", "")] + list(sec.get("includes") or sec.get("scope") or []))


def _jac(a, b):
    a, b = set(a) - SMALL, set(b) - SMALL
    return len(a & b) / len(a | b) if a and b else 0.0


def duplicate_problems(ads, live_titles: dict, own_live_ids: dict | None = None) -> list[str]:
    own_live_ids = own_live_ids or {}
    errs, seen = [], {}
    for a in ads:
        if a["service_key"] in seen:
            errs.append(f"{a['service_key']}: two ads for the same service")
        seen[a["service_key"]] = a
    body = lambda a: _words(core_text(a["sections"]["en"]) + " " + core_text(a["sections"]["el"]))
    for i, a in enumerate(ads):
        for b in ads[i + 1:]:
            if a["service_key"] == b["service_key"]:
                continue
            tj, bj = _jac(_words(a["title_en"]), _words(b["title_en"])), _jac(body(a), body(b))
            sa, sb = shingles(a["description"]), shingles(b["description"])
            fj = len(sa & sb) / len(sa | sb) if sa | sb else 0.0
            if tj >= 0.5 or bj >= 0.5 or fj >= NEAR_DUP_FULL:
                errs.append(f"{b['service_key']}: near-duplicate of {a['service_key']} (title {tj:.2f}, text {bj:.2f}, full {fj:.2f})")
        for lid, lt in live_titles.items():
            j = _jac(_words(a["title_en"]), _words(lt))
            if j >= 0.5 and lid not in own_live_ids.get(a["service_key"], []):
                errs.append(f"{a['service_key']}: reject: title similar ({j:.2f}) to live ad {lid} of another service: {lt!r}")
    return errs


def live_conflicts(ad, live_titles, own_ids):
    return [(lid, live_titles.get(lid, ""), round(_jac(_words(ad["title_en"]), _words(live_titles.get(lid, ""))), 2))
            for lid in own_ids]


def build_variant(key: str, content: dict, hosp: dict, price: dict, photos: list[dict], svc_hosp: dict) -> dict:
    """Hospitality variant: a SEPARATE draft (D-046). Never published together with the main ad of the same service."""
    if svc_hosp.get("compliance_required"):
        return {"service_key": key, "variant_of": key, "status": "blocked_compliance", "publish": False, "title_en": "", "title_el": "",
                "description": "", "images": [], "problems": ["compliance gate: documents required before any hospitality ad (see COMPLIANCE_GATE.md)"]}
    v = build_ad(key, {"title_en": hosp["title_en"], "title_el": hosp["title_el"], "el": hosp["el"], "en": hosp["en"]}, price, photos)
    v.update(variant_of=key, status="hospitality_variant_draft", publish=False)
    v["problems"] = check_ad(v, load_official())
    if hosp["title_en"].strip().lower() == content["title_en"].strip().lower() or hosp["title_el"] == content["title_el"]:
        v["problems"].append("variant has the same title as the main ad")
    return v


def variant_duplicates(variants, mains) -> list[str]:
    """Variants vs other variants and vs the main ads of OTHER services (same-service main is expected to be similar)."""
    errs = []
    pool = [x for x in variants if x.get("description")]
    for i, a in enumerate(pool):
        for b in pool[i + 1:] + [m for m in mains if m.get("description") and m["service_key"] != a["service_key"]]:
            sa, sb = shingles(a["description"]), shingles(b["description"])
            fj = len(sa & sb) / len(sa | sb) if sa | sb else 0.0
            tj = _jac(_words(a["title_en"]), _words(b["title_en"]))
            if fj >= NEAR_DUP_FULL or tj >= 0.5:
                kind = "variant" if b in pool else "main ad"
                errs.append(f"{a['service_key']} (hospitality): near-duplicate of {kind} {b['service_key']} (title {tj:.2f}, full {fj:.2f})")
    return errs


def ad_status(ad, svc, errors) -> str:
    if errors:
        return "blocked"
    if svc.get("ad_status") == "research_required" or svc.get("pricing", {}).get("price_status") != "approved" \
            or ad["price_meta"].get("approval_status") != "approved":
        return "draft"
    appr = {p["checksum_sha256"] for p in ad["images"] if p.get("status") == "approved" and p.get("approved") == "yes"}
    if len(appr) >= MIN_PHOTOS:
        return "ready_to_publish"
    usable = {p["checksum_sha256"] for p in ad["images"] if p.get("status") in ("approved", "proposed")}
    return "ready_to_review" if len(usable) >= MIN_PHOTOS else "draft"


# ---------------------------------------------------------------- run
def _load_photos():
    with open(PHOTO_V3, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by = {}
    for r in rows:
        by.setdefault(r["service_key"], []).append(r)
    for k in by:
        by[k].sort(key=lambda r: (r["status"] != "approved", r["source"] != "own", int(r["rank"] or 99)))
    return by


def _live_titles():
    with open(LIVE_META, encoding="utf-8") as f:
        return {r["id"]: r["title"] for r in csv.DictReader(f)}


def group_photos(rows):
    by = {}
    for r in rows:
        by.setdefault(r["service_key"], []).append(r)
    for k in by:
        by[k].sort(key=lambda r: (r["status"] != "approved", r["source"] != "own", int(r["rank"] or 99)))
    return by


def run(write: bool = True, data: dict | None = None) -> dict:
    """data (sandbox, STEP 12) may supply: registry, proposed (list), content, photos (rows), live_titles. Default = real files."""
    data = data or {}
    official = load_official()
    reg = data.get("registry") or load_registry()
    services = {s["service_key"]: s for s in reg["services"]}
    proposed = {e["service_key"]: e for e in (data.get("proposed") or json.loads(CATALOG_PROPOSED.read_text(encoding="utf-8")))}
    content = data.get("content") or json.loads(CONTENT.read_text(encoding="utf-8"))
    photos = group_photos(data["photos"]) if "photos" in data else _load_photos()
    live = data.get("live_titles") if "live_titles" in data else _live_titles()
    gate = data["quality_gate"] if "quality_gate" in data else load_gate()     # missing = not passed
    remediated = data["remediated"] if "remediated" in data else _load_remediated()
    ads = []
    for key, svc in services.items():
        if key in OWNER_HOLD:
            ads.append({"service_key": key, "status": "blocked", "problems": [OWNER_HOLD[key]], "title_en": "", "title_el": "",
                        "description": "", "images": [], "photo_counts": {}, "price_meta": {}})
            continue
        if key not in content or key not in proposed:
            ads.append({"service_key": key, "status": "draft", "problems": ["no content or catalog entry yet"], "title_en": "",
                        "title_el": "", "description": "", "images": [], "photo_counts": {}, "price_meta": {}})
            continue
        claims_for_generation(reg, key)            # raises if the registry would pass a prohibited claim
        if key in remediated:
            ad = build_ad_v2(key, remediated[key], proposed[key]["price_meta"], photos.get(key, []))
        else:
            ad = build_ad(key, content[key], proposed[key]["price_meta"], photos.get(key, []))
        ad["rubric"], ad["district"] = proposed[key]["rubric"], proposed[key]["district"]
        ad["attrs"] = proposed[key].get("attrs")
        prohibited = list(reg.get("global_claims_prohibited", [])) + list(svc.get("claims_prohibited", []))
        prohibited = [p for p in prohibited if p not in ("Bazaraki", r"\bfree\b")]   # covered by own checks
        ad["problems"] = check_ad(ad, official, prohibited)
        ad["live_conflicts"] = live_conflicts(ad, live, svc.get("live_ads", {}).get("ids", []))
        ads.append(ad)
    full = [a for a in ads if a.get("sections")]
    dups = duplicate_problems(full, live, {k: s.get("live_ads", {}).get("ids", []) for k, s in services.items()})
    for msg in dups:
        k = msg.split(":")[0]
        next(a for a in ads if a["service_key"] == k)["problems"].append(msg)
    for a in ads:
        if a.get("sections"):
            a["status"] = ad_status(a, services[a["service_key"]], a["problems"])
            if services[a["service_key"]].get("hospitality", {}).get("compliance_required") and a["status"].startswith("ready"):
                a["status"] = "draft"          # compliance gate (D-048): documents first
            if services[a["service_key"]].get("hospitality", {}).get("compliance_required"):
                a["compliance_required"] = True
            a["quality_passed"] = passed(gate, a["service_key"])          # STEP 13.1 gate (D-057)
            if not a["quality_passed"]:
                a["status"] = gate_status(a["status"], ["Advanced Ad Standard not passed"])
    variants = []
    for key, svc in services.items():
        h = svc.get("hospitality", {})
        if key in content and "hospitality" in content[key] and key in proposed:
            variants.append(build_variant(key, content[key], content[key]["hospitality"], proposed[key]["price_meta"],
                                          photos.get(key, []), h))
        elif h.get("compliance_required"):
            variants.append(build_variant(key, content.get(key, {}), {}, {}, [], h))
    for msg in variant_duplicates(variants, ads):
        k = msg.split(" ")[0]
        next(v for v in variants if v["service_key"] == k)["problems"].append(msg)
    result = {"ads": ads, "duplicates": dups, "variants": variants}
    if write:
        from bazaraki_agent.ad_reports import write_all
        write_all(result, services, official)
    return result


def main() -> int:
    res = run(write=True)
    for a in res["ads"]:
        print(f"{a['service_key']:18} {a['status']:16} {len(a.get('images', [])):2} img  {len(a['problems'])} problem(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
