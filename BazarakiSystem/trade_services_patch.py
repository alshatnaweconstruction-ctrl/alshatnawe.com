"""
Trade Services English Description Generator — BazarakiSystem v4.1
Covers: Tiling Services | Renovation Services | Builders / Construction Services

Cyprus 2026 real market pricing (sourced from construx-cyprus.com, interior-design.green):
- Tiling labour:      €18–35/m² (ceramic), €22–45/m² (porcelain/rectified), €35–65/m² (mosaic/natural stone)
- Floor tiling total: €35–80/m² (supply + fit, standard tile)
- Bathroom tiling:    €400–900 per bathroom (labour only)
- Renovation cosmetic:€350–650/m²
- Renovation standard:€650–900/m²
- Renovation premium: €900–1,400+/m²
- New build (residential): €900–1,300/m² depending on spec and location
- Commercial build:   €850–1,600/m²
- Extensions/additions: €700–1,100/m²
- Interior fit-out:   €300–650/m²
- 5% VAT applies (owner-occupier residential renovation)

Location multipliers (same as pool system):
  Paphos ×1.125 | Limassol ×1.075 | Nicosia ×1.0 | Larnaca ×0.95

Bazaraki: English and Greek ONLY — no Arabic.
"""

# ── Service labels ─────────────────────────────────────────────────────────────

TRADE_SERVICE_LABELS = {
    # ── Tiling ──────────────────────────────────────────────────────────────────
    "tiling_floor_ceramic":     "Ceramic Floor Tiling",
    "tiling_floor_porcelain":   "Porcelain Floor Tiling",
    "tiling_bathroom":          "Bathroom Wall & Floor Tiling",
    "tiling_outdoor":           "Outdoor & Terrace Tiling",
    "tiling_mosaic_feature":    "Decorative Mosaic Feature Tiling",
    "tiling_large_format":      "Large-Format Rectified Tile Installation",
    # ── Renovation ──────────────────────────────────────────────────────────────
    "renovation_cosmetic":      "Cosmetic Apartment / Villa Renovation",
    "renovation_standard":      "Standard Full Renovation",
    "renovation_premium":       "Premium Luxury Renovation",
    "renovation_kitchen":       "Kitchen Renovation & Fit-Out",
    "renovation_bathroom":      "Bathroom Renovation & Fit-Out",
    "renovation_commercial":    "Commercial Premises Renovation",
    # ── Builders ────────────────────────────────────────────────────────────────
    "build_residential_new":    "New Residential Build",
    "build_villa":              "Luxury Villa Construction",
    "build_extension":          "Home Extension & Addition",
    "build_commercial":         "Commercial Building Construction",
    "build_fitout":             "Interior Fit-Out & Finishing",
    "build_structural":         "Structural Repairs & Underpinning",
}

# ── Location context (shared with pool system) ────────────────────────────────

TRADE_LOCATION_CONTEXT = {
    "paphos": {
        "market":    "luxury villa, holiday-let and retirement property market",
        "buyers":    "UK, Russian, and Israeli property investors and retirees",
        "stat":      "Paphos is Cyprus's fastest-growing luxury property destination — quality finish directly drives rental yields.",
        "highlight": "In Paphos's villa-rental market, premium finishes can raise your short-let rate by 20–35%.",
        "label":     "Paphos",
    },
    "limassol": {
        "market":    "upscale residential and corporate relocation market",
        "buyers":    "corporate executives, high-net-worth families, and international tenants",
        "stat":      "Limassol property values grew 11% in 2025 — high-quality renovation is the fastest route to maximum resale.",
        "highlight": "Limassol buyers demand European standards — mid-range finishes are immediately penalised at valuation.",
        "label":     "Limassol",
    },
    "larnaca": {
        "market":    "growing residential and investment property market",
        "buyers":    "local families, first-time buyers, and buy-to-let landlords",
        "stat":      "Larnaca's new international airport expansion is accelerating property demand city-wide.",
        "highlight": "Larnaca's rapidly rising rents mean renovation ROI is hitting 6–9% — one of the best in Cyprus.",
        "label":     "Larnaca",
    },
    "nicosia": {
        "market":    "capital city professional and government sector market",
        "buyers":    "government employees, banking and finance professionals, young families",
        "stat":      "Nicosia hosts 70% of Cyprus's commercial office space — commercial fit-out demand is at a 5-year high.",
        "highlight": "In Nicosia's competitive rental market, a freshly renovated property leases 40% faster at 15% higher rent.",
        "label":     "Nicosia",
    },
}

