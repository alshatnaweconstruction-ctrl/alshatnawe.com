"""STEP 5: validate the service registry (planning layer for all 22 services).

The registry lives outside the feed repo, in master_plan/registry/services_registry.json.
It is read-only for this module: nothing here writes catalog.json, rates.json,
manifest.csv or any XML.

    python -m bazaraki_agent.registry            # validate the real registry
"""

from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path

from bazaraki_agent.official import SOURCE as OFFICIAL_SOURCE, load as load_official
from bazaraki_agent.validate import REPO, load_manifest, load_rates

REGISTRY = REPO.parent / "master_plan" / "registry" / "services_registry.json"
PROPERTY_PREFIX = "Services / Property, maintenance / "
DISTRICTS = ("Famagusta", "Nicosia", "Limassol", "Larnaca", "Paphos")

AD_STATUSES = {"research_required", "prepare_now", "ready_to_review", "approved_to_publish"}
PRICE_STATUSES = {"approved", "draft", "research_required"}
PHOTO_STATUSES = {"ready", "on_hold", "missing"}
EVIDENCE_LEVELS = {"completed_project", "signed_work", "quote", "inquiry", "none"}
CATEGORY_CONFIDENCE = {"high", "medium", "low", "needs_owner_decision"}
LIVE_RELATIONSHIPS = {"none", "update", "merge", "archive"}
MIN_PHOTOS = 5


