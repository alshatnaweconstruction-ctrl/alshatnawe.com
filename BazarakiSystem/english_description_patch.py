"""
English Description Generator for BazarakiSystem v4.0
Full catalog: residential, commercial, specialty, renovation, linings.
Bazaraki allows English and Greek only — NO Arabic.

9-part architecture per ad: Hook → Problem → Escalation → Authority →
Solution → Proof → Vision → CTA, with unique content per service × location.
"""

from master_prompt_engine import MasterPromptEngine, DescriptionContext

# ── Labels ─────────────────────────────────────────────────────────────────────

SERVICE_LABELS = {
    # Maintenance
    "maintenance_weekly":        "Weekly Pool Maintenance",
    "maintenance_comprehensive": "Comprehensive Pool Maintenance",
    "maintenance_daily":         "Daily Pool Maintenance",
    # Residential construction by size
    "construction_small":        "Residential Pool Construction (up to 25m²)",
    "construction_medium":       "Residential Pool Construction (up to 50m²)",
    "construction_large":        "Residential Pool Construction (100m²+)",
    # Pool types
    "pool_overflow":             "Overflow Pool Construction",
    "pool_skimmer":              "Skimmer Pool Construction",
    "pool_infinity":             "Infinity Pool Construction",
    # Linings
    "lining_liner":              "Pool Vinyl Liner Supply & Installation",
    "lining_mosaic":             "Pool Glass Mosaic Tiling",
    "lining_ceramic":            "Pool Ceramic Tile Finish",
    # Commercial
    "commercial_pool":           "Commercial Pool Construction",
    "commercial_spa":            "Commercial Spa Construction",
    "commercial_fountain":       "Decorative Fountain Construction",
    "hotel_pool_service":        "Hotel & Resort Pool Maintenance",
    # Specialty
    "swim_spa":                  "Swim Spa Supply & Installation",
    "waterpark":                 "Waterpark Construction",
    "cooling_heating":           "Pool Cooling & Heating Systems",
    "rock_features":             "Reconstituted Rock Pool Features",
    "bar_and_stools":            "Pool Bar & Stool Construction",
    # Renovation
    "renovation_basic":          "Pool Renovation (Basic)",
    "renovation_complete":       "Complete Pool Renovation",
}

LOCATION_LABELS = {
    "paphos":   "Paphos",
    "limassol": "Limassol",
    "larnaca":  "Larnaca",
    "nicosia":  "Nicosia",
}

LOCATION_CONTEXT = {
    "paphos": {
        "market":    "luxury villa and resort rental market",
        "buyers":    "UK, Russian, and Israeli property investors",
        "stat":      "Paphos has the highest concentration of rental villas in Cyprus — pool quality is the #1 booking factor.",
        "highlight": "In Paphos's luxury market, a substandard pool directly costs you bookings and rental income.",
    },
    "limassol": {
        "market":    "high-end residential and corporate relocation market",
        "buyers":    "business owners, expat professionals, and international families",
        "stat":      "Limassol property prices rose 18% in three years — a premium pool adds measurable resale value.",
        "highlight": "Limassol's booming real estate market makes a modern, well-maintained pool a critical differentiator.",
    },
    "larnaca": {
        "market":    "growing tourism and mid-range rental market",
        "buyers":    "local homeowners, small hotels, and emerging rental investors",
        "stat":      "Larnaca Airport expansion has driven record visitor numbers — pool quality directly affects your ratings.",
        "highlight": "Larnaca's tourism growth means properties with premium pools command 20–30% higher nightly rates.",
    },
    "nicosia": {
        "market":    "capital city residential and commercial market",
        "buyers":    "private homeowners, executives, and government officials",
        "stat":      "Nicosia temperatures reach 42°C in summer — a well-functioning pool is a necessity, not a luxury.",
        "highlight": "In Nicosia's intense summer heat, pool problems compound fast and cost far more to fix reactively.",
    },
}

# ── Category helpers ────────────────────────────────────────────────────────────