# ── Cyprus 2026 pricing data ────────────────────────────────────────────────────

TRADE_BASE_PRICES = {
    # Tiling (labour + standard tile supply, per m² total)
    "tiling_floor_ceramic":    {"min": 35,    "max": 60,    "unit": "m²",  "note": "ceramic tile supply + fit"},
    "tiling_floor_porcelain":  {"min": 45,    "max": 80,    "unit": "m²",  "note": "porcelain/rectified supply + fit"},
    "tiling_bathroom":         {"min": 400,   "max": 900,   "unit": "bathroom", "note": "full bathroom wall & floor"},
    "tiling_outdoor":          {"min": 30,    "max": 65,    "unit": "m²",  "note": "outdoor/terrace anti-slip"},
    "tiling_mosaic_feature":   {"min": 55,    "max": 120,   "unit": "m²",  "note": "decorative mosaic/natural stone"},
    "tiling_large_format":     {"min": 50,    "max": 95,    "unit": "m²",  "note": "600×600+ rectified, precision levelling"},
    # Renovation (total per m² all-in, excluding structural/permits)
    "renovation_cosmetic":     {"min": 350,   "max": 650,   "unit": "m²",  "note": "cosmetic refresh"},
    "renovation_standard":     {"min": 650,   "max": 900,   "unit": "m²",  "note": "standard full renovation"},
    "renovation_premium":      {"min": 900,   "max": 1400,  "unit": "m²",  "note": "premium/luxury renovation"},
    "renovation_kitchen":      {"min": 4500,  "max": 18000, "unit": "project", "note": "kitchen full fit-out"},
    "renovation_bathroom":     {"min": 2500,  "max": 9000,  "unit": "project", "note": "bathroom full fit-out"},
    "renovation_commercial":   {"min": 300,   "max": 650,   "unit": "m²",  "note": "commercial premises refurbishment"},
    # Builders (per m² for new build / extension)
    "build_residential_new":   {"min": 900,   "max": 1300,  "unit": "m²",  "note": "new residential, standard spec"},
    "build_villa":             {"min": 1100,  "max": 2000,  "unit": "m²",  "note": "luxury villa, high spec"},
    "build_extension":         {"min": 700,   "max": 1100,  "unit": "m²",  "note": "home extension/addition"},
    "build_commercial":        {"min": 850,   "max": 1600,  "unit": "m²",  "note": "commercial building"},
    "build_fitout":            {"min": 300,   "max": 650,   "unit": "m²",  "note": "interior fit-out & finishing"},
    "build_structural":        {"min": 2000,  "max": 15000, "unit": "project", "note": "structural repair/underpinning"},
}

# ── Location multiplier ───────────────────────────────────────────────────────

LOCATION_MULTIPLIERS = {
    "paphos":   1.125,
    "limassol": 1.075,
    "nicosia":  1.0,
    "larnaca":  0.95,
}

def get_trade_price(service_type: str, location: str, experience_years: int = 10, profit_margin: float = 0.38) -> dict:
    """Calculate smart price for trade services."""
    data = TRADE_BASE_PRICES.get(service_type)
    if not data:
        return {"min": 100, "max": 500, "recommended": 300, "unit": "project"}

    loc_mult = LOCATION_MULTIPLIERS.get(location.lower(), 1.0)

    # Experience premium (10+ years → +15%)
    exp_mult = 1.15 if experience_years >= 10 else (1.05 if experience_years >= 5 else 1.0)

    # Season: Oct–Mar is slower (–8%), Apr–Sep peak (+8%)
    import datetime
    month = datetime.datetime.now().month
    season_mult = 1.08 if month in [4, 5, 6, 7, 8, 9] else 0.92

    base_mid = (data["min"] + data["max"]) / 2
    adjusted = base_mid * loc_mult * exp_mult * season_mult
    recommended = round(adjusted / (1 - profit_margin))

    return {
        "min":         round(data["min"] * loc_mult),
        "max":         round(data["max"] * loc_mult * exp_mult),
        "recommended": recommended,
        "unit":        data["unit"],
        "note":        data.get("note", ""),
    }


