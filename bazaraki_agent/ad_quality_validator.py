"""STEP 13.1: Advanced Ad Standard validator and read-only quality audit.

    python -m bazaraki_agent.ad_quality_validator          # audit, writes master_plan/quality/ only

validate_ad(ad, images, others, official) -> [(code, message)]; [] means the ad passes.
Codes: Q-COMPANY Q-CONTACT Q-BANNED Q-CLAIM Q-PASTOR Q-PARITY Q-TEMPLATE Q-TITLE Q-PRICE-EVIDENCE Q-VAT
Q-PRICE-SCOPE Q-PRICE-UNIT Q-LANG Q-IMG-COUNT Q-IMG-MATCH Q-IMG-TITLE Q-IMG-SCORE Q-IMG-SOURCE Q-IMG-LICENCE
Q-IMG-WATERMARK Q-IMG-REUSED Q-IMG-NEAR Q-IMG-RECORD Q-IMG-COVER Q-IMG-QUALITY Q-IMG-STOCK.

The audit never writes catalog.json, rates.json, manifest.csv, photo_manifest_v3.csv, content_blocks.json,
master_plan/ads/ or any XML, and never approves a photo.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from bazaraki_agent import ad_quality_policy as P
from bazaraki_agent.audit import shingles
from bazaraki_agent.validate import ARABIC, GREEK, LATIN, MAX_DESCRIPTION, PRICE_IN_TITLE, fold, stopword_hits

WS = Path(__file__).resolve().parents[2]
QUALITY = WS / "master_plan" / "quality"
DRAFTS = QUALITY / "remediated_drafts" / "drafts.json"
SCORES = QUALITY / "photo_scores.json"
GATE = QUALITY / "quality_gate.json"
PHOTO_V3 = WS / "master_plan" / "photo_system" / "photo_manifest_v3.csv"
ADS = WS / "master_plan" / "ads" / "ads_proposed.json"
CONTENT = WS / "master_plan" / "ads" / "content_blocks.json"
PROPOSED = WS / "master_plan" / "catalog_system" / "catalog_proposed.json"
SMALL = {"and", "for", "the", "of", "in", "with", "to", "a", "or", "on", "your", "και", "για", "σε", "με", "του", "της",
         "των", "την", "το", "τα", "η", "ο", "οι", "απο", "στο", "στη", "στην", "στα", "ή"}
PHOTO_NOTE = P.PHOTO_NOTE
AI_NOTE = P.AI_NOTE
LABELS = {"el": ("Περιλαμβάνει:", "Τιμή: ", " Η τιμή αφορά: "), "en": ("Included:", "Price: ", " The price covers: ")}


def _f(text: str) -> str:
    return fold(text or "").lower()


def _hits(patterns, text):
    t = _f(text)
    out = []
    for p in patterns:
        m = re.search(p, t)
        if m:
            out.append(m.group(0).strip())
    return out


# ---------------------------------------------------------------- build
def _fee_line(ad, lang):
    pm = ad.get("price_meta") or {}
    disp = pm.get("display_" + lang)
    if disp:
        scope = (ad.get("fee_scope") or {}).get(lang)
        return LABELS[lang][1] + disp + (LABELS[lang][2] + scope + "." if scope else "")
    return P.FEE_ENQUIRY[lang]


def block(ad, lang) -> str:
    s = ad["sections"][lang]
    title = ad["title_el"] if lang == "el" else ad["title_en"]
    lines = [title, "", s.get("problem", ""), s.get("solution", ""), "", LABELS[lang][0]]
    lines += [f"- {x}" for x in s.get("scope", [])]
    if s.get("limits"):
        lines += [""] + list(s["limits"])
    lines += [""] + [x for x in (s.get("trust"), s.get("customers"), s.get("coverage")) if x]
    lines += ["", s.get("process", ""), _fee_line(ad, lang)]
    if ad.get("stock_photos"):
        lines += ["", P.PHOTO_NOTE[lang]]
    if ad.get("ai_images"):
        lines += ["", P.AI_NOTE[lang]]
    lines += ["", s.get("cta", "")]
    return "\n".join(lines)


def build_description(ad) -> str:
    return block(ad, "el") + "\n\nENGLISH\n\n" + block(ad, "en")


# ---------------------------------------------------------------- text checks
def audit_text(text: str) -> list[tuple[str, str]]:
    """Checks that need only the description text (also used on legacy drafts)."""
    errs = []
    for h in _hits(P.COMPANY_IDENTITY, text):
        errs.append(("Q-COMPANY", f"company identity / legal entity / address in description: {h!r}"))
    for h in _hits(P.CONTACT, text):
        errs.append(("Q-CONTACT", f"contact detail or link in description: {h!r}"))
    if "bazaraki" in _f(text):
        errs.append(("Q-CONTACT", "description mentions Bazaraki (platform name not allowed in the text)"))
    for h in _hits(P.BANNED_PHRASES, text):
        errs.append(("Q-BANNED", f"banned generic wording: {h!r}"))
    t = text
    for line in (P.APPROVED_COVERAGE["el"], P.APPROVED_COVERAGE["en"], P.PHOTO_NOTE["el"], P.PHOTO_NOTE["en"],
                 P.AI_NOTE["el"], P.AI_NOTE["en"]):
        t = t.replace(line, " ")
    for h in _hits(P.UNSUPPORTED_CLAIMS, t):
        errs.append(("Q-CLAIM", f"claim without evidence on file: {h!r}"))
    for h in _hits(P.INTERNAL_WORDS, text):
        errs.append(("Q-CLAIM", f"internal cost / margin wording: {h!r}"))
    if ARABIC.search(text):
        errs.append(("Q-LANG", "Arabic text in description"))
    if len(text) > MAX_DESCRIPTION:
        errs.append(("Q-LANG", f"description {len(text)} chars > {MAX_DESCRIPTION} (official)"))
    first = next((ch for ch in text if ch.isalpha()), "")
    if text and not GREEK.match(first):
        errs.append(("Q-LANG", "description must start with Greek"))
    if text and not (GREEK.search(text) and LATIN.search(text)):
        errs.append(("Q-LANG", "description must contain Greek and English"))
    return errs


def title_problems(title, lang, service_key, official) -> list[tuple[str, str]]:
    out, L = [], lang.upper()
    if not (P.TITLE_MIN <= len(title) <= P.TITLE_MAX):
        out.append(("Q-TITLE", f"{L} title length {len(title)} (required {P.TITLE_MIN}-{P.TITLE_MAX})"))
    words = re.findall(r"[^\W_]+", title)
    if not (P.TITLE_WORDS_MIN <= len(words) <= P.TITLE_WORDS_MAX):
        out.append(("Q-TITLE", f"{L} title has {len(words)} words (required {P.TITLE_WORDS_MIN}-{P.TITLE_WORDS_MAX})"))
    bad = sorted({ch for ch in title if not (ch.isalpha() or ch.isdigit() or ch in P.TITLE_CHARS)})
    if bad:
        out.append(("Q-TITLE", f"{L} title characters not allowed (text and digits only): {''.join(bad)!r}"))
    if title.isupper() or any(len(w) > 3 and w.isupper() and w not in ("ETICS", "LED") for w in words):
        out.append(("Q-TITLE", f"{L} title uses capitals"))
    for w in stopword_hits(title, official["stopwords"]):
        out.append(("Q-TITLE", f"{L} title contains official stop word {w!r}"))
    if PRICE_IN_TITLE.search(fold(title)) or "€" in title:
        out.append(("Q-TITLE", f"{L} title contains a price"))
    for h in _hits(P.TITLE_HYPE, title):
        out.append(("Q-TITLE", f"{L} title exaggeration {h!r}"))
    fw = [w for w in re.findall(r"[^\W\d_]+", _f(title)) if w not in SMALL]
    rep = sorted({w for w in fw if fw.count(w) > 1})
    if rep:
        out.append(("Q-TITLE", f"{L} title repeats {rep}"))
    kw = P.SERVICE_KEYWORDS.get(service_key)
    if kw and not any(k in _f(title) for k in kw[0 if lang == "en" else 1]):
        out.append(("Q-TITLE", f"{L} title lacks the main service keyword ({'/'.join(kw[0 if lang == 'en' else 1])})"))
    return out


def pastor_problems(sections) -> list[tuple[str, str]]:
    out = []
    for lang in ("el", "en"):
        s = sections.get(lang, {})
        for k in P.PASTOR_REQUIRED:
            v = s.get(k)
            if not v or (k == "scope" and len(v) < P.MIN_SCOPE_ITEMS):
                out.append(("Q-PASTOR", f"{lang.upper()}: missing PASTOR section {k!r}"))
        if s.get("problem") and re.match("|".join(P.BANNED_OPENINGS), _f(s["problem"])):
            out.append(("Q-BANNED", f"{lang.upper()}: generic opening {s['problem'][:30]!r}"))
    return out


def claim_section_problems(ad) -> list[tuple[str, str]]:
    out = []
    for lang in ("el", "en"):
        s = ad["sections"].get(lang, {})
        if s.get("coverage") and s["coverage"] != P.APPROVED_COVERAGE[lang]:
            out.append(("Q-CLAIM", f"{lang.upper()}: coverage wording is not the approved coverage line"))
        if s.get("trust") and not ad.get("trust_evidence"):
            out.append(("Q-CLAIM", f"{lang.upper()}: trust section without evidence ids"))
    return out


def _numbers(s):
    text = " ".join([s.get(k, "") for k in ("problem", "solution", "trust", "customers", "coverage", "process", "cta")]
                    + list(s.get("scope", [])) + list(s.get("limits", [])))
    return sorted(re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d.,]*", text))


def parity_problems(ad) -> list[tuple[str, str]]:
    el, en, out = ad["sections"].get("el", {}), ad["sections"].get("en", {}), []
    for k in P.PASTOR_REQUIRED + P.PASTOR_OPTIONAL:
        if bool(el.get(k)) != bool(en.get(k)):
            out.append(("Q-PARITY", f"section {k!r} present in only one language"))
    if len(el.get("limits", [])) != len(en.get("limits", [])):
        out.append(("Q-PARITY", "limits/notes count differs between Greek and English"))
    if len(el.get("scope", [])) != len(en.get("scope", [])):
        out.append(("Q-PARITY", f"scope has {len(el.get('scope', []))} items in Greek, {len(en.get('scope', []))} in English"))
    if _numbers(el) != _numbers(en):
        out.append(("Q-PARITY", f"numbers differ: Greek {_numbers(el)} vs English {_numbers(en)}"))
    a, b = len(block(ad, "el")), len(block(ad, "en"))
    if b and not (0.7 <= a / b <= 1.8):
        out.append(("Q-PARITY", f"Greek/English length ratio {a / b:.2f} suggests missing content"))
    return out


def price_problems(ad, description) -> list[tuple[str, str]]:
    out, pm = [], ad.get("price_meta") or {}
    amounts = re.findall(r"€\s*[\d.,]+", description)
    if not amounts:
        return out
    status = ad.get("price_status")
    ok = status in P.PRICE_EVIDENCE_STATUSES and pm.get("approval_status") == "approved"
    ok = ok or (status == P.RESEARCH_EVIDENCE_STATUS and all(c.get("url") and c.get("date") for c in pm.get("citations", [])) and pm.get("citations"))
    if not ok:
        out.append(("Q-PRICE-EVIDENCE", f"price {amounts[0]} shown but price status is {status!r} (needs approved rate or cited research)"))
    for lang in ("el", "en"):
        disp = _f(pm.get("display_" + lang, ""))
        if not re.search(P.VAT_WORDS[lang], disp):
            out.append(("Q-VAT", f"{lang.upper()}: price line does not say whether VAT is included"))
        if not re.search(P.UNIT_WORDS[lang], disp):
            out.append(("Q-PRICE-UNIT", f"{lang.upper()}: price line has no unit"))
        if re.search(P.FROM_WORDS[lang], disp) and not (ad.get("fee_scope") or {}).get(lang):
            out.append(("Q-PRICE-SCOPE", f"{lang.upper()}: 'from' price without a defined scope"))
    return out


def _strip_fixed(text):
    for d in (P.APPROVED_COVERAGE, P.PHOTO_NOTE, P.AI_NOTE, P.FEE_ENQUIRY):
        for v in d.values():
            text = text.replace(v, " ")
    return text


def _jac(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def _wset(t):
    return {w for w in re.findall(r"[^\W\d_]+", _f(t)) if w not in SMALL}


def template_problems(ad, others) -> list[tuple[str, str]]:
    out = []
    me = shingles(_strip_fixed(ad.get("description", "")))
    for o in others:
        if o is ad or o.get("service_key") == ad.get("service_key") and o.get("variant_key") == ad.get("variant_key"):
            continue
        name = o.get("variant_key") or o.get("service_key")
        j = _jac(me, shingles(_strip_fixed(o.get("description", ""))))
        if j > P.MAX_TEMPLATE_SIMILARITY:
            out.append(("Q-TEMPLATE", f"description {j:.2f} similar to {name} (max {P.MAX_TEMPLATE_SIMILARITY})"))
        for lang in ("el", "en"):
            a, b = ad.get("sections", {}).get(lang, {}), o.get("sections", {}).get(lang, {})
            if not a or not b:
                continue
            pa, pb = a.get("problem", ""), b.get("problem", "")
            if pa and pb:
                if _f(pa).split()[:P.OPENING_WORDS] == _f(pb).split()[:P.OPENING_WORDS]:
                    out.append(("Q-TEMPLATE", f"{lang.upper()}: same opening as {name}"))
                elif _jac(_wset(pa), _wset(pb)) > P.MAX_PROBLEM_SIMILARITY:
                    out.append(("Q-TEMPLATE", f"{lang.upper()}: problem statement too close to {name}"))
            if a.get("cta") and a.get("cta") == b.get("cta"):
                out.append(("Q-TEMPLATE", f"{lang.upper()}: same closing line as {name}"))
            if a.get("process") and a.get("process") == b.get("process"):
                out.append(("Q-TEMPLATE", f"{lang.upper()}: same process sentence as {name}"))
    return out


# ---------------------------------------------------------------- images
def image_score(img) -> int:
    s = img.get("scores") or {}
    return sum(min(int(s.get(k, 0)), m) for k, m in P.RUBRIC_MAX.items())


def _ham(a, b):
    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except (TypeError, ValueError):
        return 99


def single_image_problems(img, ad) -> list[tuple[str, str]]:
    out, iid = [], img.get("image_id") or img.get("file")
    svc = ad.get("service_key")
    missing = [k for k in P.IMAGE_RECORD_FIELDS if not img.get(k)]
    if missing:
        out.append(("Q-IMG-RECORD", f"{iid}: record incomplete {missing}"))
    src, url = (img.get("source") or "").lower(), (img.get("source_url") or "").lower()
    if src not in P.ALLOWED_SOURCES or any(d in url for d in P.FORBIDDEN_DOMAINS):
        out.append(("Q-IMG-SOURCE", f"{iid}: source not allowed ({src}, {url[:60]})"))
    if src == "own":
        if img.get("rights_status") != "owned":
            out.append(("Q-IMG-LICENCE", f"{iid}: own photo without confirmed ownership"))
    elif src == P.AI_SOURCE:
        if img.get("generator") not in P.AI_GENERATORS:
            out.append(("Q-IMG-AI", f"{iid}: generator {img.get('generator')!r} not approved"))
        if not img.get("prompt_ref"):
            out.append(("Q-IMG-AI", f"{iid}: AI image without a recorded prompt"))
        if img.get("owner_authorisation") != P.AI_AUTHORISATION:
            out.append(("Q-IMG-AI", f"{iid}: AI image without the owner authorisation reference"))
    elif img.get("licence_verified") != "yes" or img.get("licence") not in P.LICENCE_EVIDENCE:
        out.append(("Q-IMG-LICENCE", f"{iid}: licence not verified"))
    if img.get("watermark") or img.get("visible_watermark") or img.get("logo") or img.get("text_overlay") or img.get("collage"):
        out.append(("Q-IMG-WATERMARK", f"{iid}: watermark, logo, text or collage"))
    if img.get("ai_generated") and src != P.AI_SOURCE:
        out.append(("Q-IMG-SOURCE", f"{iid}: undeclared AI-generated image"))
    if img.get("used_by_other_ad"):
        out.append(("Q-IMG-REUSED", f"{iid}: already used by {img['used_by_other_ad']}"))
    if img.get("same_scene"):
        out.append(("Q-IMG-NEAR", f"{iid}: same scene as another image of this ad"))
    if img.get("service_key") and img["service_key"] != svc:
        out.append(("Q-IMG-MATCH", f"{iid}: image belongs to {img['service_key']}, ad is {svc}"))
    tags = set(img.get("depicts") or [])
    allowed = P.SERVICE_SUBJECTS.get(svc, set())
    if tags - allowed:
        out.append(("Q-IMG-MATCH", f"{iid}: shows {sorted(tags - allowed)}, not the service {svc}"))
    sc = img.get("scores") or {}
    if sc:
        if int(sc.get("service", 0)) < P.MIN_SERVICE_SCORE:
            out.append(("Q-IMG-MATCH", f"{iid}: service match {sc.get('service')}/35 (min {P.MIN_SERVICE_SCORE})"))
        if int(sc.get("title", 0)) < P.MIN_TITLE_SCORE:
            out.append(("Q-IMG-TITLE", f"{iid}: title match {sc.get('title')}/20 (min {P.MIN_TITLE_SCORE})"))
        if image_score(img) < P.APPROVE_SCORE:
            out.append(("Q-IMG-SCORE", f"{iid}: rubric {image_score(img)}/100 (min {P.APPROVE_SCORE})"))
    if img.get("intended_title") and ad.get("title_en") and img["intended_title"] != ad["title_en"]:
        out.append(("Q-IMG-TITLE", f"{iid}: scored for another title"))
    try:
        if min(int(img.get("width") or 9999), int(img.get("height") or 9999)) < 800:
            out.append(("Q-IMG-QUALITY", f"{iid}: resolution below 800 px"))
    except ValueError:
        pass
    return out


def image_problems(ad, images, others=()) -> list[tuple[str, str]]:
    out, good = [], []
    other_imgs = [(o.get("variant_key") or o.get("service_key"), i) for o in others if o is not ad for i in o.get("images", [])]
    seen = []
    for img in images:
        errs = single_image_problems(img, ad)
        sha, ph, iid = img.get("checksum_sha256"), img.get("phash"), img.get("image_id") or img.get("file")
        for name, oi in other_imgs:
            if sha and sha == oi.get("checksum_sha256"):
                errs.append(("Q-IMG-REUSED", f"{iid}: same file as an image of {name}"))
            elif ph and _ham(ph, oi.get("phash")) <= P.PHASH_NEAR:
                errs.append(("Q-IMG-NEAR", f"{iid}: near-duplicate of an image of {name}"))
        for s2 in seen:
            if sha and sha == s2.get("checksum_sha256"):
                errs.append(("Q-IMG-REUSED", f"{iid}: same file twice in this ad"))
            elif ph and _ham(ph, s2.get("phash")) <= P.PHASH_NEAR:
                errs.append(("Q-IMG-NEAR", f"{iid}: near-duplicate of {s2.get('image_id') or s2.get('file')}"))
        seen.append(img)
        out += errs
        if not errs and img.get("approved") is True:
            good.append(img)
    if len(good) < P.MIN_APPROVED_IMAGES:
        out.append(("Q-IMG-COUNT", f"{len(good)} approved exact-match images (need {P.MIN_APPROVED_IMAGES})"))
    covers = [i for i in images if i.get("role") == "cover"]
    if images:
        if len(covers) != 1 or images[0].get("role") != "cover":
            out.append(("Q-IMG-COVER", "exactly one cover, placed first, is required"))
        else:
            c = covers[0]
            if set(c.get("depicts") or []) & (P.COVER_FORBIDDEN | P.ILLUSTRATIVE_ONLY_TAGS) and ad.get("service_key") != "bathroom":
                out.append(("Q-IMG-COVER", "cover is generic or illustrative-only"))
            owner_cover = P.OWNER_COVER.get(ad.get("service_key")) == c.get("image_id")
            if c.get("scores") and not owner_cover and image_score(c) < max(image_score(i) for i in images if i.get("scores")):
                out.append(("Q-IMG-COVER", "cover is not the strongest literal match"))
    stock = ad.get("stock_photos") or any(i.get("source") in ("pexels", "unsplash") for i in images)
    ai = ad.get("ai_images") or any(i.get("source") == P.AI_SOURCE for i in images)
    d = ad.get("description", "")
    if stock and (P.PHOTO_NOTE["el"] not in d or P.PHOTO_NOTE["en"] not in d):
        out.append(("Q-IMG-STOCK", "stock photos used without the illustrative-photo note in both languages"))
    if ai and (P.AI_NOTE["el"] not in d or P.AI_NOTE["en"] not in d):
        out.append(("Q-IMG-AI", "AI illustrative images used without the computer-generated note in both languages"))
    if stock or ai:
        for h in _hits(P.STOCK_AS_OWN, d):
            out.append(("Q-IMG-STOCK", f"stock photos presented as own work: {h!r}"))
    return out


# ---------------------------------------------------------------- whole ad + gate
def validate_ad(ad, images, others, official) -> list[tuple[str, str]]:
    d = ad.get("description") or ""
    errs = audit_text(d)
    errs += title_problems(ad.get("title_en", ""), "en", ad.get("service_key"), official)
    errs += title_problems(ad.get("title_el", ""), "el", ad.get("service_key"), official)
    if ad.get("sections"):
        errs += pastor_problems(ad["sections"]) + claim_section_problems(ad) + parity_problems(ad)
    else:
        errs.append(("Q-PASTOR", "no structured PASTOR sections"))
    errs += price_problems(ad, d)
    errs += template_problems(ad, others)
    errs += image_problems(ad, images, others)
    seen, out = set(), []
    for e in errs:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


IMAGE_CODES = {"Q-IMG-COUNT", "Q-IMG-MATCH", "Q-IMG-TITLE", "Q-IMG-SCORE", "Q-IMG-SOURCE", "Q-IMG-LICENCE", "Q-IMG-WATERMARK",
               "Q-IMG-REUSED", "Q-IMG-NEAR", "Q-IMG-RECORD", "Q-IMG-COVER", "Q-IMG-QUALITY"}


def gate_status(status: str, errors) -> str:
    """Pipeline gate: no ready_to_review / ready_to_publish without a clean quality result."""
    if errors and status in ("ready_to_review", "ready_to_publish"):
        return "draft"
    return status


def load_gate(path: Path = GATE) -> dict:
    """{service_key: {"passed": bool, ...}}. Missing file or key = not passed."""
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("services", {})


def passed(gate: dict, key: str) -> bool:
    return bool((gate.get(key) or {}).get("passed"))


# ---------------------------------------------------------------- audit (read-only)
def _image_from_row(r, scores, title):
    # score_key: stable name the visual scores were recorded under (files were renamed externally on 2026-10-06, D-110)
    key = (r.get("score_key") or "").strip() or Path(r["file"]).name
    s = scores.get(key)
    img = {"image_id": key, "file": r["file"], "source": r["source"], "source_url": r["source_url"],
           "licence": r["licence"], "licence_verified": r["licence_verified"], "rights_status": r["rights_status"],
           "download_date": r["download_date"], "checksum_sha256": r["checksum_sha256"], "phash": r["phash"],
           "service_key": r["service_key"], "variant_key": r["service_key"], "width": r["width"], "height": r["height"],
           "approved": r["status"] == "approved" and r["approved"] == "yes", "status": r["status"],
           "logo": r.get("logos_or_trademarks") == "yes"}
    if r["source"] == P.AI_SOURCE:
        img.update({"ai_generated": True, "generator": r.get("generator", ""), "prompt_ref": r.get("prompt_ref", ""),
                    "owner_authorisation": r.get("owner_authorisation", ""), "visible_watermark": r.get("visible_watermark") == "yes"})
    if s:
        img.update({"scores": s["scores"], "depicts": s["depicts"], "role": s["role"], "intended_title": title,
                    "logo": img["logo"] or s.get("logo"), "same_scene": s.get("same_scene"), "note": s["note"]})
    return img


def _order(imgs):
    imgs = sorted(imgs, key=lambda i: (i.get("role") != "cover", -image_score(i)))
    return imgs


def photo_decision(img, errs):
    codes = {c for c, _ in errs}
    if img["status"] == "rejected":
        return "rejected (earlier)", ""
    if img["status"] == "on_hold":
        return "on_hold (owner rights/approval)", "owner must approve from the contact sheet"
    if not img.get("scores"):
        return "unscored", "needs a visual rubric review before it can be proposed"
    if codes & {"Q-IMG-WATERMARK", "Q-IMG-QUALITY"}:
        return "rejected_for_quality", "; ".join(m for c, m in errs if c in ("Q-IMG-WATERMARK", "Q-IMG-QUALITY"))
    if codes & {"Q-IMG-MATCH", "Q-IMG-TITLE", "Q-IMG-SCORE", "Q-IMG-NEAR", "Q-IMG-REUSED"}:
        return "rejected_for_match", img.get("note", "")
    if codes & {"Q-IMG-SOURCE", "Q-IMG-LICENCE"}:
        return "rejected_for_rights", "; ".join(m for _, m in errs)
    return "passes_rubric (awaiting owner approval)", img.get("note", "")


def run(write: bool = True) -> dict:
    from bazaraki_agent.official import load as load_official
    from bazaraki_agent.registry import load_registry
    official = load_official()
    reg = {s["service_key"]: s for s in load_registry()["services"]}
    legacy = json.loads(ADS.read_text(encoding="utf-8"))
    drafts = json.loads(DRAFTS.read_text(encoding="utf-8")) if DRAFTS.is_file() else {"ads": []}
    proposed = {e["service_key"]: e for e in json.loads(PROPOSED.read_text(encoding="utf-8"))}
    sc = json.loads(SCORES.read_text(encoding="utf-8")) if SCORES.is_file() else {"photos": {}, "replacement_requirements": {}}
    with open(PHOTO_V3, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by = {}
    for r in rows:
        by.setdefault(r["service_key"], []).append(r)
    dtitle = {d["service_key"]: d["title_en"] for d in drafts["ads"]}

    # remediated drafts (review only)
    for d in drafts["ads"]:
        pm = proposed.get(d["service_key"], {}).get("price_meta", {})
        d["price_meta"] = pm if pm.get("approval_status") == "approved" else {}
        d["price_status"] = reg.get(d["service_key"], {}).get("pricing", {}).get("price_status")
        d["stock_photos"] = True
        d["description"] = build_description(d)
        d["images"] = _order([_image_from_row(r, sc["photos"], d["title_en"]) for r in by.get(d["service_key"], [])
                              if r["status"] == "proposed"])
    draft_res = {}
    for d in drafts["ads"]:
        errs = validate_ad(d, d["images"], drafts["ads"], official)
        draft_res[d["service_key"]] = errs

    # current ads in master_plan/ads/ads_proposed.json (read only; legacy layout or regenerated pastor_v2)
    leg_res = {}
    for a in legacy:
        key = a["service_key"]
        imgs = _order([_image_from_row(r, sc["photos"], dtitle.get(key, a["title_en"])) for r in by.get(key, []) if r["status"] == "proposed"])
        ad = {"service_key": key, "title_en": a["title_en"], "title_el": a["title_el"], "description": a["description"],
              "price_status": reg.get(key, {}).get("pricing", {}).get("price_status"),
              "price_meta": proposed.get(key, {}).get("price_meta", {}), "stock_photos": True}
        if a.get("layout") == "pastor_v2":            # regenerated from the remediated drafts
            full = {**ad, "sections": a["sections"], "fee_scope": a.get("fee_scope"), "variant_key": key}
            others = [{"service_key": o["service_key"], "variant_key": o["service_key"], "description": o["description"],
                       "sections": o.get("sections", {})} for o in legacy if o["service_key"] != key]
            errs = validate_ad(full, imgs, others, official)
            leg_res[key] = {"status_before": a["status"], "errors": errs, "images": imgs, "layout": "pastor_v2"}
            continue
        errs = audit_text(ad["description"]) + title_problems(ad["title_en"], "en", key, official) + \
            title_problems(ad["title_el"], "el", key, official)
        errs.append(("Q-PASTOR", "no problem statement, process or customer-type section (legacy structure)"))
        errs += price_problems(ad, ad["description"])
        errs += [e for e in template_problems(ad, [{"service_key": o["service_key"], "description": o["description"]} for o in legacy])]
        for lang, cta in (("el", "Στείλτε μας μήνυμα με την τοποθεσία"), ("en", "Send us a message with the location")):
            if cta in ad["description"]:
                errs.append(("Q-TEMPLATE", f"{lang.upper()}: shared closing line used by all ads"))
        errs += image_problems({**ad, "title_en": dtitle.get(key, a["title_en"])}, imgs)
        leg_res[key] = {"status_before": a["status"], "errors": list(dict.fromkeys(errs)), "images": imgs}

    # photo audit (all rows of photo_manifest_v3.csv, read only)
    photo_rows, seen_sha = [], {}
    for r in rows:
        title = dtitle.get(r["service_key"], "")
        img = _image_from_row(r, sc["photos"], title)
        errs = single_image_problems(img, {"service_key": r["service_key"], "title_en": title}) if img.get("scores") else \
            [e for e in single_image_problems(img, {"service_key": r["service_key"]}) if e[0] in ("Q-IMG-SOURCE", "Q-IMG-LICENCE", "Q-IMG-QUALITY", "Q-IMG-WATERMARK")]
        if r["checksum_sha256"] in seen_sha and seen_sha[r["checksum_sha256"]] != r["service_key"]:
            errs.append(("Q-IMG-REUSED", f"same file also in {seen_sha[r['checksum_sha256']]}"))
        seen_sha.setdefault(r["checksum_sha256"], r["service_key"])
        dec, why = photo_decision(img, errs)
        photo_rows.append({"file": r["file"], "service_key": r["service_key"], "manifest_status": r["status"], "source": r["source"],
                           "score": image_score(img) if img.get("scores") else "", "role": img.get("role", ""),
                           "depicts": ",".join(img.get("depicts", [])), "decision": dec, "reason": why,
                           "codes": " ".join(sorted({c for c, _ in errs})),
                           "replacement_requirement": sc["replacement_requirements"].get(r["service_key"], "") if dec.startswith("rejected_for") else ""})

    result = {"legacy": leg_res, "drafts": drafts["ads"], "draft_errors": draft_res, "photos": photo_rows, "registry": reg}
    if write:
        from bazaraki_agent.ad_quality_reports import write_all
        write_all(result)
    return result


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    res = run(write=True)
    n = len(res["legacy"])
    ok = sum(1 for v in res["legacy"].values() if not v["errors"])
    print(f"audited {n} ads, {ok} pass; remediated drafts text-clean: "
          f"{sum(1 for e in res['draft_errors'].values() if not [x for x in e if x[0] not in IMAGE_CODES and x[0] != 'Q-IMG-STOCK'])}/{len(res['draft_errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
