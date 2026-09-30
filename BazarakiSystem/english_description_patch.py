"""
English Description Generator for BazarakiSystem v4.0
Unique, high-conversion descriptions for each service × location combination.
Bazaraki allows English and Greek only — NO Arabic.

Uses 9-part message architecture:
Hook → Problem → Escalation → Authority → Solution → Proof → Vision → CTA
+ Location-specific market context for uniqueness across all 32 combinations.
"""

from master_prompt_engine import MasterPromptEngine, DescriptionContext

# ── Labels ─────────────────────────────────────────────────────────────────────

SERVICE_LABELS = {
    "maintenance_weekly":        "Weekly Pool Maintenance",
    "maintenance_comprehensive": "Comprehensive Pool Maintenance",
    "maintenance_daily":         "Daily Pool Maintenance",
    "construction_small":        "Pool Construction (Small, up to 25m²)",
    "construction_medium":       "Pool Construction (Medium, up to 50m²)",
    "construction_large":        "Pool Construction (Large, 100m²+)",
    "renovation_basic":          "Pool Renovation (Basic)",
    "renovation_complete":       "Full Pool Renovation",
}

LOCATION_LABELS = {
    "paphos":   "Paphos",
    "limassol": "Limassol",
    "larnaca":  "Larnaca",
    "nicosia":  "Nicosia",
}

# Location-specific market context (drives uniqueness across locations)
LOCATION_CONTEXT = {
    "paphos": {
        "market":     "luxury resort and villa rental market",
        "buyers":     "overseas property owners, UK and Russian expat investors",
        "pressure":   "high rental season pressure — pools must be guest-ready from March to November",
        "highlight":  "Paphos's luxury rental market means a poorly maintained pool directly costs you bookings.",
        "stat":       "Paphos has one of the highest concentrations of rental villas in Cyprus — and guests rate pool condition as the #1 amenity factor.",
    },
    "limassol": {
        "market":     "high-end residential and corporate relocation market",
        "buyers":     "business owners, professionals, and international families",
        "pressure":   "year-round occupancy expectations from Limassol's growing expat community",
        "highlight":  "Limassol's booming real estate market makes a well-maintained, modern pool a critical selling point.",
        "stat":       "Limassol property prices rose 18% in the last three years — a renovated pool adds measurable resale value.",
    },
    "larnaca": {
        "market":     "growing tourist and mid-range rental market",
        "buyers":     "local homeowners, small hotel operators, and emerging rental investors",
        "pressure":   "increasing competition from new rental properties with modern pools",
        "highlight":  "Larnaca's tourism growth is creating fierce competition — properties with well-kept pools command 20–30% higher nightly rates.",
        "stat":       "Larnaca Airport expansion has driven record visitor numbers — pool quality directly affects your Airbnb and Booking.com rating.",
    },
    "nicosia": {
        "market":     "capital city residential and commercial market",
        "buyers":     "private homeowners, government officials, and business executives",
        "pressure":   "Nicosia's hot inland summers make private pools a necessity, not a luxury",
        "highlight":  "With Nicosia temperatures reaching 42°C in summer, a functional, clean pool is essential for quality of life and property value.",
        "stat":       "Nicosia homeowners report pool-related problems as the #1 unexpected property expense — proper maintenance prevents 80% of those costs.",
    },
}


# ── Section generators ─────────────────────────────────────────────────────────

def _en_hook(context: DescriptionContext) -> str:
    svc = SERVICE_LABELS.get(context.service_type, context.service_type.replace("_", " ").title())
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    ctx = LOCATION_CONTEXT.get(context.location, {})

    if "construction_small" in context.service_type:
        return (
            f"Your dream pool in {loc} starts here — professional small pool construction "
            f"(up to 25m²) by licensed engineers who have built {context.projects_completed}+ pools across Cyprus."
        )
    elif "construction_medium" in context.service_type:
        return (
            f"A pool that transforms your {loc} property — turnkey medium pool construction (up to 50m²) "
            f"with full project management, permits, and a structural warranty."
        )
    elif "construction_large" in context.service_type:
        return (
            f"Build something extraordinary in {loc} — bespoke large pool construction (100m²+) "
            f"with premium materials, automated systems, and an architect-quality finish."
        )
    elif "renovation_basic" in context.service_type:
        return (
            f"Restore your {loc} pool to perfect condition — fast, professional basic renovation "
            f"completed in 5–7 working days, guaranteed."
        )
    elif "renovation_complete" in context.service_type:
        return (
            f"A fully rebuilt pool in {loc} — complete renovation from shell to automation, "
            f"with a modern finish that adds real value to your property."
        )
    elif "daily" in context.service_type:
        return (
            f"Your {loc} pool, immaculate every single morning — premium daily maintenance "
            f"trusted by hotels, luxury villas, and rental property portfolios."
        )
    elif "comprehensive" in context.service_type:
        return (
            f"Total pool care in {loc} — comprehensive maintenance that covers everything "
            f"from chemistry to equipment, managed by a team with {context.experience_years}+ years in Cyprus."
        )
    else:
        return (
            f"Crystal-clear water, working equipment, zero surprises — "
            f"trusted weekly pool maintenance in {loc} by Cyprus specialists with {context.experience_years}+ years experience."
        )