def _is_construction(st):    return "construction" in st or st in ("pool_overflow", "pool_skimmer", "pool_infinity")
def _is_lining(st):          return st.startswith("lining_")
def _is_commercial(st):      return st.startswith("commercial_") or st == "hotel_pool_service"
def _is_specialty(st):       return st in ("swim_spa", "waterpark", "cooling_heating", "rock_features", "bar_and_stools")
def _is_renovation(st):      return "renovation" in st
def _is_maintenance(st):     return "maintenance" in st


# ── Section generators ─────────────────────────────────────────────────────────

def _en_hook(context: DescriptionContext) -> str:
    st  = context.service_type
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    yrs = context.experience_years
    pro = context.projects_completed

    hooks = {
        "pool_overflow":        f"A pool that overflows with elegance — professional overflow pool construction in {loc}, Cyprus, by engineers with {yrs}+ years of precision work.",
        "pool_skimmer":         f"The classic of Cyprus pools, built right — skimmer pool construction in {loc} with a {yrs}-year track record and {pro}+ projects delivered.",
        "pool_infinity":        f"Where water meets horizon — infinity pool construction in {loc} by specialists who have crafted {pro}+ stunning pools across Cyprus.",
        "lining_liner":         f"A fresh new look for your {loc} pool in days — professional vinyl liner supply and installation, watertight and beautiful.",
        "lining_mosaic":        f"Turn your {loc} pool into a work of art — premium glass mosaic tiling by craftsmen with {yrs}+ years creating stunning underwater finishes.",
        "lining_ceramic":       f"A crisp, durable finish that lasts decades — professional ceramic pool tiling in {loc}, Cyprus.",
        "commercial_pool":      f"Built for performance, built for guests — commercial pool construction in {loc} for hotels, resorts, and leisure facilities.",
        "commercial_spa":       f"A spa that earns its keep — commercial spa construction in {loc} built to hospitality standards with full compliance certification.",
        "commercial_fountain":  f"Make a statement in {loc} — decorative fountain design and construction for public spaces, hotels, and commercial developments.",
        "hotel_pool_service":   f"Your guests notice the pool first — professional hotel and resort pool maintenance in {loc} trusted by Cyprus's leading hospitality brands.",
        "swim_spa":             f"Swim. Relax. Recover. All year round — swim spa supply and installation in {loc} by certified pool engineers.",
        "waterpark":            f"Build the attraction that defines your destination — waterpark construction in {loc}, Cyprus, from concept to opening day.",
        "cooling_heating":      f"Swim in perfect comfort all year — professional pool heating and cooling system installation in {loc} by certified engineers.",
        "rock_features":        f"Bring nature to your pool — bespoke reconstituted rock features for {loc} pools: waterfalls, grottos, and natural-stone surrounds.",
        "bar_and_stools":            f"The pool bar that becomes the heart of your property — professional pool bar and stool construction in {loc}, Cyprus.",
        "maintenance_weekly":        f"Crystal-clear water, working equipment, zero surprises — trusted weekly pool maintenance in {loc} by Cyprus specialists with {yrs}+ years experience.",
        "maintenance_daily":         f"Your {loc} pool, immaculate every single morning — premium daily pool care trusted by hotels, villas, and rental portfolios.",
        "maintenance_comprehensive": f"Total pool care in {loc} — comprehensive maintenance covering chemistry, equipment, and aesthetics by a team with {yrs}+ years in Cyprus.",
        "renovation_basic":          f"Restore your {loc} pool to perfect condition — fast basic renovation completed in 5–7 working days, guaranteed.",
        "renovation_complete":       f"A fully rebuilt pool in {loc} — complete renovation from shell to automation with a modern finish that adds real property value.",
        "construction_small":        f"Your dream pool in {loc} starts here — professional small pool construction (up to 25m²) by licensed engineers who have built {pro}+ pools across Cyprus.",
        "construction_medium":       f"A pool that transforms your {loc} property — turnkey medium pool construction (up to 50m²) with full project management, permits, and warranty.",
        "construction_large":        f"Build something extraordinary in {loc} — bespoke large pool construction (100m²+) with premium materials, automated systems, and architect-quality finish.",
    }
    if st in hooks:
        return hooks[st]
    return f"Professional pool services in {loc}, Cyprus — {yrs}+ years experience, {pro}+ completed projects."


