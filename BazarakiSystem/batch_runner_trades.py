#!/usr/bin/env python3
"""
BazarakiSystem v4.1 — Trade Services Batch Runner
Generates ad packages for Tiling | Renovation | Builders services × 4 Cyprus locations.

18 service types × 4 locations = 72 ads
Cyprus 2026 real market pricing with per-m² rates where applicable.
English only — Bazaraki: English and Greek only, NO Arabic.
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade_services_patch import (
    build_trade_description,
    build_trade_title,
    get_trade_price,
    TRADE_SERVICE_LABELS,
)

LOCATIONS = ["paphos", "limassol", "larnaca", "nicosia"]

SERVICES = [
    # ── Tiling ──────────────────────────────────────────────────────────────────
    {"service_type": "tiling_floor_ceramic",   "experience_years": 12, "projects_completed": 380,
     "category": "TILING SERVICES"},
    {"service_type": "tiling_floor_porcelain", "experience_years": 12, "projects_completed": 280,
     "category": "TILING SERVICES"},
    {"service_type": "tiling_bathroom",        "experience_years": 12, "projects_completed": 420,
     "category": "TILING SERVICES"},
    {"service_type": "tiling_outdoor",         "experience_years": 12, "projects_completed": 250,
     "category": "TILING SERVICES"},
    {"service_type": "tiling_mosaic_feature",  "experience_years": 15, "projects_completed": 120,
     "category": "TILING SERVICES"},
    {"service_type": "tiling_large_format",    "experience_years": 12, "projects_completed": 180,
     "category": "TILING SERVICES"},

    # ── Renovation ───────────────────────────────────────────────────────────────
    {"service_type": "renovation_cosmetic",    "experience_years": 12, "projects_completed": 310,
     "category": "RENOVATION SERVICES"},
    {"service_type": "renovation_standard",    "experience_years": 15, "projects_completed": 210,
     "category": "RENOVATION SERVICES"},
    {"service_type": "renovation_premium",     "experience_years": 15, "projects_completed": 85,
     "category": "RENOVATION SERVICES"},
    {"service_type": "renovation_kitchen",     "experience_years": 12, "projects_completed": 260,
     "category": "RENOVATION SERVICES"},
    {"service_type": "renovation_bathroom",    "experience_years": 12, "projects_completed": 390,
     "category": "RENOVATION SERVICES"},
    {"service_type": "renovation_commercial",  "experience_years": 15, "projects_completed": 75,
     "category": "RENOVATION SERVICES"},

    # ── Builders ─────────────────────────────────────────────────────────────────
    {"service_type": "build_residential_new",  "experience_years": 15, "projects_completed": 120,
     "category": "BUILDERS & CONSTRUCTION"},
    {"service_type": "build_villa",            "experience_years": 15, "projects_completed": 65,
     "category": "BUILDERS & CONSTRUCTION"},
    {"service_type": "build_extension",        "experience_years": 12, "projects_completed": 180,
     "category": "BUILDERS & CONSTRUCTION"},
    {"service_type": "build_commercial",       "experience_years": 15, "projects_completed": 55,
     "category": "BUILDERS & CONSTRUCTION"},
    {"service_type": "build_fitout",           "experience_years": 12, "projects_completed": 220,
     "category": "BUILDERS & CONSTRUCTION"},
    {"service_type": "build_structural",       "experience_years": 15, "projects_completed": 90,
     "category": "BUILDERS & CONSTRUCTION"},
]

# Images — 5 per service type, to be sourced from Pinterest/internet
SERVICE_IMAGES = {
    "tiling_floor_ceramic":    [f"/images/tiling/ceramic_{i}.jpg" for i in range(1, 6)],
    "tiling_floor_porcelain":  [f"/images/tiling/porcelain_{i}.jpg" for i in range(1, 6)],
    "tiling_bathroom":         [f"/images/tiling/bathroom_{i}.jpg" for i in range(1, 6)],
    "tiling_outdoor":          [f"/images/tiling/outdoor_{i}.jpg" for i in range(1, 6)],
    "tiling_mosaic_feature":   [f"/images/tiling/mosaic_{i}.jpg" for i in range(1, 6)],
    "tiling_large_format":     [f"/images/tiling/large_format_{i}.jpg" for i in range(1, 6)],
    "renovation_cosmetic":     [f"/images/renovation/cosmetic_{i}.jpg" for i in range(1, 6)],
    "renovation_standard":     [f"/images/renovation/standard_{i}.jpg" for i in range(1, 6)],
    "renovation_premium":      [f"/images/renovation/premium_{i}.jpg" for i in range(1, 6)],
    "renovation_kitchen":      [f"/images/renovation/kitchen_{i}.jpg" for i in range(1, 6)],
    "renovation_bathroom":     [f"/images/renovation/bathroom_{i}.jpg" for i in range(1, 6)],
    "renovation_commercial":   [f"/images/renovation/commercial_{i}.jpg" for i in range(1, 6)],
    "build_residential_new":   [f"/images/builders/residential_{i}.jpg" for i in range(1, 6)],
    "build_villa":             [f"/images/builders/villa_{i}.jpg" for i in range(1, 6)],
    "build_extension":         [f"/images/builders/extension_{i}.jpg" for i in range(1, 6)],
    "build_commercial":        [f"/images/builders/commercial_{i}.jpg" for i in range(1, 6)],
    "build_fitout":            [f"/images/builders/fitout_{i}.jpg" for i in range(1, 6)],
    "build_structural":        [f"/images/builders/structural_{i}.jpg" for i in range(1, 6)],
}


def run_batch():
    total_ads = len(SERVICES) * len(LOCATIONS)
    print("=" * 90)
    print("🏗️  BAZARAKI TRADE SERVICES — FULL CATALOG BATCH GENERATION")
    print(f"   Date      : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Services  : {len(SERVICES)} types  |  Locations: {len(LOCATIONS)}  |  Total: {total_ads} ads")
    print("=" * 90)

    results = []
    approved = 0
    errors = 0
    last_category = None

    for svc in SERVICES:
        cat = svc.get("category", "")
        if cat != last_category:
            print(f"\n── {cat} {'─' * (60 - len(cat))}")
            last_category = cat

        for location in LOCATIONS:
            service_type = svc["service_type"]
            ctx = {
                "service_type":       service_type,
                "location":           location,
                "experience_years":   svc["experience_years"],
                "projects_completed": svc["projects_completed"],
            }

            try:
                title       = build_trade_title(ctx)
                description = build_trade_description(ctx)
                price       = get_trade_price(service_type, location, svc["experience_years"])
                images      = SERVICE_IMAGES.get(service_type, [])

                # Simple quality check
                word_count  = len(description.split())
                quality     = min(100, 60 + word_count // 8)
                status      = "APPROVED" if word_count >= 80 else "NEEDS_REVISION"

                if status == "APPROVED":
                    approved += 1

                results.append({
                    "category":          cat,
                    "service_type":      service_type,
                    "location":          location,
                    "status":            status,
                    "title":             title,
                    "description":       description,
                    "price_unit":        price["unit"],
                    "price_min":         price["min"],
                    "price_max":         price["max"],
                    "price_recommended": price["recommended"],
                    "quality_score":     quality,
                    "images":            images,
                    "word_count":        word_count,
                })

                icon = "✅" if status == "APPROVED" else "⚠️ "
                unit = price["unit"]
                if unit == "m²":
                    price_str = f"€{price['min']}/m²–€{price['max']}/m²"
                else:
                    price_str = f"€{price['min']:,}–€{price['max']:,}"
                print(f"  {icon} {service_type:28s} | {location:9s} | {price_str:22s} | Q:{quality}%")

            except Exception as e:
                print(f"  ❌ ERROR {service_type}/{location}: {e}")
                errors += 1
                results.append({
                    "category": cat, "service_type": service_type,
                    "location": location, "status": "ERROR", "error": str(e),
                })

    # ── Summary ──────────────────────────────────────────────────────────────────
    print()
    print("=" * 90)
    print("📊 TRADE SERVICES BATCH SUMMARY")
    print(f"   Total Generated : {total_ads}")
    print(f"   ✅ Approved     : {approved}  ({approved/total_ads*100:.0f}%)")
    print(f"   ❌ Errors       : {errors}")
    print("=" * 90)

    # ── Save ─────────────────────────────────────────────────────────────────────
    out = "/tmp/bazaraki_trades_batch_results.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at":    datetime.now().isoformat(),
            "system_version":  "4.1-trades",
            "summary": {"total": total_ads, "approved": approved, "errors": errors},
            "ads": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Results saved to {out}")

    # ── Print approved titles ─────────────────────────────────────────────────────
    approved_ads = [r for r in results if r.get("status") == "APPROVED"]
    print(f"\n{'='*90}")
    print(f"📋 {len(approved_ads)} TRADE ADS READY TO POST ON BAZARAKI")
    print(f"{'='*90}")
    current_cat = None
    for i, ad in enumerate(approved_ads, 1):
        if ad.get("category") != current_cat:
            current_cat = ad.get("category", "")
            print(f"\n── {current_cat}")
        unit = ad.get("price_unit", "")
        if unit == "m²":
            pstr = f"€{ad['price_min']}/m²"
        else:
            pstr = f"€{ad['price_min']:,}"
        print(f"  [{i:3d}] {ad['title']}")
        print(f"        Location: {ad['location'].title()}, Cyprus | From: {pstr} | Quality: {ad['quality_score']}%")

    return results


if __name__ == "__main__":
    run_batch()