# ── 9-part description builder ────────────────────────────────────────────────

def _loc(ctx) -> str:
    return TRADE_LOCATION_CONTEXT.get(ctx.get("location", "nicosia").lower(), TRADE_LOCATION_CONTEXT["nicosia"])["label"]

def _lctx(ctx) -> dict:
    return TRADE_LOCATION_CONTEXT.get(ctx.get("location", "nicosia").lower(), TRADE_LOCATION_CONTEXT["nicosia"])

def _yrs(ctx) -> int:
    return ctx.get("experience_years", 10)

def _proj(ctx) -> int:
    return ctx.get("projects_completed", 150)

def _svc(ctx) -> str:
    return ctx.get("service_type", "")


def _hook(ctx) -> str:
    svc = _svc(ctx)
    loc = _loc(ctx)
    yrs = _yrs(ctx)

    hooks = {
        "tiling_floor_ceramic":    f"Precision-laid ceramic tiles, flawless grout lines, zero lippage — professional floor tiling in {loc} by specialists with {yrs}+ years on Cyprus projects.",
        "tiling_floor_porcelain":  f"Rectified porcelain at its finest — razor-sharp edges, perfectly levelled, built to last 30+ years in {loc}'s climate.",
        "tiling_bathroom":         f"Your bathroom transformation starts here — full wall and floor tiling in {loc} completed on time, on budget, zero mess left behind.",
        "tiling_outdoor":          f"Outdoor tiles that handle Cyprus heat and heavy rain without cracking, lifting, or staining — professional terrace tiling in {loc}.",
        "tiling_mosaic_feature":   f"Bespoke mosaic feature walls and decorative inlays that stop visitors in their tracks — artisan tiling craftsmanship in {loc}.",
        "tiling_large_format":     f"900mm × 900mm and larger porcelain slabs, precision-levelled to within 2mm — large-format tiling done right in {loc}.",
        "renovation_cosmetic":     f"Fresh paint, new floors, modern fixtures — your property looks brand new in weeks, not months, without the premium price tag. {loc} renovation specialists.",
        "renovation_standard":     f"Kitchen replaced, bathrooms transformed, electrics and plumbing updated — full apartment renovation in {loc} delivered on a fixed timeline and fixed price.",
        "renovation_premium":      f"Italian marble, custom joinery, smart-home integration — premium renovation in {loc} that commands top rental yields and maximum resale value.",
        "renovation_kitchen":      f"A kitchen that actually works for your family and impresses every guest — complete kitchen renovation in {loc} from design to final tile.",
        "renovation_bathroom":     f"The bathroom you've always wanted, installed to German engineering standards — complete bathroom renovation in {loc} with zero hidden extras.",
        "renovation_commercial":   f"First impressions close clients — your commercial space in {loc} transformed quickly and cleanly, minimising business downtime.",
        "build_residential_new":   f"Your home, built exactly to your specifications on your land in {loc} — transparent fixed-price residential construction with no surprises.",
        "build_villa":             f"A custom luxury villa in {loc} built to the highest European standards — the property you've dreamed of, delivered on schedule.",
        "build_extension":         f"More space, more value — professional home extension in {loc} that matches your existing structure perfectly and adds immediate equity.",
        "build_commercial":        f"Commercial premises built to your exact operational needs in {loc} — on time, compliant, and ready for business.",
        "build_fitout":            f"Shell to showroom in weeks — complete interior fit-out in {loc} for residential or commercial spaces, from flooring to ceilings.",
        "build_structural":        f"Cracks, subsidence, or structural failure in {loc}? Our engineers diagnose, design, and fix it permanently — no guesswork, no patch-work.",
    }
    return hooks.get(svc, f"Professional {TRADE_SERVICE_LABELS.get(svc, 'trade services')} in {loc} — {yrs}+ years building Cyprus properties.")


