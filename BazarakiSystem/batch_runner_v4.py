#!/usr/bin/env python3
"""
BazarakiSystem v4.1 - Full Catalog Batch Runner
Generates complete ad packages for ALL pool service categories × 4 Cyprus locations.

Service categories (27 types × 4 locations = 108 ads):
  ┌ Residential Pool Construction (by size: small / medium / large)
  ├ Pool Types            (overflow, skimmer, infinity)
  ├ Pool Internal Linings (liner, mosaic, ceramic)
  ├ Maintenance           (weekly, comprehensive, daily)
  ├ Commercial            (commercial pool, spa, fountain, hotel service)
  ├ Specialty             (swim spa, waterpark, cooling/heating, rock features, bar & stools)
  └ Renovation            (basic, complete)

English only — Cyprus market — Real 2026 prices.
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from master_system_v4 import BazarakiMasterSystemV4

# ── Configuration ───────────────────────────────────────────────────────────────

LOCATIONS = ["paphos", "limassol", "larnaca", "nicosia"]

SERVICES = [
    # ── Maintenance ─────────────────────────────────────────────────────────────
    {"service_type": "maintenance_weekly",        "experience_years": 12, "projects_completed": 400,
     "category": "RESIDENTIAL POOL SERVICES"},
    {"service_type": "maintenance_comprehensive", "experience_years": 12, "projects_completed": 400,
     "category": "RESIDENTIAL POOL SERVICES"},
    {"service_type": "maintenance_daily",         "experience_years": 12, "projects_completed": 400,
     "category": "COMMERCIAL POOL SERVICE"},

    # ── Residential Construction by size ─────────────────────────────────────────
    {"service_type": "construction_small",        "experience_years": 15, "projects_completed": 280,
     "category": "CONSTRUCTION SERVICES"},
    {"service_type": "construction_medium",       "experience_years": 15, "projects_completed": 180,
     "category": "CONSTRUCTION SERVICES"},
    {"service_type": "construction_large",        "experience_years": 15, "projects_completed": 80,
     "category": "CONSTRUCTION SERVICES"},

    # ── Pool Types ───────────────────────────────────────────────────────────────
    {"service_type": "pool_overflow",             "experience_years": 15, "projects_completed": 95,
     "category": "POOL CATEGORIES - Overflow"},
    {"service_type": "pool_skimmer",              "experience_years": 15, "projects_completed": 220,
     "category": "POOL CATEGORIES - Skimmer"},
    {"service_type": "pool_infinity",             "experience_years": 15, "projects_completed": 65,
     "category": "POOL CATEGORIES - Infinity"},

    # ── Pool Internal Linings ─────────────────────────────────────────────────────
    {"service_type": "lining_liner",              "experience_years": 12, "projects_completed": 300,
     "category": "Pool Internal Linings - Liner"},
    {"service_type": "lining_mosaic",             "experience_years": 12, "projects_completed": 180,
     "category": "Pool Internal Linings - Mosaic"},
    {"service_type": "lining_ceramic",            "experience_years": 12, "projects_completed": 250,
     "category": "Pool Internal Linings - Ceramic"},

    # ── Commercial ───────────────────────────────────────────────────────────────
    {"service_type": "commercial_pool",           "experience_years": 15, "projects_completed": 45,
     "category": "COMMERCIAL POOL SERVICE"},
    {"service_type": "commercial_spa",            "experience_years": 15, "projects_completed": 60,
     "category": "COMMERCIAL POOL SERVICE"},
    {"service_type": "commercial_fountain",       "experience_years": 12, "projects_completed": 80,
     "category": "COMMERCIAL POOL SERVICE"},
    {"service_type": "hotel_pool_service",        "experience_years": 12, "projects_completed": 55,
     "category": "COMMERCIAL POOL SERVICE - Hotels of Cyprus"},

    # ── Specialty ─────────────────────────────────────────────────────────────────
    {"service_type": "swim_spa",                  "experience_years": 12, "projects_completed": 90,
     "category": "Service, Renovation and Repair - Swim Spas"},
    {"service_type": "waterpark",                 "experience_years": 15, "projects_completed": 8,
     "category": "Service, Renovation and Repair - Waterparks"},
    {"service_type": "cooling_heating",           "experience_years": 12, "projects_completed": 200,
     "category": "Service, Renovation and Repair - Cooling and Heating"},
    {"service_type": "rock_features",             "experience_years": 12, "projects_completed": 120,
     "category": "Service, Renovation and Repair - Reconstituted Rock Features"},
    {"service_type": "bar_and_stools",            "experience_years": 12, "projects_completed": 75,
     "category": "Service, Renovation and Repair - Bar and Stools"},

    # ── Renovation ───────────────────────────────────────────────────────────────
    {"service_type": "renovation_basic",          "experience_years": 12, "projects_completed": 350,
     "category": "Service, Renovation and Repair"},
    {"service_type": "renovation_complete",       "experience_years": 12, "projects_completed": 150,
     "category": "Service, Renovation and Repair"},
]

# Images per service type — 5 minimum, matched to service content
SERVICE_IMAGES = {
    "maintenance_weekly":        ["/images/maintenance/weekly_1.jpg", "/images/maintenance/weekly_2.jpg",
                                   "/images/maintenance/weekly_3.jpg", "/images/maintenance/weekly_4.jpg",
                                   "/images/maintenance/weekly_5.jpg"],
    "maintenance_comprehensive": ["/images/maintenance/comp_1.jpg", "/images/maintenance/comp_2.jpg",
                                   "/images/maintenance/comp_3.jpg", "/images/maintenance/comp_4.jpg",
                                   "/images/maintenance/comp_5.jpg"],
    "maintenance_daily":         ["/images/maintenance/daily_1.jpg", "/images/maintenance/daily_2.jpg",
                                   "/images/maintenance/daily_3.jpg", "/images/maintenance/daily_4.jpg",
                                   "/images/maintenance/daily_5.jpg"],
    "construction_small":        ["/images/construction/small_1.jpg", "/images/construction/small_2.jpg",
                                   "/images/construction/small_3.jpg", "/images/construction/small_4.jpg",
                                   "/images/construction/small_5.jpg"],
    "construction_medium":       ["/images/construction/medium_1.jpg", "/images/construction/medium_2.jpg",
                                   "/images/construction/medium_3.jpg", "/images/construction/medium_4.jpg",
                                   "/images/construction/medium_5.jpg"],
    "construction_large":        ["/images/construction/large_1.jpg", "/images/construction/large_2.jpg",
                                   "/images/construction/large_3.jpg", "/images/construction/large_4.jpg",
                                   "/images/construction/large_5.jpg"],
    "pool_overflow":             ["/images/pool_types/overflow_1.jpg", "/images/pool_types/overflow_2.jpg",
                                   "/images/pool_types/overflow_3.jpg", "/images/pool_types/overflow_4.jpg",
                                   "/images/pool_types/overflow_5.jpg"],
    "pool_skimmer":              ["/images/pool_types/skimmer_1.jpg", "/images/pool_types/skimmer_2.jpg",
                                   "/images/pool_types/skimmer_3.jpg", "/images/pool_types/skimmer_4.jpg",
                                   "/images/pool_types/skimmer_5.jpg"],
    "pool_infinity":             ["/images/pool_types/infinity_1.jpg", "/images/pool_types/infinity_2.jpg",
                                   "/images/pool_types/infinity_3.jpg", "/images/pool_types/infinity_4.jpg",
                                   "/images/pool_types/infinity_5.jpg"],
    "lining_liner":              ["/images/linings/liner_1.jpg", "/images/linings/liner_2.jpg",
                                   "/images/linings/liner_3.jpg", "/images/linings/liner_4.jpg",
                                   "/images/linings/liner_5.jpg"],
    "lining_mosaic":             ["/images/linings/mosaic_1.jpg", "/images/linings/mosaic_2.jpg",
                                   "/images/linings/mosaic_3.jpg", "/images/linings/mosaic_4.jpg",
                                   "/images/linings/mosaic_5.jpg"],
    "lining_ceramic":            ["/images/linings/ceramic_1.jpg", "/images/linings/ceramic_2.jpg",
                                   "/images/linings/ceramic_3.jpg", "/images/linings/ceramic_4.jpg",
                                   "/images/linings/ceramic_5.jpg"],
    "commercial_pool":           ["/images/commercial/pool_1.jpg", "/images/commercial/pool_2.jpg",
                                   "/images/commercial/pool_3.jpg", "/images/commercial/pool_4.jpg",
                                   "/images/commercial/pool_5.jpg"],
    "commercial_spa":            ["/images/commercial/spa_1.jpg", "/images/commercial/spa_2.jpg",
                                   "/images/commercial/spa_3.jpg", "/images/commercial/spa_4.jpg",
                                   "/images/commercial/spa_5.jpg"],
    "commercial_fountain":       ["/images/commercial/fountain_1.jpg", "/images/commercial/fountain_2.jpg",
                                   "/images/commercial/fountain_3.jpg", "/images/commercial/fountain_4.jpg",
                                   "/images/commercial/fountain_5.jpg"],
    "hotel_pool_service":        ["/images/commercial/hotel_1.jpg", "/images/commercial/hotel_2.jpg",
                                   "/images/commercial/hotel_3.jpg", "/images/commercial/hotel_4.jpg",
                                   "/images/commercial/hotel_5.jpg"],
    "swim_spa":                  ["/images/specialty/swim_spa_1.jpg", "/images/specialty/swim_spa_2.jpg",
                                   "/images/specialty/swim_spa_3.jpg", "/images/specialty/swim_spa_4.jpg",
                                   "/images/specialty/swim_spa_5.jpg"],
    "waterpark":                 ["/images/specialty/waterpark_1.jpg", "/images/specialty/waterpark_2.jpg",
                                   "/images/specialty/waterpark_3.jpg", "/images/specialty/waterpark_4.jpg",
                                   "/images/specialty/waterpark_5.jpg"],
    "cooling_heating":           ["/images/specialty/heating_1.jpg", "/images/specialty/heating_2.jpg",
                                   "/images/specialty/heating_3.jpg", "/images/specialty/heating_4.jpg",
                                   "/images/specialty/heating_5.jpg"],
    "rock_features":             ["/images/specialty/rock_1.jpg", "/images/specialty/rock_2.jpg",
                                   "/images/specialty/rock_3.jpg", "/images/specialty/rock_4.jpg",
                                   "/images/specialty/rock_5.jpg"],
    "bar_and_stools":            ["/images/specialty/bar_1.jpg", "/images/specialty/bar_2.jpg",
                                   "/images/specialty/bar_3.jpg", "/images/specialty/bar_4.jpg",
                                   "/images/specialty/bar_5.jpg"],
    "renovation_basic":          ["/images/renovation/basic_1.jpg", "/images/renovation/basic_2.jpg",
                                   "/images/renovation/basic_3.jpg", "/images/renovation/basic_4.jpg",
                                   "/images/renovation/basic_5.jpg"],
    "renovation_complete":       ["/images/renovation/complete_1.jpg", "/images/renovation/complete_2.jpg",
                                   "/images/renovation/complete_3.jpg", "/images/renovation/complete_4.jpg",
                                   "/images/renovation/complete_5.jpg"],
}

# ── Batch Runner ────────────────────────────────────────────────────────────────

def run_batch():
    total_ads = len(SERVICES) * len(LOCATIONS)
    print("=" * 90)
    print("🚀 BAZARAKI SYSTEM v4.1 — FULL CATALOG BATCH GENERATION")
    print(f"   Date      : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Services  : {len(SERVICES)} categories  |  Locations: {len(LOCATIONS)}  |  Total: {total_ads} ads")
    print("=" * 90)

    system = BazarakiMasterSystemV4()
    results   = []
    approved  = 0
    rejected  = 0
    needs_rev = 0

    last_category = None

    for svc in SERVICES:
        cat = svc.get("category", "")
        if cat != last_category:
            print(f"\n── {cat} {'─' * (60 - len(cat))}")
            last_category = cat

        for location in LOCATIONS:
            service_type = svc["service_type"]
            images = SERVICE_IMAGES.get(service_type, SERVICE_IMAGES["maintenance_weekly"])

            try:
                package = system.generate_complete_ad_package(
                    service_type=service_type,
                    location=location,
                    experience_years=svc["experience_years"],
                    projects_completed=svc["projects_completed"],
                    images=images,
                )

                status = package.status or "UNKNOWN"
                if status == "APPROVED":   approved  += 1
                elif status == "REJECTED": rejected  += 1
                else:                      needs_rev += 1

                results.append({
                    "category":            cat,
                    "service_type":        service_type,
                    "location":            location,
                    "status":              status,
                    "title":               package.title,
                    "description":         package.description or package.master_prompt_description or "",
                    "price_recommended":   getattr(package, "recommended_price", 0),
                    "price_base":          getattr(package, "base_price", 0),
                    "quality_score":       getattr(package, "quality_score", 0),
                    "master_prompt_score": getattr(package, "master_prompt_score", 0),
                    "master_prompt_level": getattr(package, "master_prompt_level", ""),
                    "predicted_ctr":       getattr(package, "predicted_ctr", 0),
                    "predicted_conversion":getattr(package, "predicted_conversion", 0),
                    "success_probability": getattr(package, "success_probability", 0),
                    "image_quality_score": getattr(package, "image_verification_score", 0),
                    "images_verified":     getattr(package, "images_verified_count", 0),
                })

                icon = "✅" if status == "APPROVED" else ("❌" if status == "REJECTED" else "⚠️ ")
                print(f"  {icon} {service_type:28s} | {location:9s} | {status:10s} | "
                      f"Quality:{package.quality_score:.0f}% | €{package.recommended_price:>9,.0f}")

            except Exception as e:
                print(f"  ❌ ERROR {service_type} / {location}: {e}")
                needs_rev += 1
                results.append({
                    "category": cat, "service_type": service_type,
                    "location": location, "status": "ERROR", "error": str(e),
                })

    # ── Summary ─────────────────────────────────────────────────────────────────
    print()
    print("=" * 90)
    print("📊 BATCH SUMMARY")
    print(f"   Total Generated   : {total_ads}")
    print(f"   ✅ Approved       : {approved}  ({approved/total_ads*100:.0f}%)")
    print(f"   ⚠️  Needs Revision : {needs_rev}  ({needs_rev/total_ads*100:.0f}%)")
    print(f"   ❌ Rejected       : {rejected}  ({rejected/total_ads*100:.0f}%)")
    print("=" * 90)

    # ── Save results ─────────────────────────────────────────────────────────────
    out = "/tmp/bazaraki_v4_batch_results.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "system_version": "4.1",
            "summary": {
                "total": total_ads, "approved": approved,
                "needs_revision": needs_rev, "rejected": rejected,
            },
            "ads": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Results saved to {out}")

    # ── Ready-to-post ads by category ────────────────────────────────────────────
    approved_ads = [r for r in results if r.get("status") == "APPROVED"]
    if approved_ads:
        print(f"\n{'=' * 90}")
        print(f"📋 {len(approved_ads)} ADS READY TO POST ON BAZARAKI")
        print(f"{'=' * 90}")

        current_cat = None
        for i, ad in enumerate(approved_ads, 1):
            if ad.get("category") != current_cat:
                current_cat = ad.get("category", "")
                print(f"\n── {current_cat}")
            print(f"  [{i:3d}] {ad['title']}")
            print(f"        Location : {ad['location'].title()}, Cyprus")
            print(f"        Price    : €{ad['price_recommended']:,.0f}")
            print(f"        Quality  : {ad['quality_score']:.0f}% | MP Score: {ad['master_prompt_score']:.0f}% ({ad.get('master_prompt_level','')})")
            if ad.get("description"):
                preview = ad["description"][:180].replace("\n", " ")
                print(f"        Preview  : {preview}…")

    return results


if __name__ == "__main__":
    run_batch()
