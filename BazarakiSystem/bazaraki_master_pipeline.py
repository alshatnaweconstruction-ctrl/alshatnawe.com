#!/usr/bin/env python3
"""
BAZARAKI MASTER PIPELINE v5.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Integrates:
  1. Master Prompt Engine  — bilingual, compliance-checked, human-tone ads
  2. Bazaraki XML Format   — structured output ready for platform upload
  3. BazarakiSystem v4.0   — pricing engine, category mapping, quality gates

Output: bazaraki_new.xml — drop-in upload file for Bazaraki

Usage:
  python3 bazaraki_master_pipeline.py
  python3 bazaraki_master_pipeline.py --services pool      # pool ads only
  python3 bazaraki_master_pipeline.py --services trades    # trade ads only
  python3 bazaraki_master_pipeline.py --location paphos    # one location
  python3 bazaraki_master_pipeline.py --limit 10           # first N ads
"""

import json
import os
import sys
import argparse
import hashlib
import shutil
import urllib.request
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

REPO_BASE   = "https://raw.githubusercontent.com/alshatnaweconstruction-ctrl/alshatnawe.com/main"
LOCAL_BASE  = Path("/home/claude/alshatnawe.com")
OUTPUT_XML  = LOCAL_BASE / "bazaraki_new.xml"
OUTPUT_JSON = Path("/tmp/bazaraki_pipeline_output.json")
PHONE       = "+35795553931"
WHATSAPP    = "+35795553931"
NOW         = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── District / Rubric mappings ─────────────────────────────────────────────────

DISTRICT = {
    "paphos":   "5713",
    "limassol": "269",
    "larnaca":  "426",
    "nicosia":  "5",
}

# Bazaraki rubric IDs confirmed from existing XML + form inspection
RUBRIC = {
    "Pools maintenance":              "2167",
    "Pool construction":              "2168",
    "Pool renovation":                "2169",
    "General construction":           "3026",
    "Plasterboard / Drywall":         "3027",
    "Interior renovation":            "3028",
    "Tiling":                         "3031",
    "Painting":                       "312",
    "Electricians":                   "2175",
    "Plumbers":                       "2176",
    "Gardeners / Landscaping":        "2172",
    "Handymen":                       "2173",
    "Builders & General Contracting": "3026",
}

# Language attr: 10=Greek, 20=English
BILINGUAL = "10,20"

# ── Service catalogue ─────────────────────────────────────────────────────────
# Each entry defines one unique service ad.
# Images: list of GitHub paths relative to repo root (ad-XXX/0N.jpg)
# Price: real Cyprus 2026 market price (int EUR) or 0 for "upon enquiry"