def _problem(ctx) -> str:
    svc = _svc(ctx)
    loc = _loc(ctx)

    problems = {
        "tiling_floor_ceramic":    f"Most tiling failures in {loc} — hollow tiles, cracked grout, uneven surfaces — happen when contractors skip the prep work and rush the layout.",
        "tiling_floor_porcelain":  f"Porcelain demands perfect sub-floor preparation and precision levelling. Without it, lippage and cracking appear within months, costing twice the original job.",
        "tiling_bathroom":         f"A bathroom tiled by an inexperienced contractor means rising damp, falling tiles, and mould within two years — common and costly in {loc}'s humid summers.",
        "tiling_outdoor":          f"The wrong tile, the wrong adhesive, or improper drainage — and {loc}'s summer heat and winter rain will lift your terrace in a single season.",
        "tiling_mosaic_feature":   f"Mosaic work is unforgiving — a single misaligned row or inconsistent grout joint destroys the entire pattern. Most contractors in {loc} avoid it for that reason.",
        "tiling_large_format":     f"Large-format tiles require specialist levelling systems, dedicated adhesives, and experienced installers — standard tilers in {loc} often refuse these projects.",
        "renovation_cosmetic":     f"A quick coat of paint and new light fittings sounds simple — but without the right surface prep and materials, fresh work in {loc} degrades within 18 months.",
        "renovation_standard":     f"The biggest risk in a full renovation in {loc} is hidden scope creep — jobs that start at €40,000 regularly balloon to €65,000 with contractors who under-quote to win work.",
        "renovation_premium":      f"Premium renovation in {loc} requires perfect coordination: architects, tradespeople, and suppliers all timed precisely — a single delay cascades through every other trade.",
        "renovation_kitchen":      f"A poorly planned kitchen in {loc} costs you twice — once to build it, and again within five years when the layout fails and cabinets delaminate in the Mediterranean heat.",
        "renovation_bathroom":     f"Waterproofing failures are the number-one bathroom problem in {loc} — water migrates behind tiles undetected for years before catastrophic damage appears.",
        "renovation_commercial":   f"Commercial renovation downtime directly costs revenue — every extra day your {loc} business is closed for works is a day of lost trading.",
        "build_residential_new":   f"New builds in {loc} frequently stall over planning permissions, material delays, and contractor changes — cost overruns of 20–35% are common without strong project management.",
        "build_villa":             f"Luxury villa construction in {loc} requires material sourcing from across Europe, bespoke sub-contractors, and zero tolerance for quality compromise — most builders aren't equipped.",
        "build_extension":         f"An extension that doesn't match your existing structure — wrong ceiling height, mismatched render, different floor levels — immediately signals poor workmanship to future buyers.",
        "build_commercial":        f"Commercial construction in {loc} requires compliance with strict municipal codes — a single planning error can halt your project for months and cost tens of thousands.",
        "build_fitout":            f"Fit-out delivered late means your business launch is delayed — every week of overrun in {loc} costs money before you've earned a single euro.",
        "build_structural":        f"Structural problems in {loc} worsen exponentially — what costs €3,000 to fix today often costs €15,000–30,000 if left untreated for another season.",
    }
    return problems.get(svc, f"Construction quality in {loc} varies dramatically — the wrong contractor choice costs time, money, and structural integrity.")


def _authority(ctx) -> str:
    yrs = _yrs(ctx)
    proj = _proj(ctx)
    loc = _loc(ctx)
    # Build a district list that always includes all 4 without duplicating the current location
    all_districts = ["Paphos", "Limassol", "Larnaca", "Nicosia"]
    other_districts = [d for d in all_districts if d != loc]
    district_list = loc + ", " + ", ".join(other_districts[:2]) + " and " + other_districts[2]
    return (
        f"We have built, renovated, and tiled across {district_list} for {yrs}+ years — "
        f"{proj}+ completed projects, all to Eurocode and Cyprus Building Permit standards. "
        f"Our team holds current CY construction licences and carries full public liability insurance."
    )