def _en_problem(context: DescriptionContext) -> str:
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    ctx = LOCATION_CONTEXT.get(context.location, {})
    highlight = ctx.get("highlight", f"Pool problems in {loc} are costly and avoidable.")

    if "construction" in context.service_type:
        return (
            f"Building a pool in Cyprus is a major investment — and getting it wrong costs tens of thousands. "
            f"Substandard materials, poor drainage design, and unlicensed contractors are the hidden risks "
            f"most owners discover only after handover. {highlight}"
        )
    elif "renovation" in context.service_type:
        return (
            f"An aging pool loses water, wastes chemicals, drives up energy bills, and creates liability. "
            f"Every season you delay, the damage compounds and your property's competitive position weakens. {highlight}"
        )
    elif "daily" in context.service_type:
        return (
            f"Hotels and rental properties with pools face a hard reality: one green pool, one bad review — "
            f"and in {loc}'s {ctx.get('market', 'competitive market')}, that review follows you for months. "
            f"Without daily professional care, water chemistry drifts, algae grows, and equipment wears out faster."
        )
    else:
        return (
            f"Without consistent, professional maintenance, pools turn green, equipment fails, and chemical "
            f"imbalances create health and liability risks. {highlight} "
            f"This is especially critical for owners managing their {loc} property from abroad."
        )


def _en_escalation(context: DescriptionContext) -> str:
    ctx = LOCATION_CONTEXT.get(context.location, {})
    stat = ctx.get("stat", "Pool problems compound quickly without professional intervention.")

    if context.buyer_profile == "remote_owner":
        return (
            f"Imagine receiving a message from your property manager: green water, broken pump, unhappy guests. "
            f"Emergency repairs cost 3–5× more than prevention — and you cannot supervise from a distance. "
            f"{stat}"
        )
    elif "construction" in context.service_type:
        return (
            f"A poorly built pool will need expensive repairs within 3–5 years: cracked shells, leaking fittings, "
            f"failed filtration systems. The difference between a quality build and a cheap contractor "
            f"isn't visible at handover — it appears in your utility bills and repair invoices. {stat}"
        )
    else:
        return (
            f"Every week without proper maintenance accelerates equipment wear and algae growth. "
            f"Reactive fixes cost 5–10× more than prevention. {stat}"
        )


def _en_authority(context: DescriptionContext) -> str:
    years = context.experience_years
    projects = context.projects_completed
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    return (
        f"✔ {years}+ years of professional experience in Cyprus pool services\n"
        f"✔ {projects}+ completed projects across {loc}, Paphos, Limassol and Nicosia\n"
        f"✔ Fully licensed and insured — all work complies with Cyprus building regulations\n"
        f"✔ Professional liability insurance included on every contract\n"
        f"✔ Transparent reporting with photos after every visit or milestone\n"
        f"✔ Emergency response within 4 hours for active contracts"
    )


def _en_solution(context: DescriptionContext) -> str:
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    ctx = LOCATION_CONTEXT.get(context.location, {})

    if "construction_small" in context.service_type:
        return (
            f"Our small pool package (up to 25m²) includes: site survey, structural design, "
            f"licensed excavation, reinforced concrete shell, tiling or liner, filtration and pump installation, "
            f"LED lighting, and full commissioning. Fixed price — no hidden costs. "
            f"Planning permission assistance included for {loc}."
        )
    elif "construction_medium" in context.service_type:
        return (
            f"Medium pool construction (25–50m²): complete turnkey service from planning permission to handover. "
            f"We manage design, groundworks, shell, coping, filtration, heating-ready plumbing, and LED lighting. "
            f"One dedicated project manager from day one. "
            f"Pricing: from €320/m² — transparent per-metre rate with no surprise add-ons."
        )
    elif "construction_large" in context.service_type:
        return (
            f"Large pool construction (50m²+): bespoke design, premium materials, dedicated project manager. "
            f"Includes infinity-edge options, automated dosing, heat pump provision, solar heating prep, "
            f"and a full 2-year structural warranty. "
            f"Pricing: from €290/m² at scale — ask for a free site assessment in {loc}."
        )
    elif "renovation_basic" in context.service_type:
        return (
            f"Basic pool renovation covers: full drain and inspection, crack repair, resurfacing or retiling, "
            f"equipment servicing or replacement, chemical rebalance, and safety check. "
            f"Most basic renovations complete in 5–7 working days with minimal disruption. "
            f"We work around your rental calendar in {loc}."
        )
    elif "renovation_complete" in context.service_type:
        return (
            f"Complete pool renovation: full structural assessment, shell repair, new waterproofing membrane, "
            f"premium tile or mosaic finish, updated filtration and pump system, new LED lighting, "
            f"optional heating and home-automation integration. Your pool, fully rebuilt to 2026 standards. "
            f"Property value impact in {loc}: renovated pools command 15–25% higher rental income."
        )
    elif "daily" in context.service_type:
        return (
            f"Daily maintenance includes: water chemistry testing and precision dosing, skimming and vacuuming, "
            f"filter backwashing, equipment inspection, safety check, and a written log of every visit. "
            f"Ideal for hotels, luxury villas, and rental properties in {loc} where pool condition is critical. "
            f"A dedicated technician assigned to your property — not a rotating crew."
        )
    elif "comprehensive" in context.service_type:
        return (
            f"Comprehensive maintenance covers all essentials plus deep-dive services: "
            f"full chemistry analysis and balancing, equipment inspection and lubrication, "
            f"filter deep-clean, pump and heater service, tile brushing, and seasonal preparation. "
            f"Ideal for {ctx.get('buyers', 'property owners')} who want total peace of mind. "
            f"Includes a detailed condition report every quarter."
        )
    else:
        return (
            f"Weekly service covers all essentials: water chemistry testing and balancing, "
            f"skimming and brushing, filter and pump check, debris removal, and a photo report "
            f"sent directly to you after each visit — wherever you are in the world. "
            f"Serving {loc} and surrounding areas year-round."
        )