SERVICES = [

    # ════════════════════════════════════════════════════════
    # POOL SERVICES — 23 unique services × up to 4 locations
    # ════════════════════════════════════════════════════════

    # ── Weekly maintenance ──────────────────────────────────
    {
        "external_id_prefix": "POOL-MW",
        "service_type": "pool_weekly_maintenance",
        "bazaraki_category": "Pools maintenance",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 189, "limassol": 181, "larnaca": 159, "nicosia": 168},
        "image_folder": "maintenance/weekly",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Weekly swimming pool maintenance",
            "SERVICES_INCLUDED": "Water chemistry testing and balancing, surface skimming, vacuuming pool floor and walls, brushing tiles and waterline, filter backwash, pump and equipment inspection, chemical dosing, monthly written report",
            "CUSTOMER_TYPE": "Homeowners, villa owners, holiday-let landlords, property managers",
            "PROPERTY_TYPE": "Residential villas, apartments with pools, holiday rental properties",
            "SPECIAL_FEATURES": "All chemicals and equipment included in the weekly price",
            "UNIQUE_ANGLE": "Maintenance convenience — owner never needs to think about the pool",
            "PRICING_NOTE": "Fixed weekly rate, all chemicals included",
        }
    },

    # ── Comprehensive maintenance ───────────────────────────
    {
        "external_id_prefix": "POOL-MC",
        "service_type": "pool_comprehensive_maintenance",
        "bazaraki_category": "Pools maintenance",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 315, "limassol": 301, "larnaca": 266, "nicosia": 280},
        "image_folder": "maintenance/comp",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Comprehensive monthly pool maintenance",
            "SERVICES_INCLUDED": "Full water analysis, chemical balancing, vacuum, brush, backwash, equipment inspection, light servicing of pump and filter, minor repairs, detailed written condition report",
            "CUSTOMER_TYPE": "Property developers, hotel operators, villa rental managers",
            "PROPERTY_TYPE": "Residential villas, boutique hotels, holiday rental complexes",
            "SPECIAL_FEATURES": "Detailed condition report and minor repairs included",
            "UNIQUE_ANGLE": "Full accountability — detailed written report every visit",
            "PRICING_NOTE": "Monthly fixed fee",
        }
    },

    # ── Daily / commercial maintenance ─────────────────────
    {
        "external_id_prefix": "POOL-MD",
        "service_type": "pool_daily_maintenance",
        "bazaraki_category": "Pools maintenance",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 945, "limassol": 903, "larnaca": 798, "nicosia": 840},
        "image_folder": "maintenance/daily",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Daily commercial pool maintenance",
            "SERVICES_INCLUDED": "Daily water testing and chemical dosing, skimming, vacuuming, filter check, equipment log, regulatory compliance record-keeping",
            "CUSTOMER_TYPE": "Hotel operators, apartment complex owners, leisure centre managers",
            "PROPERTY_TYPE": "Hotels, apartment complexes, health clubs, leisure facilities",
            "SPECIAL_FEATURES": "Regulatory compliance records maintained on every visit",
            "UNIQUE_ANGLE": "Commercial compliance — daily records for health authority requirements",
            "PRICING_NOTE": "Monthly contract, daily visits",
        }
    },

    # ── Pool construction — small ───────────────────────────
    {
        "external_id_prefix": "POOL-CS",
        "service_type": "pool_construction_small",
        "bazaraki_category": "Pool construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 18900, "limassol": 18060, "larnaca": 15960, "nicosia": 16800},
        "image_folder": "construction/small",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Small swimming pool construction (up to 25 m²)",
            "SERVICES_INCLUDED": "Excavation and earthworks, reinforced concrete shell, plumbing and circulation system, filtration installation, waterproofing, tile or mosaic finish, commissioning",
            "CUSTOMER_TYPE": "Homeowners, villa owners, property developers",
            "PROPERTY_TYPE": "Residential gardens, private villas, terraces",
            "SPECIAL_FEATURES": "Complete turnkey construction including all structural and finishing work",
            "UNIQUE_ANGLE": "Project coordination — one contractor from excavation to filled pool",
            "PRICING_NOTE": "From price depending on site conditions and finish selected",
        }
    },

    # ── Pool construction — medium ──────────────────────────
    {
        "external_id_prefix": "POOL-CM",
        "service_type": "pool_construction_medium",
        "bazaraki_category": "Pool construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 31500, "limassol": 30100, "larnaca": 26600, "nicosia": 28000},
        "image_folder": "construction/medium",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Medium swimming pool construction (25–50 m²)",
            "SERVICES_INCLUDED": "Excavation, reinforced concrete shell, full plumbing and filtration system, LED lighting, waterproofing, ceramic or mosaic finish, equipment room setup, commissioning",
            "CUSTOMER_TYPE": "Homeowners, property developers, boutique hotel owners",
            "PROPERTY_TYPE": "Private villas, residential developments, small hotels",
            "SPECIAL_FEATURES": "LED lighting and equipment room included in scope",
            "UNIQUE_ANGLE": "Full structural integrity — engineer-supervised reinforced shell",
            "PRICING_NOTE": "From price depending on ground conditions and finish",
        }
    },

    # ── Pool construction — large ───────────────────────────
    {
        "external_id_prefix": "POOL-CL",
        "service_type": "pool_construction_large",
        "bazaraki_category": "Pool construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 63000, "limassol": 60200, "larnaca": 53200, "nicosia": 56000},
        "image_folder": "construction/large",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Large swimming pool construction (50 m² and above)",
            "SERVICES_INCLUDED": "Full site survey, excavation, engineer-designed reinforced concrete shell, commercial-grade filtration, full automation system, LED and underwater lighting, mosaic or ceramic finish, pool cover provision, commissioning",
            "CUSTOMER_TYPE": "Property developers, hotel groups, large villa owners",
            "PROPERTY_TYPE": "Hotels, luxury villas, residential developments, leisure facilities",
            "SPECIAL_FEATURES": "Engineer-designed structure, commercial-grade filtration, full automation",
            "UNIQUE_ANGLE": "Specialist capability for large-scale residential and commercial pools",
            "PRICING_NOTE": "Quotation after site survey — scope and ground conditions variable",
        }
    },

    # ── Overflow pool ───────────────────────────────────────
    {
        "external_id_prefix": "POOL-OV",
        "service_type": "pool_overflow",
        "bazaraki_category": "Pool construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 42000, "limassol": 40100, "larnaca": 35400, "nicosia": 37300},
        "image_folder": "pool_types/overflow",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Overflow swimming pool construction",
            "SERVICES_INCLUDED": "Overflow gutter design and construction, balance tank, high-capacity circulation system, reinforced concrete shell, waterproofing, tile or mosaic finish, automation, commissioning",
            "CUSTOMER_TYPE": "Luxury villa owners, boutique hotel operators, property developers",
            "PROPERTY_TYPE": "Luxury villas, boutique hotels, high-end residential developments",
            "SPECIAL_FEATURES": "Overflow gutter system with balance tank — achieves seamless water-level finish",
            "UNIQUE_ANGLE": "Specialist overflow design — technically demanding, visually distinctive",
            "PRICING_NOTE": "From price — overflow system adds engineering complexity",
        }
    },

    # ── Infinity pool ───────────────────────────────────────
    {
        "external_id_prefix": "POOL-INF",
        "service_type": "pool_infinity",
        "bazaraki_category": "Pool construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 52500, "limassol": 50100, "larnaca": 44300, "nicosia": 46600},
        "image_folder": "pool_types/infinity",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Infinity edge swimming pool construction",
            "SERVICES_INCLUDED": "Infinity wall engineering and construction, catch basin, dual-pump circulation, reinforced concrete shell, waterproofing, mosaic finish, LED lighting, full automation, commissioning",
            "CUSTOMER_TYPE": "Luxury villa owners, boutique hotels, architects, property developers",
            "PROPERTY_TYPE": "Hillside villas, seafront properties, luxury hotels",
            "SPECIAL_FEATURES": "Infinity wall with catch basin — creates the visual disappearing-edge effect",
            "UNIQUE_ANGLE": "Technically complex — specialist design required for site-specific infinity edge",
            "PRICING_NOTE": "Quotation after site survey — infinity edge is site-specific",
        }
    },

    # ── Skimmer pool ────────────────────────────────────────
    {
        "external_id_prefix": "POOL-SK",
        "service_type": "pool_skimmer",
        "bazaraki_category": "Pool construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 21000, "limassol": 20100, "larnaca": 17700, "nicosia": 18700},
        "image_folder": "pool_types/skimmer",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Skimmer swimming pool construction",
            "SERVICES_INCLUDED": "Skimmer system design and installation, concrete shell, plumbing and filtration, waterproofing, tile or liner finish, commissioning",
            "CUSTOMER_TYPE": "Homeowners, property developers, landlords",
            "PROPERTY_TYPE": "Residential gardens, private villas, apartments",
            "SPECIAL_FEATURES": "Cost-effective proven technology — most widely used pool type in Cyprus",
            "UNIQUE_ANGLE": "Reliable skimmer system — lower running cost than overflow",
            "PRICING_NOTE": "From price — most cost-effective pool construction option",
        }
    },

    # ── Liner lining ────────────────────────────────────────
    {
        "external_id_prefix": "POOL-LN",
        "service_type": "pool_liner",
        "bazaraki_category": "Pool renovation",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 3150, "limassol": 3010, "larnaca": 2660, "nicosia": 2800},
        "image_folder": "linings/liner",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Swimming pool liner installation and replacement",
            "SERVICES_INCLUDED": "Removal of existing liner, shell inspection and minor crack repair, new PVC liner supply and fitting, water refill coordination",
            "CUSTOMER_TYPE": "Homeowners with existing pools, landlords, property managers",
            "PROPERTY_TYPE": "Residential pools requiring liner replacement or upgrade",
            "SPECIAL_FEATURES": "Shell inspection included — identifies structural issues before relining",
            "UNIQUE_ANGLE": "Cost-effective pool resurfacing — fraction of full renovation cost",
            "PRICING_NOTE": "From price depending on pool size and liner grade selected",
        }
    },

    # ── Mosaic lining ───────────────────────────────────────
    {
        "external_id_prefix": "POOL-MOS",
        "service_type": "pool_mosaic",
        "bazaraki_category": "Pool renovation",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 8400, "limassol": 8030, "larnaca": 7100, "nicosia": 7460},
        "image_folder": "linings/mosaic",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Swimming pool mosaic tiling and resurfacing",
            "SERVICES_INCLUDED": "Removal of existing surface, structural repair where needed, waterproofing membrane, mosaic tile supply and installation, grouting and finishing, water refill coordination",
            "CUSTOMER_TYPE": "Luxury villa owners, hotel operators, property investors",
            "PROPERTY_TYPE": "Luxury residential pools, hotel pools, high-end renovation projects",
            "SPECIAL_FEATURES": "Mosaic finish improves both appearance and surface durability",
            "UNIQUE_ANGLE": "High-end finish — mosaic is the premium resurfacing option for Cyprus pools",
            "PRICING_NOTE": "From price depending on pool size and mosaic selected",
        }
    },

    # ── Ceramic lining ──────────────────────────────────────
    {
        "external_id_prefix": "POOL-CER",
        "service_type": "pool_ceramic",
        "bazaraki_category": "Pool renovation",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 5250, "limassol": 5020, "larnaca": 4430, "nicosia": 4660},
        "image_folder": "linings/ceramic",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Swimming pool ceramic tile installation and resurfacing",
            "SERVICES_INCLUDED": "Removal of existing surface, waterproofing membrane, pool-grade ceramic tile supply and installation, grouting and sealing, water refill coordination",
            "CUSTOMER_TYPE": "Homeowners, landlords, property developers",
            "PROPERTY_TYPE": "Residential pools, villas, holiday rental properties",
            "SPECIAL_FEATURES": "Pool-grade ceramic — UV-resistant, chemical-resistant, slip-resistant finish",
            "UNIQUE_ANGLE": "Durable mid-range resurfacing — better than liner, more affordable than mosaic",
            "PRICING_NOTE": "From price depending on pool size and tile selected",
        }
    },

    # ── Commercial pool ─────────────────────────────────────
    {
        "external_id_prefix": "POOL-COM",
        "service_type": "pool_commercial",
        "bazaraki_category": "Pools maintenance",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 1260, "limassol": 1205, "larnaca": 1064, "nicosia": 1120},
        "image_folder": "commercial/pool",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Commercial swimming pool maintenance contract",
            "SERVICES_INCLUDED": "Daily or tri-weekly water testing, chemical dosing, vacuum, brush, filter management, equipment inspection, regulatory compliance log, written service records",
            "CUSTOMER_TYPE": "Hotel operators, apartment complex owners, leisure centre managers, building management companies",
            "PROPERTY_TYPE": "Hotels, apartment complexes, health clubs, tourist accommodation",
            "SPECIAL_FEATURES": "Regulatory compliance log maintained — ready for health authority inspection",
            "UNIQUE_ANGLE": "Commercial accountability — documented records for every service visit",
            "PRICING_NOTE": "Monthly contract — rate depends on pool size and visit frequency",
        }
    },

    # ── Spa / jacuzzi maintenance ───────────────────────────
    {
        "external_id_prefix": "POOL-SPA",
        "service_type": "pool_spa",
        "bazaraki_category": "Pools maintenance",
        "locations": ["paphos", "limassol"],
        "prices": {"paphos": 420, "limassol": 401},
        "image_folder": "commercial/spa",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Spa and jacuzzi maintenance service",
            "SERVICES_INCLUDED": "Water chemistry balancing, jet system inspection, filter cleaning, sanitiser dosing, surface clean, equipment check",
            "CUSTOMER_TYPE": "Villa owners, hotel operators, wellness centre managers",
            "PROPERTY_TYPE": "Villas with spa, hotels, wellness facilities",
            "SPECIAL_FEATURES": "Jet system and heater inspection included on every visit",
            "UNIQUE_ANGLE": "Specialist spa care — different chemistry requirements to standard pools",
            "PRICING_NOTE": "Monthly rate — visit frequency depends on usage",
        }
    },

    # ── Basic renovation ────────────────────────────────────
    {
        "external_id_prefix": "POOL-RB",
        "service_type": "pool_renovation_basic",
        "bazaraki_category": "Pool renovation",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 3937, "limassol": 3762, "larnaca": 3325, "nicosia": 3500},
        "image_folder": "maintenance/weekly",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Basic swimming pool renovation",
            "SERVICES_INCLUDED": "Drain and clean, crack repair, waterproof coating, surface repaint or re-render, equipment check, refill",
            "CUSTOMER_TYPE": "Homeowners with older pools, landlords preparing for rental season",
            "PROPERTY_TYPE": "Residential pools showing surface wear, older villas",
            "SPECIAL_FEATURES": "Completed within 5–7 working days",
            "UNIQUE_ANGLE": "Fast turnaround — pool back in use within one week",
            "PRICING_NOTE": "From price depending on pool condition and size",
        }
    },

    # ── Complete renovation ─────────────────────────────────
    {
        "external_id_prefix": "POOL-RC",
        "service_type": "pool_renovation_complete",
        "bazaraki_category": "Pool renovation",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 31500, "limassol": 30100, "larnaca": 26600, "nicosia": 28000},
        "image_folder": "construction/medium",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Complete swimming pool renovation",
            "SERVICES_INCLUDED": "Full drain and structural inspection, crack and shell repair, new waterproofing membrane, new tile or mosaic surface, replacement of filtration system, new LED lighting, automation system update, refill and commissioning",
            "CUSTOMER_TYPE": "Property investors, hotel owners, villa owners preparing for sale or rental",
            "PROPERTY_TYPE": "Older residential pools, hotel pools due for full refurbishment",
            "SPECIAL_FEATURES": "Structural inspection report provided before work begins",
            "UNIQUE_ANGLE": "Property value — complete renovation adds measurable resale value",
            "PRICING_NOTE": "Quotation after inspection — scope depends on existing condition",
        }
    },

    # ════════════════════════════════════════════════════════
    # TRADE SERVICES — 18 unique services × up to 4 locations
    # ════════════════════════════════════════════════════════

    # ── Interior painting ───────────────────────────────────
    {
        "external_id_prefix": "SV-PAINT-INT",
        "service_type": "painting_interior",
        "bazaraki_category": "Painting",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-001",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Interior wall and ceiling painting",
            "SERVICES_INCLUDED": "Surface preparation, filling cracks and imperfections, primer coat, two finish coats, masking and protection of floors and fittings, cleanup",
            "CUSTOMER_TYPE": "Homeowners, landlords, property managers, businesses",
            "PROPERTY_TYPE": "Apartments, houses, offices, shops, commercial properties",
            "SPECIAL_FEATURES": "Surface preparation and crack filling included",
            "UNIQUE_ANGLE": "Clean finish without disruption — protection of all surfaces before work begins",
            "PRICING_NOTE": "Price upon enquiry depending on property size and condition",
        }
    },

    # ── Exterior painting ───────────────────────────────────
    {
        "external_id_prefix": "SV-PAINT-EXT",
        "service_type": "painting_exterior",
        "bazaraki_category": "Painting",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-002",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Exterior facade and wall painting",
            "SERVICES_INCLUDED": "Surface wash and preparation, crack and render repair, weather-resistant primer, two coats exterior paint, masking, cleanup",
            "CUSTOMER_TYPE": "Homeowners, landlords, property managers, commercial property owners",
            "PROPERTY_TYPE": "Villas, apartment buildings, commercial premises",
            "SPECIAL_FEATURES": "Weather-resistant paint formulation suitable for Cyprus climate",
            "UNIQUE_ANGLE": "Property protection — exterior coating prevents moisture ingress and deterioration",
            "PRICING_NOTE": "Price upon enquiry depending on facade area and access requirements",
        }
    },

    # ── Tiling ──────────────────────────────────────────────
    {
        "external_id_prefix": "SV-TILE",
        "service_type": "tiling",
        "bazaraki_category": "Tiling",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-003",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Floor and wall tiling for homes and commercial properties",
            "SERVICES_INCLUDED": "Surface preparation and levelling, adhesive bed, tile supply coordination or customer tile use, installation, grouting, sealing, cleanup",
            "CUSTOMER_TYPE": "Homeowners, developers, landlords, businesses",
            "PROPERTY_TYPE": "Kitchens, bathrooms, living areas, terraces, commercial floors",
            "SPECIAL_FEATURES": "Surface levelling included — prevents hollow spots and cracked tiles",
            "UNIQUE_ANGLE": "Correct substrate preparation — the step most often skipped that causes future failure",
            "PRICING_NOTE": "Price upon enquiry depending on area, tile type and surface condition",
        }
    },

    # ── Plasterboard / Drywall ──────────────────────────────
    {
        "external_id_prefix": "SV-DRY",
        "service_type": "plasterboard",
        "bazaraki_category": "Plasterboard / Drywall",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 75, "limassol": 70, "larnaca": 65, "nicosia": 68},
        "image_folder": "ad-sv-004",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Plasterboard partition walls and drywall installation",
            "SERVICES_INCLUDED": "Metal stud framing, plasterboard installation, joint taping and filling, corner bead, ready-to-paint finish",
            "CUSTOMER_TYPE": "Homeowners, businesses, landlords, office fit-out contractors",
            "PROPERTY_TYPE": "Homes, offices, commercial premises requiring internal partition or lining",
            "SPECIAL_FEATURES": "Ready-to-paint finish — no additional plastering required",
            "UNIQUE_ANGLE": "Faster than block wall — partition complete in days, not weeks",
            "PRICING_NOTE": "From €65/m² depending on partition specification and location",
        }
    },

    # ── General renovation ──────────────────────────────────
    {
        "external_id_prefix": "SV-REN",
        "service_type": "renovation_interior",
        "bazaraki_category": "Interior renovation",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-005",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Interior renovation and refurbishment",
            "SERVICES_INCLUDED": "Scope defined per project — typically includes partition walls, flooring, tiling, painting, kitchen or bathroom upgrades, plumbing and electrical coordination",
            "CUSTOMER_TYPE": "Homeowners, landlords preparing for rental, property investors",
            "PROPERTY_TYPE": "Apartments, houses, villas requiring partial or full refurbishment",
            "SPECIAL_FEATURES": "Single contractor coordination — no need to manage multiple trades separately",
            "UNIQUE_ANGLE": "Project coordination — one point of contact for all renovation trades",
            "PRICING_NOTE": "Price upon enquiry after site assessment — scope varies significantly",
        }
    },

    # ── General construction ────────────────────────────────
    {
        "external_id_prefix": "SV-BUILD",
        "service_type": "general_construction",
        "bazaraki_category": "General construction",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-006",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "General construction works for homes and villas",
            "SERVICES_INCLUDED": "Extensions, structural additions, concrete works, block laying, render, roof works — scope defined per project",
            "CUSTOMER_TYPE": "Homeowners, property developers, villa owners",
            "PROPERTY_TYPE": "Residential villas, houses, small commercial properties",
            "SPECIAL_FEATURES": "Structural and finishing work from one contractor",
            "UNIQUE_ANGLE": "Project control — structural and finishing phases coordinated by one team",
            "PRICING_NOTE": "Price upon enquiry after site visit and scope review",
        }
    },

    # ── Plumbing ────────────────────────────────────────────
    {
        "external_id_prefix": "SV-PLUMB",
        "service_type": "plumbing",
        "bazaraki_category": "Plumbers",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-007",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Plumbing installation and repair",
            "SERVICES_INCLUDED": "Pipe installation and repair, bathroom and kitchen plumbing, hot water system installation, leak detection and repair, drainage works",
            "CUSTOMER_TYPE": "Homeowners, landlords, property managers, developers",
            "PROPERTY_TYPE": "Residential properties, apartments, villas, commercial premises",
            "SPECIAL_FEATURES": "Leak detection included before any repair work begins",
            "UNIQUE_ANGLE": "Diagnosis first — fault identified before any materials are ordered",
            "PRICING_NOTE": "Price upon enquiry depending on scope and access",
        }
    },

    # ── Electrical ──────────────────────────────────────────
    {
        "external_id_prefix": "SV-ELEC",
        "service_type": "electrical",
        "bazaraki_category": "Electricians",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-008",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Electrical installation and repair",
            "SERVICES_INCLUDED": "Electrical installation for new builds and renovations, fault finding and repair, consumer unit upgrades, lighting installation, socket and switch installation, EV charger installation",
            "CUSTOMER_TYPE": "Homeowners, developers, landlords, businesses",
            "PROPERTY_TYPE": "Residential properties, commercial premises, new builds",
            "SPECIAL_FEATURES": "Fault finding diagnostic service before repair — no guesswork",
            "UNIQUE_ANGLE": "Correct diagnosis — electrical faults identified precisely before any work",
            "PRICING_NOTE": "Price upon enquiry depending on scope of work",
        }
    },

    # ── Gardening / landscaping ─────────────────────────────
    {
        "external_id_prefix": "SV-GARD",
        "service_type": "gardening",
        "bazaraki_category": "Gardeners / Landscaping",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-009",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Garden maintenance and landscaping",
            "SERVICES_INCLUDED": "Lawn mowing, hedge and shrub trimming, tree pruning, irrigation system check, plant care, garden cleanup and waste removal",
            "CUSTOMER_TYPE": "Homeowners, landlords, property managers, holiday villa owners",
            "PROPERTY_TYPE": "Residential gardens, villa grounds, commercial outdoor areas",
            "SPECIAL_FEATURES": "Irrigation system check included in maintenance visits",
            "UNIQUE_ANGLE": "Regular maintenance contract — garden stays presentable without owner involvement",
            "PRICING_NOTE": "Price upon enquiry depending on garden size and visit frequency",
        }
    },

    # ── Handyman ────────────────────────────────────────────
    {
        "external_id_prefix": "SV-HANDY",
        "service_type": "handyman",
        "bazaraki_category": "Handymen",
        "locations": ["paphos", "limassol", "larnaca", "nicosia"],
        "prices": {"paphos": 0, "limassol": 0, "larnaca": 0, "nicosia": 0},
        "image_folder": "ad-sv-010",
        "negotiable": True,

        "master_prompt": {
            "SERVICE": "Handyman and property maintenance service",
            "SERVICES_INCLUDED": "Minor repairs, door and window adjustments, furniture assembly, shelving installation, minor plumbing and electrical fixes, general property maintenance tasks",
            "CUSTOMER_TYPE": "Homeowners, landlords, property managers, businesses",
            "PROPERTY_TYPE": "Residential properties, offices, shops, holiday rental properties",
            "SPECIAL_FEATURES": "Broad trade capability — multiple small jobs completed in one visit",
            "UNIQUE_ANGLE": "Convenience — all minor repairs handled in a single scheduled visit",
            "PRICING_NOTE": "Hourly rate or fixed price per job upon enquiry",
        }
    },
]