def _solution(ctx) -> str:
    svc = _svc(ctx)
    loc = _loc(ctx)
    price = get_trade_price(svc, ctx.get("location", "nicosia"), _yrs(ctx))
    unit = price["unit"]
    recommended = price["recommended"]
    min_p = price["min"]
    max_p = price["max"]

    per_unit_svcs = {
        "tiling_floor_ceramic", "tiling_floor_porcelain", "tiling_outdoor",
        "tiling_mosaic_feature", "tiling_large_format",
        "renovation_cosmetic", "renovation_standard", "renovation_premium",
        "renovation_commercial", "build_residential_new", "build_villa",
        "build_extension", "build_commercial", "build_fitout",
    }

    if svc in per_unit_svcs:
        price_line = f"Pricing from €{min_p}/m² to €{max_p}/m² depending on scope and materials — transparent quote before any work begins."
    else:
        price_line = f"Fixed-price projects starting from €{min_p:,} — full scope, materials, and labour included in your quote."

    solutions = {
        "tiling_floor_ceramic":    f"We supply premium Spanish and Italian ceramic tiles (10–20mm calibrated) and lay them to British Standard BS5385 tolerances in {loc}. {price_line} Minimum order 20m².",
        "tiling_floor_porcelain":  f"Rectified porcelain from €45/m² including supply and installation in {loc} — we use T-Lock levelling clips for zero lippage on every job. {price_line}",
        "tiling_bathroom":         f"Complete bathroom tiling in {loc}: strip, waterproof membrane, full wall and floor tile installation. €400–900 per bathroom depending on size and tile specification. {price_line}",
        "tiling_outdoor":          f"Anti-slip R11/R12-rated outdoor tiles for {loc} terraces, balconies, and pool surrounds — properly bedded in flexible cement mortar with expansion joints. {price_line}",
        "tiling_mosaic_feature":   f"Hand-laid glass mosaic, natural stone, and penny-tile features in {loc} — we match historic patterns or create contemporary bespoke designs. {price_line}",
        "tiling_large_format":     f"900×900, 1200×600, and 1200×1200 rectified porcelain slabs installed in {loc} using specialist levelling systems and full-bed adhesive — no hollow spots. {price_line}",
        "renovation_cosmetic":     f"Full cosmetic refresh in {loc}: skim-coat and paint all surfaces, replace flooring, update fixtures and fittings, new internal doors — property market-ready in 2–4 weeks. {price_line}",
        "renovation_standard":     f"Full standard renovation in {loc}: new kitchen, new bathrooms, rewire, replumb, new flooring throughout — fixed price agreed before work starts. {price_line}",
        "renovation_premium":      f"Premium renovation in {loc}: Italian marble, custom joinery, underfloor heating, smart lighting — project-managed from design to snagging. {price_line}",
        "renovation_kitchen":      f"Complete kitchen renovation in {loc}: demolition, new units (German or Italian), integrated appliances, worktop, tiling, electrics, plumbing. €4,500–18,000 depending on spec.",
        "renovation_bathroom":     f"Full bathroom renovation in {loc}: strip to structure, tanking membrane, new suite, full tiling, towel rail, extraction — 5-year workmanship guarantee. €2,500–9,000 per bathroom.",
        "renovation_commercial":   f"Commercial renovation in {loc}: offices, retail units, restaurants, clinics — all works permitted, certified, and completed with minimum disruption to neighbouring businesses. {price_line}",
        "build_residential_new":   f"New residential build in {loc}: architectural drawings, permits, structural works, MEP (mechanical, electrical, plumbing), finishes — full turnkey delivery. {price_line}",
        "build_villa":             f"Custom luxury villa construction in {loc}: private architect coordination, premium materials, custom pool and landscaping included as an option — from concept to keys. {price_line}",
        "build_extension":         f"Home extension in {loc}: structural engineer calculations, planning permit management, matching finishes, integrated electrics and plumbing — seamless with your existing property. {price_line}",
        "build_commercial":        f"Commercial building in {loc}: reinforced concrete frame, masonry, steel, MEP systems, municipality compliance — built for your business operational requirements. {price_line}",
        "build_fitout":            f"Interior fit-out in {loc}: raised floors, suspended ceilings, partition walls, MEP first-fix and second-fix, painting, tiling, joinery — ready for occupancy. {price_line}",
        "build_structural":        f"Structural diagnosis, design, and repair in {loc}: crack injection, underpinning, beam replacement, shear walls — engineered solution with full calculations and sign-off. Fixed-price quote after inspection.",
    }
    return solutions.get(svc, f"Professional {TRADE_SERVICE_LABELS.get(svc, 'trade services')} in {loc}. {price_line}")