def _en_problem(context: DescriptionContext) -> str:
    st  = context.service_type
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    ctx = LOCATION_CONTEXT.get(context.location, {})
    hl  = ctx.get("highlight", f"Pool quality is critical in {loc}.")

    if _is_commercial(st):
        return (
            f"Commercial pools and spas are held to a higher standard — health inspections, insurance requirements, "
            f"and guest expectations leave no margin for error. Underspecified systems, amateur workmanship, and "
            f"deferred maintenance can result in closures, liability claims, and reputational damage. {hl}"
        )
    elif _is_specialty(st) and st == "waterpark":
        return (
            f"A waterpark is one of the most complex leisure investments in Cyprus — engineering, water treatment, "
            f"safety certification, and project management all must execute in sequence. Delays and design errors "
            f"can cost millions. {hl}"
        )
    elif _is_specialty(st):
        return (
            f"Specialty pool features — swim spas, heating systems, rock features, pool bars — are investments "
            f"that only deliver their full value when installed correctly. Poor workmanship and wrong specifications "
            f"lead to high running costs, premature failure, and disappointed clients. {hl}"
        )
    elif _is_lining(st):
        return (
            f"An aging or damaged pool lining loses water, harbours algae, and makes the pool unattractive to "
            f"guests. Many owners put off lining replacement until water bills and chemical waste make it unavoidable — "
            f"by then, the cost is higher. {hl}"
        )
    elif _is_construction(st):
        return (
            f"Building a pool in Cyprus is a major investment — and getting it wrong costs tens of thousands. "
            f"Substandard materials, poor drainage design, and unlicensed contractors are the hidden risks "
            f"most owners discover only after handover. {hl}"
        )
    elif _is_renovation(st):
        return (
            f"An aging pool loses water, wastes chemicals, drives up energy bills, and creates liability. "
            f"Every season you delay renovation, the damage compounds and your property's competitive position weakens. {hl}"
        )
    else:
        return (
            f"Without consistent, professional maintenance, pools turn green, equipment fails, and chemical "
            f"imbalances create health and liability risks. {hl} "
            f"This is especially critical for owners managing their {loc} property from abroad."
        )


def _en_escalation(context: DescriptionContext) -> str:
    st  = context.service_type
    ctx = LOCATION_CONTEXT.get(context.location, {})
    stat = ctx.get("stat", "Pool problems compound quickly without professional intervention.")

    if _is_commercial(st) or st == "hotel_pool_service":
        return (
            f"One failed health inspection closes your pool — and in high season, a closed pool means empty rooms "
            f"and cancelled bookings that can never be recovered. {stat}"
        )
    elif st == "waterpark":
        return (
            f"A waterpark that opens late or with safety deficiencies faces regulatory shutdown, legal exposure, "
            f"and a reputation that is very hard to rebuild. The difference between a successful waterpark and a "
            f"failed one is always the quality of the engineering and project management. {stat}"
        )
    elif _is_construction(st):
        return (
            f"A poorly built pool will need expensive repairs within 3–5 years: cracked shells, leaking fittings, "
            f"failed filtration systems. The difference between quality and cheap isn't visible at handover — "
            f"it shows in your utility bills and repair invoices. {stat}"
        )
    elif context.buyer_profile == "remote_owner":
        return (
            f"Imagine receiving a message from your property manager: green water, broken pump, unhappy guests. "
            f"Emergency repairs cost 3–5× more than prevention — and you cannot supervise from a distance. {stat}"
        )
    else:
        return (
            f"Every week without proper maintenance accelerates equipment wear and algae growth. "
            f"Reactive fixes cost 5–10× more than prevention. {stat}"
        )


def _en_authority(context: DescriptionContext) -> str:
    yrs = context.experience_years
    pro = context.projects_completed
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    return (
        f"✔ {yrs}+ years of professional experience in Cyprus pool services\n"
        f"✔ {pro}+ completed projects across {loc}, Paphos, Limassol and Nicosia\n"
        f"✔ Fully licensed and insured — all work complies with Cyprus building regulations\n"
        f"✔ Professional liability insurance included on every contract\n"
        f"✔ Transparent reporting with photos after every visit or milestone\n"
        f"✔ Emergency response within 4 hours for active contracts"
    )