# ── Master Prompt Content Generator ──────────────────────────────────────────

def generate_description(service: dict, location: str, price: int) -> str:
    """
    Applies the Bazaraki Master Prompt framework to produce a
    bilingual (Greek + English) description that is:
    - Compliant (no invented facts, no fake urgency)
    - Natural human tone
    - Structured: opening → value → scope → customers → process → CTA
    """
    mp = service["master_prompt"]
    svc_name      = mp["SERVICE"]
    inclusions    = mp["SERVICES_INCLUDED"]
    customers     = mp["CUSTOMER_TYPE"]
    properties    = mp["PROPERTY_TYPE"]
    unique_angle  = mp.get("UNIQUE_ANGLE", "")
    pricing_note  = mp.get("PRICING_NOTE", "Price upon enquiry")
    loc_title     = location.capitalize()

    # Split inclusions into bullet list
    incl_items = [i.strip() for i in inclusions.split(",")]
    incl_el    = "\n".join(f"- {i}" for i in incl_items)
    incl_el_gr = "\n".join(f"- {i}" for i in incl_items)   # kept English in bullets for accuracy

    price_str_en = f"From €{price:,}" if price > 0 else pricing_note
    price_str_gr = f"Από €{price:,}" if price > 0 else "Τιμή μετά από επικοινωνία"

    location_area_en = f"{loc_title}, Cyprus"
    location_area_gr = {
        "Paphos": "Πάφος", "Limassol": "Λεμεσός",
        "Larnaca": "Λάρνακα", "Nicosia": "Λευκωσία",
    }.get(loc_title, loc_title)

    # ── Greek service name mapping ──────────────────────────
    GREEK_SERVICE_NAMES = {
        "Weekly swimming pool maintenance": "Εβδομαδιαία συντήρηση πισίνας",
        "Monthly swimming pool maintenance": "Μηνιαία συντήρηση πισίνας",
        "Daily swimming pool maintenance": "Καθημερινή συντήρηση πισίνας",
        "Comprehensive swimming pool maintenance": "Ολοκληρωμένη συντήρηση πισίνας",
        "Custom swimming pool construction": "Κατασκευή πισίνας κατά παραγγελία",
        "Swimming pool construction": "Κατασκευή πισίνας",
        "Concrete swimming pool construction": "Κατασκευή πισίνας από μπετόν",
        "Infinity pool construction": "Κατασκευή πισίνας infinity",
        "Overflow pool construction": "Κατασκευή πισίνας overflow",
        "Mosaic pool finish": "Ψηφιδωτή επένδυση πισίνας",
        "Ceramic tile pool finish": "Κεραμικές πλακέτες πισίνας",
        "Pool liner installation": "Τοποθέτηση liner πισίνας",
        "Swimming pool renovation": "Ανακαίνιση πισίνας",
        "Pool waterproofing": "Υδρομόνωση πισίνας",
        "Pool filter and pump installation": "Εγκατάσταση φίλτρου και αντλίας πισίνας",
        "Pool heating system installation": "Εγκατάσταση συστήματος θέρμανσης πισίνας",
        "Pool lighting installation": "Εγκατάσταση φωτισμού πισίνας",
        "Pool deck and surround construction": "Κατασκευή αποβάθρας πισίνας",
        "Swim spa installation": "Εγκατάσταση swim spa",
        "Rock pool construction": "Κατασκευή πισίνας από πέτρα",
        "Water feature installation": "Εγκατάσταση υδατοστοιχείων",
        "Pool bar installation": "Εγκατάσταση bar πισίνας",
        "Commercial pool construction": "Κατασκευή εμπορικής πισίνας",
        "Hotel pool maintenance": "Συντήρηση πισίνας ξενοδοχείου",
        "Waterpark construction": "Κατασκευή υδατοπάρκου",
        "Plasterboard and drywall installation": "Τοποθέτηση γυψοσανίδας",
        "Interior plastering": "Εσωτερικός σοβατισμός",
        "Ceiling and partition installation": "Τοποθέτηση οροφής και χωρισμάτων",
        "Interior renovation and refurbishment": "Εσωτερική ανακαίνιση",
        "Floor tiling and wall tiling": "Τοποθέτηση πλακιδίων δαπέδου και τοίχου",
        "Interior and exterior painting": "Εσωτερική και εξωτερική βαφή",
        "General building and construction": "Γενικές οικοδομικές εργασίες",
        "Electrical installation and wiring": "Ηλεκτρολογικές εγκαταστάσεις",
        "Plumbing installation and repair": "Υδραυλικές εγκαταστάσεις και επισκευές",
        "Garden design and landscaping": "Σχεδιασμός κήπου και τοπιογραφία",
        "General handyman services": "Γενικές εργασίες επισκευής",
    }
    svc_name_gr = GREEK_SERVICE_NAMES.get(svc_name, svc_name)

    # ── Greek description ──────────────────────────────────
    greek = f"""{svc_name_gr} για {customers.split(',')[0].lower()} και {customers.split(',')[1].strip().lower() if ',' in customers else 'ιδιοκτήτες ακινήτων'} που χρειάζονται αξιόπιστο αποτέλεσμα.

Αναλαμβάνουμε ολόκληρη τη διαδικασία ώστε να διασφαλίσουμε σωστή εκτέλεση και καθαρό αποτέλεσμα χωρίς περιττά προβλήματα.

Περιλαμβάνεται:
{incl_el_gr}

Κατάλληλο για: {customers}.

Διαδικασία: Επικοινωνία → αξιολόγηση απαιτήσεων → επιθεώρηση χώρου → προσφορά → εκτέλεση → παράδοση.

Περιοχή εξυπηρέτησης: {location_area_gr} και γύρω περιοχές.

Τιμή: {price_str_gr}.

Στείλτε την τοποθεσία και τις βασικές σας απαιτήσεις μέσω Bazaraki για να συζητήσουμε το έργο."""

    # ── English description ────────────────────────────────
    english = f"""{svc_name} for {customers.lower()} who need a correctly delivered result without unnecessary complications.

We manage the entire process to ensure proper execution and a clean outcome at every stage.

Scope of work:
{incl_el}

Suitable for: {customers}.
Property types: {properties}.

Process: Enquiry → requirements review → site assessment → quotation → service delivery → handover.

Service area: {location_area_en} and surrounding areas.

{price_str_en}.

Send the property location and basic requirements through Bazaraki to discuss the project."""

    return f"{greek.strip()}\n\n{'—' * 3}\n\n{english.strip()}"