def _proof(ctx) -> str:
    proj = _proj(ctx)
    yrs = _yrs(ctx)
    loc = _loc(ctx)
    svc = _svc(ctx)

    if "tiling" in svc:
        return (f"We have tiled {proj}+ projects across Cyprus — from private bathrooms to hotel lobbies. "
                f"Every job comes with a 5-year workmanship guarantee covering adhesion failure, grout cracking, and hollow tiles.")
    elif "renovation" in svc:
        return (f"{proj}+ renovations completed across Cyprus in {yrs} years. "
                f"We provide a photographic handover report, 2-year defects liability period, and a 10-year structural guarantee on all permitted works.")
    else:
        return (f"{proj}+ construction projects delivered in Cyprus over {yrs} years. "
                f"Every build is certified by a registered Cyprus structural engineer, submitted to the District Administration, and handed over with a full file of as-built drawings.")


def _vision(ctx) -> str:
    svc = _svc(ctx)
    loc = _loc(ctx)
    lctx = _lctx(ctx)

    visions = {
        "tiling_floor_ceramic":    f"Imagine walking on perfectly level, gleaming ceramic floors every morning — in your {loc} home or investment property, adding lasting value for years.",
        "tiling_floor_porcelain":  f"Porcelain that looks as sharp on day 3,000 as day one — your {loc} property finishes that make buyers stop and look twice.",
        "tiling_bathroom":         f"A bathroom that works, looks stunning, and holds its value for the next owner — that's what professional tiling in {loc} delivers.",
        "tiling_outdoor":          f"A {loc} terrace that withstands 40°C summers and winter storms without lifting, cracking, or fading — made for the Mediterranean climate.",
        "tiling_mosaic_feature":   f"A mosaic feature wall that becomes the conversation piece of every room — bespoke artisan work only a handful of {loc} specialists can deliver.",
        "tiling_large_format":     f"Those magazine-perfect large-format tile floors — now achievable in your {loc} home, installed by specialists who do this every week.",
        "renovation_cosmetic":     f"A property that looks and feels brand new, commands higher rent, and sells faster in {loc}'s {lctx['market']}.",
        "renovation_standard":     f"A fully renovated home in {loc} where everything works, nothing leaks, and the finish impresses every viewer — raising its value by 15–25%.",
        "renovation_premium":      f"A premium {loc} property that sits at the very top of the market — the one buyers remember and pay a premium to secure.",
        "renovation_kitchen":      f"The kitchen that makes you want to cook, entertain, and show off your {loc} home — completed in 3–5 weeks from first fix to final tile.",
        "renovation_bathroom":     f"A spa-quality bathroom in your {loc} home — the one feature that every buyer and every tenant notices first.",
        "renovation_commercial":   f"Your {loc} business premises reflecting the quality of your brand — clean, professional, and ready to impress clients from day one.",
        "build_residential_new":   f"Your family home, built exactly as you designed it, on your own land in {loc} — the single biggest investment you'll ever get right the first time.",
        "build_villa":             f"A {loc} luxury villa that earns strong rental yields in season and holds its capital value through any market cycle.",
        "build_extension":         f"The extra bedroom, the home office, the open-plan living space — your {loc} property extended to match how your life has grown.",
        "build_commercial":        f"Purpose-built commercial space in {loc} where every square metre is optimised for your business — not adapted from someone else's floor plan.",
        "build_fitout":            f"Walk into your {loc} space fully fitted, fully compliant, and ready for business — no snagging list, no outstanding works.",
        "build_structural":        f"Complete peace of mind — your {loc} property structurally sound, certified by engineers, and protecting your family or tenants for decades.",
    }
    return visions.get(svc, f"A finished {loc} property you're proud of, built to last, and valued accordingly in the market.")


def _cta(ctx) -> str:
    svc = _svc(ctx)
    loc = _loc(ctx)

    if "tiling" in svc:
        return (f"📐 Send us your floor plan or photos for a free, detailed quote within 24 hours. "
                f"Call or WhatsApp today — serving {loc} and all Cyprus.")
    elif "renovation" in svc:
        return (f"🏠 Book your free on-site assessment in {loc} today — we'll give you a fixed price with a written guarantee. "
                f"Limited project slots available — contact us to secure yours.")
    else:
        return (f"🏗️ Contact us for a free site visit and detailed construction quote in {loc}. "
                f"We'll walk you through the full scope, timeline, and fixed price — no obligation, no vague estimates.")