@lru_cache(maxsize=None)
def district_map(path: Path = OFFICIAL_SOURCE) -> dict[str, str]:
    """location id -> district, from the section headers of the official list."""
    current, out = None, {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s in DISTRICTS:
            current = s
            continue
        m = re.match(r"^(\d+)\s*\|", s)
        if m and current:
            out[m.group(1)] = current
    return out


def district_of(location_id: str) -> str | None:
    return district_map().get(str(location_id))


def load_registry(path: Path = REGISTRY) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _prohibited_patterns(reg: dict, svc: dict) -> list[re.Pattern]:
    terms = list(reg.get("global_claims_prohibited", [])) + list(svc.get("claims_prohibited", []))
    return [re.compile(t if any(c in t for c in "\\[](){}+*?|^$") else re.escape(t), re.I) for t in terms]


def _bad_claims(reg: dict, svc: dict) -> list[tuple[str, str]]:
    pats = _prohibited_patterns(reg, svc)
    return [(c, p.pattern) for c in svc.get("claims_allowed", []) for p in pats if p.search(c)]


def claims_for_generation(reg: dict, service_key: str) -> list[str]:
    """The only claims an ad-generation stage may receive; raises if any is prohibited."""
    svc = next(s for s in reg["services"] if s["service_key"] == service_key)
    bad = _bad_claims(reg, svc)
    if bad:
        raise ValueError(f"{service_key}: prohibited claim(s) in claims_allowed: {bad}")
    return list(svc.get("claims_allowed", []))


def validate_registry(reg: dict, rates: dict | None = None, manifest: dict | None = None,
                      official: dict | None = None, expected_count: int | None = None) -> list[str]:
    rates = load_rates() if rates is None else rates
    manifest = load_manifest() if manifest is None else manifest
    official = load_official() if official is None else official
    rubrics, districts = official["rubrics"], official["districts"]
    errors: list[str] = []
    services = reg.get("services", [])

    if expected_count is not None and len(services) != expected_count:
        errors.append(f"expected {expected_count} services, found {len(services)}")
    seen: set[str] = set()
    live_owner: dict[str, str] = {}

    for s in services:
        key = s.get("service_key", "")
        e = lambda msg, k=key: errors.append(f"{k}: {msg}")
        if not key:
            errors.append("service without service_key")
            continue
        if key in seen:
            e("duplicate service_key")
        seen.add(key)
        names = s.get("names", {})
        for lang in ("ar", "el", "en"):
            if not names.get(lang):
                e(f"name.{lang} missing")

        # enums
        for field, allowed, value in (("ad_status", AD_STATUSES, s.get("ad_status")),
                                      ("evidence_level", EVIDENCE_LEVELS, s.get("evidence_level")),
                                      ("pricing.price_status", PRICE_STATUSES, s.get("pricing", {}).get("price_status")),
                                      ("images.status", PHOTO_STATUSES, s.get("images", {}).get("status")),
                                      ("bazaraki_category.confidence", CATEGORY_CONFIDENCE,
                                       s.get("bazaraki_category", {}).get("confidence")),
                                      ("live_ads.relationship", LIVE_RELATIONSHIPS,
                                       s.get("live_ads", {}).get("relationship"))):
            if value not in allowed:
                e(f"{field} {value!r} not in {sorted(allowed)}")

        # category: official IDs only
        cat = s.get("bazaraki_category", {})
        for rid in [cat.get("rubric_id")] + list(cat.get("candidates", [])):
            if rid is None:
                continue
            name = rubrics.get(str(rid), "")
            if not name.startswith(PROPERTY_PREFIX):
                e(f"category {rid} is not an official 'Property, maintenance' category")
        if not cat.get("rubric_id") and cat.get("confidence") != "needs_owner_decision":
            e("rubric_id missing (set it, or mark confidence needs_owner_decision with candidates)")
        if cat.get("confidence") == "needs_owner_decision" and not cat.get("candidates"):
            e("needs_owner_decision but no candidate categories")

        # location: official IDs only
        loc = s.get("locations", {})
        if str(loc.get("xml_district_id")) not in districts:
            e(f"xml_district_id {loc.get('xml_district_id')!r} is not an official location")

        # price linkage
        p = s.get("pricing", {})
        if p.get("price_status") == "approved":
            rate = rates.get(p.get("rates_key") or "", {})
            if not rate.get("approved_by"):
                e(f"price_status approved but no approved rate for rates_key {p.get('rates_key')!r}")
            elif p.get("approved_price") is None or abs(float(rate["approved_price"]) - float(p["approved_price"])) > 0.001:
                e(f"approved_price {p.get('approved_price')} differs from rates.json {rate.get('approved_price')}")
        elif p.get("rates_key") and rates.get(p["rates_key"], {}).get("approved_by"):
            e("rates.json has an approved price but price_status is not 'approved'")

        # photos: counts come from the manifest, never from the registry alone
        rows = [r for r in manifest.values() if r.get("service_key") == key]
        approved = sum(1 for r in rows if r.get("approved", "").strip().lower() == "yes")
        held = sum(1 for r in rows if r.get("approved", "").strip().lower() == "on_hold")
        img = s.get("images", {})
        if img.get("on_hold_count", 0) != held:
            e(f"images.on_hold_count {img.get('on_hold_count')} != manifest on_hold rows {held}")
        if img.get("approved_count", 0) > approved:
            e(f"images.approved_count {img.get('approved_count')} > manifest approved rows {approved}")
        if img.get("status") == "ready" and approved < MIN_PHOTOS:
            e(f"images.status ready but only {approved} approved photos (min {MIN_PHOTOS})")

        # publishing gate
        if s.get("ad_status") == "approved_to_publish":
            if approved < MIN_PHOTOS:
                e(f"approved_to_publish needs {MIN_PHOTOS} approved photos in the manifest, has {approved}")
            if p.get("price_status") != "approved":
                e("approved_to_publish but price not approved")
            if cat.get("confidence") == "needs_owner_decision":
                e("approved_to_publish but category still needs an owner decision")

        # claims gate
        for claim, pat in _bad_claims(reg, s):
            e(f"claims_allowed contains prohibited term /{pat}/: {claim!r}")

        # live ads: one service per live ad
        for lid in s.get("live_ads", {}).get("ids", []):
            other = live_owner.setdefault(str(lid), key)
            if other != key:
                e(f"live ad {lid} also linked to {other}")

    return errors


def main() -> int:
    reg = load_registry()
    errors = validate_registry(reg, expected_count=22)
    for msg in errors:
        print("ERROR  ", msg)
    svcs = reg["services"]
    print(f"{len(errors)} error(s); {len(svcs)} services; "
          f"approved prices {sum(s['pricing']['price_status'] == 'approved' for s in svcs)}; "
          f"approved_to_publish {sum(s['ad_status'] == 'approved_to_publish' for s in svcs)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