def get_image_urls(service: dict) -> list:
    """
    Returns GitHub raw URLs for this service's images.
    Looks in local folder first; falls back to ad-sv-* or ad-* folders.
    """
    folder = service.get("image_folder", "")
    urls   = []

    # folder can be:
    # (a) "ad-sv-001" or "ad-002" → direct subfolder under LOCAL_BASE
    # (b) "maintenance/weekly"    → images are in LOCAL_BASE/images/maintenance/
    #                               with prefix "weekly_" e.g. weekly_1.jpg
    # (c) "construction/small"    → images in LOCAL_BASE/images/construction/ prefix "small_"

    # Case (a): direct folder
    local_folder = LOCAL_BASE / folder
    if local_folder.exists() and local_folder.is_dir():
        imgs = sorted(local_folder.glob("*.jpg"))[:5]
        if imgs:
            for img in imgs:
                rel = img.relative_to(LOCAL_BASE)
                urls.append(f"{REPO_BASE}/{rel}")
            return urls

    # Case (b)/(c): "category/type" pattern → look in images/category/ for type_*.jpg
    if "/" in folder:
        parts = folder.split("/", 1)
        category, prefix = parts[0], parts[1]
        img_dir = LOCAL_BASE / "images" / category
        if img_dir.exists():
            # Match files starting with prefix_ (e.g. "weekly_1.jpg")
            imgs = sorted(img_dir.glob(f"{prefix}_*.jpg"))[:5]
            if not imgs:
                # Also try without underscore prefix (e.g. just any jpg in that folder)
                imgs = sorted(img_dir.glob("*.jpg"))[:5]
            if imgs:
                for img in imgs:
                    rel = img.relative_to(LOCAL_BASE)
                    urls.append(f"{REPO_BASE}/{rel}")
                return urls

    # Try entire images/folder path directly
    images_folder = LOCAL_BASE / "images" / folder
    if images_folder.exists() and images_folder.is_dir():
        imgs = sorted(images_folder.glob("*.jpg"))[:5]
        if imgs:
            for img in imgs:
                rel = img.relative_to(LOCAL_BASE)
                urls.append(f"{REPO_BASE}/{rel}")
            return urls

    # Fallback: use ad-sv-001 images
    fallback = LOCAL_BASE / "ad-sv-001"
    if fallback.exists():
        imgs = sorted(fallback.glob("*.jpg"))[:5]
        for img in imgs:
            rel = img.relative_to(LOCAL_BASE)
            urls.append(f"{REPO_BASE}/{rel}")

    return urls


