#!/usr/bin/env python3
"""
BazarakiSystem v4.0 - Batch Runner
Generates complete ad packages for all services × all locations
English only - Cyprus market - Real prices
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from master_system_v4 import BazarakiMasterSystemV4

# ── Configuration ──────────────────────────────────────────────────────────────

LOCATIONS = ["paphos", "limassol", "larnaca", "nicosia"]

# All service types with experience profile
SERVICES = [
    {"service_type": "maintenance_weekly",        "experience_years": 12, "projects_completed": 400},
    {"service_type": "maintenance_comprehensive",  "experience_years": 12, "projects_completed": 400},
    {"service_type": "maintenance_daily",          "experience_years": 12, "projects_completed": 400},
    {"service_type": "construction_small",         "experience_years": 15, "projects_completed": 280},
    {"service_type": "construction_medium",        "experience_years": 15, "projects_completed": 180},
    {"service_type": "construction_large",         "experience_years": 15, "projects_completed": 80},
    {"service_type": "renovation_basic",           "experience_years": 12, "projects_completed": 350},
    {"service_type": "renovation_complete",        "experience_years": 12, "projects_completed": 150},
]

# Placeholder images per service category (5 minimum required)
SERVICE_IMAGES = {
    "maintenance_weekly":       ["/images/pool_maintenance_1.jpg", "/images/pool_maintenance_2.jpg",
                                  "/images/pool_maintenance_3.jpg", "/images/pool_maintenance_4.jpg",
                                  "/images/pool_maintenance_5.jpg"],
    "maintenance_comprehensive":["/images/pool_comp_1.jpg", "/images/pool_comp_2.jpg",
                                  "/images/pool_comp_3.jpg", "/images/pool_comp_4.jpg",
                                  "/images/pool_comp_5.jpg"],
    "maintenance_daily":        ["/images/pool_daily_1.jpg", "/images/pool_daily_2.jpg",
                                  "/images/pool_daily_3.jpg", "/images/pool_daily_4.jpg",
                                  "/images/pool_daily_5.jpg"],
    "construction_small":       ["/images/pool_build_small_1.jpg", "/images/pool_build_small_2.jpg",
                                  "/images/pool_build_small_3.jpg", "/images/pool_build_small_4.jpg",
                                  "/images/pool_build_small_5.jpg"],
    "construction_medium":      ["/images/pool_build_med_1.jpg", "/images/pool_build_med_2.jpg",
                                  "/images/pool_build_med_3.jpg", "/images/pool_build_med_4.jpg",
                                  "/images/pool_build_med_5.jpg"],
    "construction_large":       ["/images/pool_build_lg_1.jpg", "/images/pool_build_lg_2.jpg",
                                  "/images/pool_build_lg_3.jpg", "/images/pool_build_lg_4.jpg",
                                  "/images/pool_build_lg_5.jpg"],
    "renovation_basic":         ["/images/pool_reno_basic_1.jpg", "/images/pool_reno_basic_2.jpg",
                                  "/images/pool_reno_basic_3.jpg", "/images/pool_reno_basic_4.jpg",
                                  "/images/pool_reno_basic_5.jpg"],
    "renovation_complete":      ["/images/pool_reno_full_1.jpg", "/images/pool_reno_full_2.jpg",
                                  "/images/pool_reno_full_3.jpg", "/images/pool_reno_full_4.jpg",
                                  "/images/pool_reno_full_5.jpg"],
}

# ── Batch Runner ───────────────────────────────────────────────────────────────

def run_batch():
    print("=" * 80)
    print("🚀 BAZARAKI SYSTEM v4.0 - BATCH AD GENERATION")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Services: {len(SERVICES)} | Locations: {len(LOCATIONS)} | Total: {len(SERVICES) * len(LOCATIONS)} ads")
    print("=" * 80)

    system = BazarakiMasterSystemV4()
    results = []
    approved = 0
    rejected = 0
    needs_revision = 0

    for svc in SERVICES:
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

                status = package.status if package.status else "UNKNOWN"
                if status == "APPROVED":
                    approved += 1
                elif status == "REJECTED":
                    rejected += 1
                else:
                    needs_revision += 1

                results.append({
                    "service_type": service_type,
                    "location": location,
                    "status": status,
                    "title": package.title,
                    "description": package.description or getattr(package, "master_prompt_description", "") or "",
                    "price_recommended": getattr(package, "recommended_price", 0),
                    "price_base": getattr(package, "base_price", 0),
                    "quality_score": getattr(package, "quality_score", 0),
                    "master_prompt_score": getattr(package, "master_prompt_score", 0),
                    "master_prompt_level": getattr(package, "master_prompt_level", ""),
                    "predicted_ctr": getattr(package, "predicted_ctr", 0),
                    "predicted_conversion": getattr(package, "predicted_conversion", 0),
                    "success_probability": getattr(package, "success_probability", 0),
                    "gates_passed": int(getattr(package, "quality_score", 0) / 10),
                    "image_quality_score": getattr(package, "image_quality_score", 0),
                })

                icon = "✅" if status == "APPROVED" else ("❌" if status == "REJECTED" else "⚠️")
                print(f"  {icon} {service_type:30s} | {location:10s} | {status:15s} | "
                      f"Quality: {package.quality_score:.0f}% | Price: €{package.recommended_price:.0f}")

            except Exception as e:
                print(f"  ❌ ERROR {service_type} / {location}: {e}")
                needs_revision += 1
                results.append({
                    "service_type": service_type,
                    "location": location,
                    "status": "ERROR",
                    "error": str(e),
                })

    # ── Summary ────────────────────────────────────────────────────────────────
    total = len(SERVICES) * len(LOCATIONS)
    print()
    print("=" * 80)
    print("📊 BATCH SUMMARY")
    print(f"   Total Generated : {total}")
    print(f"   ✅ Approved      : {approved}  ({approved/total*100:.0f}%)")
    print(f"   ⚠️  Needs Revision: {needs_revision}  ({needs_revision/total*100:.0f}%)")
    print(f"   ❌ Rejected      : {rejected}  ({rejected/total*100:.0f}%)")
    print("=" * 80)

    # ── Save results ───────────────────────────────────────────────────────────
    output_path = "/tmp/bazaraki_v4_batch_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "approved": approved,
                "needs_revision": needs_revision,
                "rejected": rejected,
            },
            "ads": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Results saved to {output_path}")

    # ── Print approved ads ready to post ──────────────────────────────────────
    approved_ads = [r for r in results if r.get("status") == "APPROVED"]
    if approved_ads:
        print(f"\n{'=' * 80}")
        print(f"📋 {len(approved_ads)} ADS READY TO POST ON BAZARAKI")
        print(f"{'=' * 80}")
        for i, ad in enumerate(approved_ads, 1):
            print(f"\n[{i}] {ad['title']}")
            print(f"     Service  : {ad['service_type']}")
            print(f"     Location : {ad['location'].title()}, Cyprus")
            print(f"     Price    : €{ad['price_recommended']:.0f}")
            print(f"     Quality  : {ad['quality_score']:.0f}% | Master Prompt: {ad['master_prompt_score']:.0f}% ({ad.get('master_prompt_level','')})")
            print(f"     CTR      : {ad['predicted_ctr']:.2f}% | Conversion: {ad['predicted_conversion']:.2f}%")
            if ad.get("description"):
                desc_preview = ad["description"][:200].replace("\n", " ")
                print(f"     Desc     : {desc_preview}...")

    return results

if __name__ == "__main__":
    run_batch()