def build_trade_description(ctx: dict) -> str:
    """
    Build a complete 9-part English Bazaraki ad description for a trade service.
    ctx keys: service_type, location, experience_years, projects_completed
    """
    parts = [
        _hook(ctx),
        "",
        _problem(ctx),
        "",
        _authority(ctx),
        "",
        _solution(ctx),
        "",
        "✅ OUR TRACK RECORD:",
        _proof(ctx),
        "",
        _vision(ctx),
        "",
        _cta(ctx),
        "",
        "─" * 50,
        "📍 Based in Cyprus | Covering all districts",
        "🔑 Licensed & Insured | All permits handled",
        "⭐ 5-Year Workmanship Guarantee on all projects",
    ]
    return "\n".join(parts)


def build_trade_title(ctx: dict) -> str:
    """Build a compelling Bazaraki ad title for a trade service."""
    svc = ctx.get("service_type", "")
    loc = _loc(ctx)
    yrs = _yrs(ctx)
    price = get_trade_price(svc, ctx.get("location", "nicosia"), yrs)
    unit = price["unit"]
    min_p = price["min"]

    titles = {
        "tiling_floor_ceramic":    f"Professional Ceramic Floor Tiling in {loc} — From €{min_p}/m² | {yrs}+ Years",
        "tiling_floor_porcelain":  f"Rectified Porcelain Tile Installation in {loc} — From €{min_p}/m²",
        "tiling_bathroom":         f"Bathroom Tiling Specialists {loc} — Full Wall & Floor | Free Quote",
        "tiling_outdoor":          f"Outdoor & Terrace Tiling in {loc} — Anti-Slip, Weather-Proof | €{min_p}/m²",
        "tiling_mosaic_feature":   f"Decorative Mosaic Tiling {loc} — Bespoke Feature Walls & Floors",
        "tiling_large_format":     f"Large-Format Porcelain Tile Installation {loc} — 900mm+ Slabs | Specialists",
        "renovation_cosmetic":     f"Cosmetic Apartment Renovation {loc} — From €{min_p}/m² | Ready in 3 Weeks",
        "renovation_standard":     f"Full Apartment & Villa Renovation {loc} — Fixed Price from €{min_p}/m²",
        "renovation_premium":      f"Premium Luxury Renovation {loc} — Italian Finishes | From €{min_p}/m²",
        "renovation_kitchen":      f"Kitchen Renovation & Fit-Out {loc} — Complete from €{min_p:,} | {yrs}+ Years",
        "renovation_bathroom":     f"Full Bathroom Renovation {loc} — Waterproofed & Tiled | From €{min_p:,}",
        "renovation_commercial":   f"Commercial Premises Renovation {loc} — Fast, Compliant, Fixed Price",
        "build_residential_new":   f"New Residential Build {loc} — From €{min_p}/m² | Turnkey | All Permits",
        "build_villa":             f"Luxury Villa Construction {loc} — Custom Design | From €{min_p}/m²",
        "build_extension":         f"Home Extension & Addition {loc} — From €{min_p}/m² | Permit Managed",
        "build_commercial":        f"Commercial Building Construction {loc} — From €{min_p}/m² | Licensed",
        "build_fitout":            f"Interior Fit-Out {loc} — Shell to Move-In Ready | From €{min_p}/m²",
        "build_structural":        f"Structural Repairs & Underpinning {loc} — Engineer-Designed | Permanent Fix",
    }
    return titles.get(svc, f"Professional {TRADE_SERVICE_LABELS.get(svc, 'Trade Services')} in {loc} — {yrs}+ Years Cyprus Experience")


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        {"service_type": "tiling_floor_porcelain", "location": "paphos",   "experience_years": 12, "projects_completed": 380},
        {"service_type": "renovation_standard",    "location": "limassol", "experience_years": 15, "projects_completed": 210},
        {"service_type": "build_villa",            "location": "paphos",   "experience_years": 15, "projects_completed": 65},
    ]
    for ctx in test_cases:
        print("=" * 70)
        print(f"TITLE: {build_trade_title(ctx)}")
        print()
        print(build_trade_description(ctx))
        print()