def _en_solution(context: DescriptionContext) -> str:
    st  = context.service_type
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    ctx = LOCATION_CONTEXT.get(context.location, {})

    solutions = {
        "pool_overflow": (
            f"Overflow pool construction in {loc}: full engineering design, licensed excavation, reinforced shell, "
            f"overflow channel and gutter system, tiling or mosaic finish, filtration, pump room, LED lighting, "
            f"and full commissioning. Per-metre² rate from €350/m² — transparent fixed pricing, no hidden costs."
        ),
        "pool_skimmer": (
            f"Skimmer pool construction in {loc}: complete turnkey from site survey to handover — concrete shell, "
            f"skimmer system, coping, ceramic or mosaic tiling, filtration, pump, LED lighting, and all plumbing. "
            f"From €280/m² — the most cost-effective quality pool in Cyprus."
        ),
        "pool_infinity": (
            f"Infinity pool construction in {loc}: bespoke design, precision-engineered vanishing edge, "
            f"balance tank, premium tiling or glass mosaic, automated dosing, heat pump provision, underwater LED, "
            f"and a 2-year structural warranty. From €450/m² — where engineering meets art."
        ),
        "lining_liner": (
            f"Vinyl liner supply and installation in {loc}: full drain and surface prep, custom-measured liner "
            f"(0.8mm or 1.0mm reinforced), professional fitting, bead-track installation, refill, and chemical "
            f"balance. Completed in 2–4 days. Liner warranty: 8 years."
        ),
        "lining_mosaic": (
            f"Glass mosaic pool tiling in {loc}: drain and surface preparation, adhesive bed, premium glass mosaic "
            f"tiles (25+ colour options including custom blends), professional grouting, sealing, and final polish. "
            f"From €85/m² — a finish that lasts 20+ years and transforms any pool."
        ),
        "lining_ceramic": (
            f"Ceramic pool tiling in {loc}: drain, prep, anti-fracture membrane, full-vitrified ceramic tiles "
            f"(frost-resistant, non-slip), professional adhesive and grouting, waterproof sealant. "
            f"From €55/m² — durable, clean, and easy to maintain."
        ),
        "commercial_pool": (
            f"Commercial pool construction in {loc} for hotels, resorts, and leisure facilities: full design and "
            f"planning, structural engineering, high-capacity filtration and treatment, automated dosing, "
            f"accessibility compliance, LED lighting, and full regulatory certification. "
            f"One project manager from concept to handover."
        ),
        "commercial_spa": (
            f"Commercial spa construction in {loc}: hydrotherapy jet layout design, structural shell, premium "
            f"surface finish, high-output heating, automated chemical dosing, lighting and audio, "
            f"health & safety compliance documentation, and operator training. Built to hospitality standards."
        ),
        "commercial_fountain": (
            f"Decorative fountain construction in {loc}: concept design, hydraulic engineering, basin and shell "
            f"construction, pump and nozzle system, programmable LED lighting, filtration, and annual service plan. "
            f"Suitable for hotel entrances, public plazas, and commercial developments."
        ),
        "hotel_pool_service": (
            f"Hotel and resort pool maintenance in {loc}: dedicated licensed technician, daily water chemistry "
            f"testing and dosing, equipment inspection, filter management, record-keeping for health authority "
            f"compliance, and emergency response within 2 hours. Monthly contract with guaranteed SLA."
        ),
        "swim_spa": (
            f"Swim spa supply and installation in {loc}: site preparation, structural base, supply of premium "
            f"swim spa unit (leading European brands available), plumbing, electrical, insulation cover, "
            f"commissioning, and operator training. Year-round use — built for Cyprus's climate."
        ),
        "waterpark": (
            f"Waterpark construction in {loc}: concept to completion — site feasibility, master planning, "
            f"engineering design, ride and attraction supply, water treatment plant, safety systems, "
            f"operator training, and regulatory compliance. Full turnkey delivery with phased opening support."
        ),
        "cooling_heating": (
            f"Pool heating and cooling in {loc}: heat pump selection and supply (leading brands), "
            f"hydraulic integration, electrical installation, thermostat and automation wiring, commissioning, "
            f"and a 2-year equipment warranty. Extend your swimming season to 10–12 months per year."
        ),
        "rock_features": (
            f"Reconstituted rock pool features in {loc}: custom design, structural engineering, GRC or "
            f"hand-sculpted reconstituted rock formation, waterfall plumbing and pump, integrated LED lighting, "
            f"and weatherproof sealant finish. Each feature is unique — no two are the same."
        ),
        "bar_and_stools": (
            f"Pool bar and stool construction in {loc}: waterproof structural base, rendered or tiled finish, "
            f"built-in sunken bar seating, service counter, plumbing for sink, electrical for lighting and fridge, "
            f"and weather-resistant surface treatment. The ultimate entertaining addition to any pool."
        ),
        "maintenance_daily": (
            f"Daily pool maintenance in {loc}: water chemistry testing and precision dosing, skimming, vacuuming, "
            f"filter backwashing, equipment inspection, safety check, and a written visit log. "
            f"Dedicated technician — not a rotating crew. Ideal for hotels, luxury villas, and rental properties."
        ),
        "maintenance_comprehensive": (
            f"Comprehensive pool maintenance in {loc}: full chemistry analysis, equipment inspection and lubrication, "
            f"filter deep-clean, pump and heater service, tile brushing, seasonal preparation, "
            f"and a quarterly condition report. For {ctx.get('buyers','property owners')} who want total peace of mind."
        ),
        "maintenance_weekly": (
            f"Weekly pool maintenance in {loc}: chemistry testing and balancing, skimming and brushing, "
            f"filter and pump check, debris removal, and a photo report sent after every visit — "
            f"wherever you are in the world. Year-round service, flexible contracts."
        ),
        "renovation_basic": (
            f"Basic pool renovation in {loc}: full drain and inspection, crack repair, resurfacing or retiling, "
            f"equipment servicing or replacement, chemical rebalance, and safety check. "
            f"Most basic renovations complete in 5–7 working days. We work around your rental calendar."
        ),
        "renovation_complete": (
            f"Complete pool renovation in {loc}: full structural assessment, shell repair, new waterproofing membrane, "
            f"premium tile or mosaic finish, updated filtration and pump system, new LED lighting, "
            f"optional heating and automation upgrade. Your pool, fully rebuilt to 2026 standards. "
            f"Rental income impact: renovated pools command 15–25% higher rates in {loc}."
        ),
        "construction_small": (
            f"Small pool construction in {loc} (up to 25m²): site survey, structural design, licensed excavation, "
            f"reinforced concrete shell, tiling or liner, filtration and pump, LED lighting, and full commissioning. "
            f"Fixed price from €320/m² — no hidden costs. Planning permission assistance included."
        ),
        "construction_medium": (
            f"Medium pool construction in {loc} (25–50m²): complete turnkey from planning permission to handover. "
            f"We manage design, groundworks, shell, coping, filtration, heating-ready plumbing, and LED lighting. "
            f"One dedicated project manager. From €300/m² — transparent per-metre pricing, zero surprises."
        ),
        "construction_large": (
            f"Large pool construction in {loc} (50m²+): bespoke design, premium materials, dedicated project manager. "
            f"Includes infinity-edge options, automated dosing, heat pump provision, solar heating prep, "
            f"and a full 2-year structural warranty. From €290/m² at scale — ask for a free site assessment."
        ),
    }
    return solutions.get(st, f"Professional pool services in {loc} — contact us for a tailored quote.")


