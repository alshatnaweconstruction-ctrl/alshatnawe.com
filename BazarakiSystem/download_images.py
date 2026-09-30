#!/usr/bin/env python3
"""
Download real pool service images from Unsplash for each service category.
Run this script from YOUR OWN MACHINE (not the server).
Uses Unsplash free photo source — NO images from other Bazaraki ads.
Each image is matched to service content exactly.

Usage:
    python3 download_images.py
    python3 download_images.py --base /path/to/alshatnawe.com/images
"""

import os
import sys
import time
import urllib.request
import urllib.parse
import ssl
import argparse

# SSL context for HTTPS
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

parser = argparse.ArgumentParser()
parser.add_argument("--base", default=None, help="Base images directory")
args, _ = parser.parse_known_args()

# Auto-detect base dir relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = args.base or os.path.join(SCRIPT_DIR, "..", "images")

# Pexels free image search — keyword sets per service type
# Each entry: (folder, filename_prefix, search_keywords_list)
IMAGE_PLAN = [
    # ── Maintenance ──────────────────────────────────────────────────────────
    ("maintenance", "weekly",  [
        "swimming pool cleaning",
        "pool maintenance service",
        "pool technician cleaning",
        "pool skimmer net cleaning",
        "clean blue swimming pool",
    ]),
    ("maintenance", "comp",    [
        "pool equipment maintenance",
        "pool pump filter service",
        "pool chemical testing water",
        "pool technician equipment",
        "swimming pool service professional",
    ]),
    ("maintenance", "daily",   [
        "hotel pool daily maintenance",
        "commercial pool cleaning daily",
        "resort pool service",
        "hotel swimming pool blue",
        "pool vacuum cleaner underwater",
    ]),
    # ── Construction ─────────────────────────────────────────────────────────
    ("construction", "small",  [
        "small backyard swimming pool",
        "compact garden pool construction",
        "small pool build",
        "mini swimming pool blue",
        "private pool backyard small",
    ]),
    ("construction", "medium", [
        "swimming pool construction site",
        "pool building concrete",
        "medium size pool construction",
        "pool under construction",
        "luxury pool construction",
    ]),
    ("construction", "large",  [
        "large swimming pool construction",
        "olympic size pool building",
        "big pool luxury construction",
        "villa large pool",
        "resort pool large blue",
    ]),
    # ── Pool Types ───────────────────────────────────────────────────────────
    ("pool_types", "overflow", [
        "overflow swimming pool",
        "wet edge pool luxury",
        "infinity overflow pool edge",
        "pool overflow water feature",
        "luxury overflow pool Cyprus",
    ]),
    ("pool_types", "skimmer",  [
        "skimmer swimming pool",
        "standard home pool blue",
        "residential skimmer pool",
        "backyard swimming pool clear",
        "family swimming pool summer",
    ]),
    ("pool_types", "infinity", [
        "infinity pool sea view",
        "infinity edge pool luxury",
        "vanishing edge pool sunset",
        "infinity pool Mediterranean",
        "infinity pool blue sky",
    ]),
    # ── Linings ──────────────────────────────────────────────────────────────
    ("linings", "liner",       [
        "vinyl liner pool",
        "pool liner installation blue",
        "swimming pool vinyl liner",
        "pool liner replacement",
        "blue pool vinyl interior",
    ]),
    ("linings", "mosaic",      [
        "mosaic pool tile",
        "glass mosaic swimming pool",
        "pool mosaic tile blue",
        "luxury mosaic pool interior",
        "decorative pool tile mosaic",
    ]),
    ("linings", "ceramic",     [
        "ceramic tile pool",
        "pool ceramic tiles interior",
        "swimming pool tile work",
        "pool tile installation",
        "ceramic pool finish blue",
    ]),
    # ── Commercial ───────────────────────────────────────────────────────────
    ("commercial", "pool",     [
        "commercial swimming pool",
        "hotel resort pool large",
        "public swimming pool",
        "commercial pool blue",
        "resort hotel pool luxury",
    ]),
    ("commercial", "spa",      [
        "commercial spa jacuzzi",
        "luxury spa pool interior",
        "hot tub spa commercial",
        "spa jacuzzi water jets",
        "wellness spa pool blue",
    ]),
    ("commercial", "fountain", [
        "decorative water fountain",
        "pool fountain feature",
        "ornamental fountain water",
        "garden fountain landscape",
        "fountain water feature luxury",
    ]),
    ("commercial", "hotel",    [
        "hotel pool service",
        "resort swimming pool service",
        "hotel pool maintenance",
        "luxury hotel pool blue",
        "resort pool technician",
    ]),
    # ── Specialty ─────────────────────────────────────────────────────────────
    ("specialty", "swim_spa",  [
        "swim spa",
        "swim spa backyard",
        "hydrotherapy swim spa",
        "swim spa exercise",
        "swim spa installation",
    ]),
    ("specialty", "waterpark", [
        "waterpark slides",
        "water park pool",
        "waterpark attractions",
        "water park construction",
        "aqua park water slides",
    ]),
    ("specialty", "heating",   [
        "pool heat pump",
        "swimming pool heating system",
        "pool heater installation",
        "pool heat exchanger",
        "pool temperature control",
    ]),
    ("specialty", "rock",      [
        "pool rock feature",
        "natural rock pool waterfall",
        "reconstituted rock pool",
        "pool waterfall rock",
        "stone feature pool design",
    ]),
    ("specialty", "bar",       [
        "swim up pool bar",
        "pool bar stools",
        "pool bar underwater stools",
        "swim up bar resort",
        "pool bar luxury",
    ]),
    # ── Renovation ───────────────────────────────────────────────────────────
    ("renovation", "basic",    [
        "pool renovation repair",
        "old pool refurbishment",
        "pool resurfacing repair",
        "swimming pool renovation",
        "pool crack repair surface",
    ]),
    ("renovation", "complete", [
        "complete pool renovation",
        "pool complete makeover",
        "pool renovation before after",
        "luxury pool renovation complete",
        "pool redesign renovation",
    ]),
]

