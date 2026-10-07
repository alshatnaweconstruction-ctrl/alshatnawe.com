"""STEP 7: pricing approval engine and catalog proposal.

Links the service registry (master_plan/registry) to the owner-approved prices in
data/rates.json and produces master_plan/catalog_system/catalog_proposed.json.
It NEVER writes catalog.json or rates.json, never sets publish:true, and never
invents a price: a service without an approved rate stays a draft at 0.00.

    python -m bazaraki_agent.pricing          # write catalog_proposed.json + CATALOG_DIFF.md
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

from bazaraki_agent.registry import load_registry, validate_registry
from bazaraki_agent.validate import REPO, load_rates, validate

CATALOG = REPO / "bazaraki_agent" / "catalog.json"
OUT_DIR = REPO.parent / "master_plan" / "catalog_system"
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COVERAGE = ("All of Cyprus; service availability is confirmed depending on the property location "
            "and project requirements")
VAT_EN, VAT_EL = "Prices exclude VAT.", "Οι τιμές δεν περιλαμβάνουν ΦΠΑ."
UNIT_SHORT = [  # (match in rates unit text, EN, EL)
    ("per m2", "per m²", "ανά μ²"), ("per standard bathroom", "per bathroom", "ανά μπάνιο"),
    ("per kitchen project", "per project", "ανά έργο"), ("per month", "per month", "ανά μήνα"),
    ("per hour", "per hour", "ανά ώρα"), ("per visit", "per visit", "ανά επίσκεψη"),
]
NEW_TITLES = {  # from master_plan/registry/MIGRATION_PLAN.md (checked by validate.py)
    "pool-renovation": "Swimming pool renovation and rehabilitation in Cyprus",
    "concrete-repairs": "Concrete and balcony repairs for homes and apartment blocks",
    "retaining-walls": "Retaining walls for sloped plots and gardens",
    "damp-repairs": "Damp and water damage repairs for homes",
    "etics": "External wall insulation ETICS for houses",
    "joinery": "Bespoke joinery TV walls wardrobes and cabinets",
    "electrical": "Electrical installation and repair works for homes and shops",
    "light-steel": "Light steel structures, carports and rooftop rooms",
}
TEMPLATE_KEYS = ["negotiable_price", "exchange", "phone_hide", "chosen_phone", "whatsapp", "disallow_chat", "attrs", "geometry"]


def load_catalog(path: Path = CATALOG) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _unit_short(unit: str) -> tuple[str, str]:
    u = (unit or "").lower()
    for k, en, el in UNIT_SHORT:
        if k in u:
            return en, el
    return unit, unit


def price_view(svc: dict, rates: dict) -> dict:
    """Pricing facts for one registry service. Raises if registry and rates.json disagree."""
    p = svc.get("pricing", {})
    key = p.get("rates_key")
    rate = rates.get(key or "", {})
    approved = bool(rate.get("approved_by")) and p.get("price_status") == "approved"
    if p.get("price_status") == "approved":
        if not rate.get("approved_by"):
            raise ValueError(f"{svc['service_key']}: registry says approved but rates.json has no approved rate")
        if abs(float(rate["approved_price"]) - float(p.get("approved_price") or -1)) > 0.001:
            raise ValueError(f"{svc['service_key']}: registry price {p.get('approved_price')} != rates.json {rate['approved_price']}")
    if not approved:
        return {"service_key": svc["service_key"], "unit": p.get("unit"), "price": None, "vat": "excluded",
                "approval_status": "research_required", "approved_by": "", "approved_date": "", "confidence": None,
                "sources": [], "display_en": "", "display_el": "", "rates_key": None}
    en, el = _unit_short(rate.get("unit", ""))
    price = rate["approved_price"]
    amount = f"€{price:,.0f}" if float(price).is_integer() else f"€{price:,.2f}"
    basis = rate.get("basis", "from")
    return {"service_key": svc["service_key"], "unit": rate.get("unit"), "price": price, "vat": "excluded",
            "approval_status": "approved", "approved_by": rate["approved_by"], "approved_date": rate["approved_date"],
            "confidence": rate.get("confidence"), "rates_key": key,
            "sources": [{"source": s.get("source"), "url": s.get("url"), "figure": s.get("figure")} for s in rate.get("sources", [])],
            "display_en": f"{'From ' if basis == 'from' else ''}{amount} {en}. {VAT_EN}",
            "display_el": f"{'Από ' if basis == 'from' else ''}{amount.replace(',', '.')} {el}. {VAT_EL}"}


def build_catalog_proposed(registry: dict, rates: dict, catalog: list[dict]) -> tuple[list[dict], dict]:
    """Return (proposed entries, skipped {service_key: reason}). Inputs are not mutated."""
    current = {c["service_key"]: c for c in copy.deepcopy(catalog)}
    template = {k: copy.deepcopy(next(iter(current.values()), {}).get(k)) for k in TEMPLATE_KEYS} if current else {}
    out, skipped = [], {}
    for s in registry["services"]:
        key = s["service_key"]
        rubric = s.get("bazaraki_category", {}).get("rubric_id")
        if not rubric:
            skipped[key] = "category not decided (needs owner decision); not added"
            continue
        v = price_view(s, rates)
        if key in current:
            e = current[key]
        else:
            e = {"service_key": key, "group": s.get("group"), "publish": False, "last_update": "2026-10-03 12:00:00",
                 "external_id": "AS-" + key.upper(), "status": "active", "rubric": str(rubric),
                 "district": s.get("locations", {}).get("xml_district_id", "5713"),
                 "title": NEW_TITLES.get(key, s["names"]["en"]), "description": "", "price": "0.00", **copy.deepcopy(template),
                 "images": [], "notes": ""}
        e["publish"] = False
        e["price"] = f"{float(v['price']):.2f}" if v["price"] is not None else "0.00"
        e["coverage"] = COVERAGE
        e["price_meta"] = v
        e["registry_status"] = s.get("ad_status")
        out.append(e)
    return out, skipped


def propose_rate_approval(rates: dict, key: str, price: float, unit: str, by: str, date: str,
                          sources: list | None = None) -> dict:
    """A NEW rates dict with one owner-approved price added. rates.json itself is never written here."""
    if not by.strip():
        raise ValueError("approved_by required")
    if not ISO.match(date):
        raise ValueError("approved_date must be YYYY-MM-DD")
    if not price or float(price) <= 0:
        raise ValueError("price must be > 0")
    new = copy.deepcopy(rates)
    new[key] = {"unit": unit, "basis": "from", "market_low": None, "market_typical": None, "market_high": None,
                "sources": sources or [], "confidence": None, "internal_evidence": "", "proposed_price": price,
                "approved_price": price, "currency": "EUR", "vat_included": False, "approved_by": by, "approved_date": date}
    return new


def diff_report(current: list[dict], proposed: list[dict], skipped: dict) -> str:
    cur = {c["service_key"]: c for c in current}
    L = ["# catalog_proposed.json vs catalog.json (STEP 7, 2026-10-03)", "",
         "`catalog.json` is **unchanged**. This is a proposal; applying it needs a separate owner approval (migration).", "",
         "| service | change | catalog.json | catalog_proposed.json |", "|---|---|---|---|"]
    for p in proposed:
        k = p["service_key"]
        if k not in cur:
            L.append(f"| {k} | **new draft entry** | — | rubric {p['rubric']}, price {p['price']} ({p['price_meta']['approval_status']}), publish false |")
            continue
        c = cur[k]
        for f in sorted(set(c) | set(p)):
            if f in ("price_meta", "registry_status"):
                continue
            if c.get(f) != p.get(f):
                L.append(f"| {k} | {f} | {json.dumps(c.get(f), ensure_ascii=False)} | {json.dumps(p.get(f), ensure_ascii=False)} |")
        L.append(f"| {k} | + price_meta (new field, ignored by the feed) | — | {p['price_meta']['display_en']} |")
    for k, why in skipped.items():
        L.append(f"| {k} | **not included** | — | {why} |")
    return "\n".join(L) + "\n"


def main() -> int:
    reg = load_registry()
    rates, catalog = load_rates(), load_catalog()
    errs = validate_registry(reg, expected_count=22)
    if errs:
        print("registry invalid:", *errs, sep="\n  "); return 1
    proposed, skipped = build_catalog_proposed(reg, rates, catalog)
    verrs, warns = validate(proposed)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "catalog_proposed.json").write_bytes((json.dumps(proposed, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    (OUT_DIR / "CATALOG_DIFF.md").write_bytes(diff_report(catalog, proposed, skipped).encode("utf-8"))
    print(f"catalog_proposed.json: {len(proposed)} entries ({sum(e['price_meta']['approval_status'] == 'approved' for e in proposed)} "
          f"priced, {len(skipped)} skipped) | validate: {len(verrs)} error(s), {len(warns)} warning(s)")
    for e in verrs:
        print("ERROR", e)
    return 1 if verrs else 0


if __name__ == "__main__":
    sys.exit(main())