def _en_proof(context: DescriptionContext) -> str:
    pro = context.projects_completed
    yrs = context.experience_years
    ctx = LOCATION_CONTEXT.get(context.location, {})
    buyers = ctx.get("buyers", "local and international property owners")
    return (
        f"📊 {pro}+ pools built, renovated, or maintained in Cyprus\n"
        f"📊 {yrs} years continuously operating in the local market\n"
        f"📊 98% client retention rate — most contracts renew year after year\n"
        f"📊 Trusted by {buyers}\n"
        f"📊 Zero unresolved complaints — all issues addressed within 24 hours"
    )


def _en_vision(context: DescriptionContext) -> str:
    st  = context.service_type
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    ctx = LOCATION_CONTEXT.get(context.location, {})

    if st == "waterpark":
        return (
            f"Opening day in {loc}: a fully operational, safety-certified waterpark that attracts visitors "
            f"from across Cyprus and abroad. Year one: occupancy, return visits, and a brand that defines the "
            f"destination. A generational asset — built to last 30+ years."
        )
    elif _is_commercial(st) or st == "hotel_pool_service":
        return (
            f"Your {loc} property becomes known for its pool — guests specifically request it, review it, "
            f"and return for it. Health inspections pass first time, every time. A pool that earns its keep "
            f"and protects your reputation in {ctx.get('market','the local hospitality market')}."
        )
    elif _is_construction(st):
        return (
            f"In 8–14 weeks: a finished, permitted, fully operational pool that adds real value to your {loc} property. "
            f"In 12 months: higher rental rates, longer guest stays, and a return on investment you can measure. "
            f"Your pool becomes the feature that sets your listing apart in {ctx.get('market','the local market')}."
        )
    elif _is_renovation(st):
        return (
            f"After renovation: a pool that looks brand new, costs less to run, and impresses every guest. "
            f"In {loc}'s {ctx.get('market','competitive market')}, a modern pool increases rental income "
            f"by 15–25% and reduces annual maintenance costs by up to 40%."
        )
    elif st in ("cooling_heating", "swim_spa"):
        return (
            f"12 months of comfortable swimming in {loc} — not just summer. Heat pump ROI is typically "
            f"achieved in under 3 seasons through extended rental income and increased property appeal."
        )
    else:
        return (
            f"Week after week: clear water, working equipment, and a photo report in your inbox — "
            f"even when you're thousands of miles away. "
            f"Year after year: lower repair bills, higher property value, and happy guests in {loc}."
        )