# Unsplash source (no API key needed for direct image URLs)
def unsplash_url(query, width=1200, height=800):
    encoded = urllib.parse.quote(query)
    return f"https://source.unsplash.com/featured/{width}x{height}/?{encoded}"

def download_image(url, dest_path, timeout=30):
    """Download image from URL to dest_path."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; PoolServiceBot/1.0)"
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"    ⚠ Too small ({len(data)} bytes) — skipping")
            return False
        with open(dest_path, "wb") as f:
            f.write(data)
        print(f"    ✓ {os.path.basename(dest_path)} ({len(data)//1024}KB)")
        return True
    except Exception as e:
        print(f"    ✗ {url}: {e}")
        return False


def run():
    print("=" * 70)
    print("🏊 POOL SERVICE IMAGE DOWNLOADER")
    print("   Source: Unsplash (free, no license restrictions)")
    print("=" * 70)

    total = 0
    downloaded = 0

    for folder, prefix, keywords in IMAGE_PLAN:
        dest_dir = os.path.join(BASE_DIR, folder)
        os.makedirs(dest_dir, exist_ok=True)
        print(f"\n── {folder}/{prefix}")

        for i, kw in enumerate(keywords, 1):
            dest = os.path.join(dest_dir, f"{prefix}_{i}.jpg")
            if os.path.exists(dest) and os.path.getsize(dest) > 5000:
                print(f"    ✓ {prefix}_{i}.jpg already exists")
                downloaded += 1
                total += 1
                continue

            url = unsplash_url(kw)
            print(f"    [{i}] '{kw}'")
            ok = download_image(url, dest)
            if ok:
                downloaded += 1
            total += 1
            time.sleep(1.2)  # rate-limit

    print()
    print("=" * 70)
    print(f"📊 Downloaded: {downloaded}/{total} images")
    print(f"   Folders: {BASE_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    run()