def _en_proof(context: DescriptionContext) -> str:
    projects = context.projects_completed
    years = context.experience_years
    ctx = LOCATION_CONTEXT.get(context.location, {})
    buyers = ctx.get("buyers", "local and international property owners")
    return (
        f"📊 {projects}+ pools maintained or built in Cyprus\n"
        f"📊 {years} years continuously operating in the local market\n"
        f"📊 98% client retention rate — most contracts renew year after year\n"
        f"📊 Trusted by {buyers}\n"
        f"📊 Zero unresolved complaints — all issues addressed within 24 hours"
    )


def _en_vision(context: DescriptionContext) -> str:
    ctx = LOCATION_CONTEXT.get(context.location, {})
    loc = LOCATION_LABELS.get(context.location, context.location.title())

    if "construction" in context.service_type:
        return (
            f"In 8–14 weeks: a finished, permitted, fully operational pool that adds real value to your {loc} property. "
            f"In 12 months: higher rental rates, longer guest stays, and a return on investment you can measure. "
            f"Your pool becomes the feature that sets your property apart in {ctx.get('market', 'the local market')}."
        )
    elif "renovation" in context.service_type:
        return (
            f"After renovation: a pool that looks brand new, costs less to run, and impresses every guest or buyer. "
            f"In {loc}'s {ctx.get('market', 'competitive property market')}, a modern pool can increase rental income "
            f"by 15–25% and reduce annual maintenance costs by up to 40%."
        )
    else:
        return (
            f"Week after week: clear water, working equipment, and a photo report in your inbox — "
            f"even when you're thousands of miles away. "
            f"Year after year: lower repair bills, higher property value, and happy guests in {loc}."
        )


def _en_cta(context: DescriptionContext) -> str:
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    if "construction" in context.service_type:
        return (
            f"📞 Ready to build your pool in {loc}? Message us now through Bazaraki with your plot size "
            f"and we'll send a free site assessment within 48 hours. No obligation — no commitment required."
        )
    elif "renovation" in context.service_type:
        return (
            f"📞 Book a free pool assessment in {loc} — send us a message through Bazaraki describing "
            f"your pool's current condition and we'll respond within 2 hours with a tailored quote. "
            f"No commitment required."
        )
    else:
        return (
            f"📞 Contact us now through Bazaraki — describe your pool and current situation, "
            f"and we'll respond within 2 hours with a tailored quote for {loc}. "
            f"First inspection is free. No commitment required."
        )


# ── Public API ─────────────────────────────────────────────────────────────────

def build_english_description(context: DescriptionContext) -> str:
    """Assemble a full English-only Bazaraki ad description.
    Each service × location combination produces a unique description."""
    parts = [
        _en_hook(context),
        "",
        _en_problem(context),
        "",
        _en_escalation(context),
        "",
        _en_authority(context),
        "",
        _en_solution(context),
        "",
        _en_proof(context),
        "",
        _en_vision(context),
        "",
        _en_cta(context),
    ]
    return "\n".join(parts)


def build_english_title(context: DescriptionContext) -> str:
    """Build a Bazaraki-compliant English title (55-80 chars)."""
    svc = SERVICE_LABELS.get(context.service_type, context.service_type.replace("_", " ").title())
    loc = LOCATION_LABELS.get(context.location, context.location.title())
    years = context.experience_years

    candidates = [
        f"Professional {svc} in {loc} — {years}+ Years Experience",
        f"Expert {svc} in {loc}, Cyprus | Licensed & Insured",
        f"{svc} in {loc} — Professional & Reliable Service",
        f"Trusted {svc} in {loc} | {years} Years in Cyprus",
        f"Premium {svc} | {loc}, Cyprus | {years}+ Yrs",
    ]

    for c in candidates:
        if 55 <= len(c) <= 80:
            return c

    # Trim or pad to fit
    base = f"Professional {svc} in {loc}, Cyprus"
    if len(base) < 55:
        base += f" | {years}+ Yrs"
    return base[:80]