def _en_cta(context: DescriptionContext) -> str:
    st  = context.service_type
    loc = LOCATION_LABELS.get(context.location, context.location.title())

    if _is_commercial(st) or st == "waterpark":
        return (
            f"📞 Send us a message through Bazaraki with your project scope in {loc} "
            f"and we'll arrange a free site consultation within 48 hours. "
            f"Commercial projects receive a detailed tender document within 5 working days."
        )
    elif _is_construction(st):
        return (
            f"📞 Ready to build your pool in {loc}? Message us through Bazaraki with your plot size "
            f"and we'll provide a free site assessment within 48 hours. No obligation."
        )
    elif _is_renovation(st):
        return (
            f"📞 Book a free pool assessment in {loc} — message us through Bazaraki describing "
            f"your pool's current condition and we'll respond within 2 hours with a tailored quote. "
            f"No commitment required."
        )
    else:
        return (
            f"📞 Contact us now through Bazaraki — describe your pool and current situation "
            f"and we'll respond within 2 hours with a tailored quote for {loc}. "
            f"First inspection is free. No commitment required."
        )


# ── Public API ─────────────────────────────────────────────────────────────────

def build_english_description(context: DescriptionContext) -> str:
    """Full unique English description for one service × location combination."""
    parts = [
        _en_hook(context),        "",
        _en_problem(context),     "",
        _en_escalation(context),  "",
        _en_authority(context),   "",
        _en_solution(context),    "",
        _en_proof(context),       "",
        _en_vision(context),      "",
        _en_cta(context),
    ]
    return "\n".join(parts)


def build_english_title(context: DescriptionContext) -> str:
    """Bazaraki-compliant English title (55–80 chars)."""
    svc = SERVICE_LABELS.get(context.service_type, context.service_type.replace("_", " ").title())
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    yrs = context.experience_years

    candidates = [
        f"Professional {svc} in {loc} — {yrs}+ Years Experience",
        f"Expert {svc} in {loc}, Cyprus | Licensed & Insured",
        f"{svc} in {loc} — Professional & Reliable Service",
        f"Trusted {svc} in {loc} | {yrs} Years in Cyprus",
        f"Premium {svc} | {loc}, Cyprus | {yrs}+ Yrs",
        f"{svc} {loc} Cyprus — {yrs}+ Years | Insured",
    ]
    for c in candidates:
        if 55 <= len(c) <= 80:
            return c
    base = f"Professional {svc} in {loc}, Cyprus"
    if len(base) < 55:
        base += f" | {yrs}+ Yrs"
    return base[:80]