# ── XML Builder ───────────────────────────────────────────────────────────────

def build_xml(ads: list) -> ElementTree:
    root_el = Element("root")

    for ad in ads:
        item = SubElement(root_el, "list-item")

        def add(tag, text):
            el = SubElement(item, tag)
            el.text = str(text) if text is not None else ""

        add("last_update", NOW)
        add("external_id",  ad["external_id"])
        add("status",       "active")
        add("rubric",       ad["rubric"])
        add("district",     ad["district"])
        add("title",        ad["title"])
        add("description",  ad["description"])
        add("price",        f"{ad['price']:.2f}" if ad["price"] > 0 else "0.00")
        add("negotiable_price", "1" if ad["negotiable"] else "0")
        add("exchange",     "0")
        add("phone_hide",   "0")
        add("chosen_phone", PHONE)
        add("whatsapp",     WHATSAPP)
        add("disallow_chat","0")

        images_el = SubElement(item, "images")
        for url in ad["images"]:
            img_el = SubElement(images_el, "list-item")
            img_el.text = url

        attrs_el = SubElement(item, "attrs")
        lang_el  = SubElement(attrs_el, "language")
        lang_el.text = BILINGUAL

        SubElement(item, "geometry")

    tree = ElementTree(root_el)
    indent(tree, space="  ")
    return tree


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(filter_services=None, filter_location=None, limit=None):
    print("\n" + "═"*60)
    print("  BAZARAKI MASTER PIPELINE v5.0")
    print("  Master Prompt + XML Format + BazarakiSystem v4.0")
    print("═"*60)

    ads_out  = []
    ads_json = []
    counter  = 0
    skipped  = 0

    for svc in SERVICES:
        # Filter by service group
        if filter_services == "pool" and not any(
            k in svc["external_id_prefix"] for k in ["POOL"]
        ):
            skipped += 1
            continue
        if filter_services == "trades" and svc["external_id_prefix"].startswith("POOL"):
            skipped += 1
            continue

        for loc in svc["locations"]:
            if filter_location and loc != filter_location:
                continue
            if limit and counter >= limit:
                break

            price    = svc["prices"].get(loc, 0)
            ext_id   = f"{svc['external_id_prefix']}-{loc[:3].upper()}"
            title    = build_title(svc, loc)
            desc     = generate_description(svc, loc, price)
            images   = get_image_urls(svc)
            rubric   = RUBRIC.get(svc["bazaraki_category"], "3026")
            district = DISTRICT.get(loc, "5713")

            if not images:
                print(f"  ⚠  No images found for {ext_id} — skipping")
                skipped += 1
                continue

            ad = {
                "external_id": ext_id,
                "title":       title,
                "description": desc,
                "rubric":      rubric,
                "district":    district,
                "price":       price,
                "negotiable":  svc.get("negotiable", True),
                "images":      images,
                "service_type": svc["service_type"],
                "location":    loc,
                "category":    svc["bazaraki_category"],
            }

            ads_out.append(ad)
            ads_json.append({k: v for k, v in ad.items()})
            counter += 1

            price_str = f"€{price:,}" if price > 0 else "upon enquiry"
            print(f"  [{counter:03d}] {ext_id:25s} | {loc:8s} | {price_str:15s} | {title[:45]}")

        if limit and counter >= limit:
            break

    print(f"\n{'─'*60}")
    print(f"  ✓  Generated : {counter} ads")
    print(f"  ✗  Skipped   : {skipped}")
    print(f"{'─'*60}")

    # Write XML
    tree = build_xml(ads_out)
    with open(OUTPUT_XML, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)
    print(f"  XML  → {OUTPUT_XML}")

    # Write JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(ads_json, f, indent=2, ensure_ascii=False)
    print(f"  JSON → {OUTPUT_JSON}")
    print("═"*60 + "\n")

    return ads_out


def build_title(svc: dict, location: str) -> str:
    """Build a compliant title: Service + qualifier + location."""
    mp       = svc["master_prompt"]
    svc_name = mp["SERVICE"]
    loc_title = location.capitalize()
    loc_map  = {
        "Paphos": "Paphos", "Limassol": "Limassol",
        "Larnaca": "Larnaca", "Nicosia": "Nicosia",
    }
    loc_display = loc_map.get(loc_title, loc_title)

    # Clean title: Service in Location
    # Keep under 80 chars
    title = f"{svc_name} in {loc_display}"
    if len(title) > 80:
        title = title[:77] + "..."
    return title


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bazaraki Master Pipeline v5.0")
    parser.add_argument("--services",  choices=["pool", "trades", "all"], default="all")
    parser.add_argument("--location",  choices=["paphos", "limassol", "larnaca", "nicosia"])
    parser.add_argument("--limit",     type=int)
    args = parser.parse_args()

    run_pipeline(
        filter_services=None if args.services == "all" else args.services,
        filter_location=args.location,
        limit=args.limit,
    )
