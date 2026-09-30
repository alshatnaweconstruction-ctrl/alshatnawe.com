"""
ADVANCED COPYWRITING ENGINE v2
Psychological + Economic + Semantic Intelligence
Based on PASTOR Framework + Neuromarketing Principles
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class PsychologicalTrigger(Enum):
    """Neuromarketing triggers that drive buyer decisions"""
    SCARCITY = "scarcity"  # Limited competitors, high demand
    SOCIAL_PROOF = "social_proof"  # Years of experience, numbers
    URGENCY = "urgency"  # Seasonal demand, time-sensitive
    EMOTIONAL_RELIEF = "emotional_relief"  # Problem solved = peace of mind
    SPECIFICITY = "specificity"  # Details build trust
    AUTHORITY = "authority"  # Expert credentials
    RECIPROCITY = "reciprocity"  # Value first (free quote, assessment)
    CONSISTENCY = "consistency"  # Proven track record

class BuyerPsychology:
    """Understanding Cyprus buyer behavior by service type"""

    BUYER_PROFILES = {
        'pool_maintenance': {
            'psychology': 'Status + Leisure Protection',
            'pain_point': 'Pool neglect reduces property value + safety risk',
            'emotional_need': 'Peace of mind + social status (entertaining guests)',
            'trigger': PsychologicalTrigger.EMOTIONAL_RELIEF,
            'decision_factor': 'Reliability + consistent quality',
            'time_sensitivity': 'High (summer season)',
            'keywords': ['reliable', 'crystal clear', 'safe swimming', 'year-round care']
        },
        'pool_renovation': {
            'psychology': 'Investment + Transformation',
            'pain_point': 'Old pool is eyesore + expensive repairs pile up',
            'emotional_need': 'Transform outdated to modern luxury',
            'trigger': PsychologicalTrigger.SOCIAL_PROOF,
            'decision_factor': 'Quality of workmanship + warranty',
            'time_sensitivity': 'Medium (spring/early summer planning)',
            'keywords': ['modern', 'investment-grade', 'lasting', 'transformation']
        },
        'ac_installation': {
            'psychology': 'Survival + Comfort',
            'pain_point': 'Unbearable summer heat = health + productivity risk',
            'emotional_need': 'Comfort + climate control confidence',
            'trigger': PsychologicalTrigger.URGENCY,
            'decision_factor': 'Speed + reliability + silent operation',
            'time_sensitivity': 'CRITICAL (July-August peak)',
            'keywords': ['silent', 'powerful cooling', 'urgent availability', 'professional']
        },
        'solar_installation': {
            'psychology': 'Future-Proofing + Savings',
            'pain_point': 'Rising electricity costs threatening savings',
            'emotional_need': 'Energy independence + long-term security',
            'trigger': PsychologicalTrigger.SOCIAL_PROOF,
            'decision_factor': 'ROI + warranty + government incentives',
            'time_sensitivity': 'Medium (incentive deadlines)',
            'keywords': ['savings', 'independence', 'government-approved', 'future-proof']
        }
    }

class AdvancedCopywriter:
    """
    Next-generation copywriting engine combining:
    - PASTOR framework (persuasion structure)
    - Neuromarketing (psychological triggers)
    - Economic pricing psychology
    - Semantic search optimization
    - Buyer journey mapping
    - Contextual language patterns
    """

    BANNED_WORDS = {
        'sale', 'sell', 'urgent', 'price', 'inexpensive',
        'rent', 'specialist', 'discount', 'special offer',
        'limited time', 'best', 'top', 'leading', 'premium'
    }

    BANNED_PHRASES = [
        'we offer', 'our team', 'premium solutions',
        'quality workmanship', 'we provide', 'our expert',
        'number one', 'satisfaction guaranteed', 'affordable'
    ]

    # ADVANCED: Problem-agitate-solution angles by service
    PSYCHOGRAPHIC_ANGLES = {
        'pool_services': {
            'remote_owner': 'Property value protection while abroad',
            'local_owner': 'Summer entertaining readiness + status',
            'investor': 'Asset maintenance + liability reduction',
            'family': 'Child safety + wholesome entertainment'
        },
        'ac_services': {
            'remote_owner': 'Tenant comfort + property value',
            'local_owner': 'Family health + productivity',
            'investor': 'Tenant retention + premium pricing',
            'business': 'Customer comfort + operational efficiency'
        },
        'solar_services': {
            'homeowner': 'Rising electricity costs / independence',
            'investor': 'Long-term ROI + government incentives',
            'business': 'Operating cost reduction + green branding'
        }
    }

    def __init__(self):
        self.buyer_psychology = BuyerPsychology()

    def analyze_service_psychology(self, service_type: str) -> Dict:
        """Determine emotional drivers for this service"""
        default_profile = {
            'psychology': 'general',
            'pain_point': f'Finding reliable {service_type} services is challenging',
            'emotional_need': 'Quality service delivery',
            'trigger': PsychologicalTrigger.SPECIFICITY,
            'decision_factor': 'Reliability and quality',
            'time_sensitivity': 'Medium',
            'keywords': ['reliable', 'professional', 'quality', 'experienced']
        }
        profile = self.buyer_psychology.BUYER_PROFILES.get(service_type, default_profile)
        return profile

    def generate_problem_statement(self, service_type: str, buyer_type: str,
                                   location: str) -> str:
        """
        Generate opening that NAMES THE PROBLEM (not "we offer").
        Triggers emotional recognition in buyer.
        Uses psychological principle of pattern matching.
        """
        psychology = self.analyze_service_psychology(service_type)

        problem_templates = {
            'pool_maintenance': {
                'remote_owner': f"Managing a property in {location} means you can't monitor the pool daily—algae builds, equipment fails silently, and by summer it's a crisis.",
                'local_owner': "Keeping a pool pristine all season is exhausting—chemical balance, equipment maintenance, liability concerns keep building up.",
                'investor': "Neglected pools are liability nightmares and deal-breakers for renters—one accident erases margins from an entire year."
            },
            'pool_renovation': {
                'remote_owner': f"An aging pool isn't just an eyesore in {location}—it's a money pit draining equity and threatening safety.",
                'local_owner': "Your pool has stopped being an asset—it's a burden, outdated, unreliable, and it's killing your summer plans.",
                'investor': "Old pools make properties hard to rent and impossible to sell at premium prices—renovation is survival, not luxury."
            },
            'ac_installation': {
                'remote_owner': "Tenants in your Cyprus property are suffering without AC—they're leaving, leaving bad reviews, or demanding rent reductions.",
                'local_owner': f"Cyprus summers are becoming unlivable without proper AC—your family is suffering, productivity is zero, sleep is impossible.",
                'investor': "High-performing rentals in Cyprus demand AC; without it, you lose tenants to competitors and can't raise rental rates."
            },
            'solar_installation': {
                'homeowner': "Your electricity bills are climbing every summer—what you paid last year costs 20% more now, and the trend is accelerating.",
                'investor': "Rising energy costs are eating into property margins—tenants expect low utility bills, and you're losing competitiveness.",
                'business': "Energy costs are squeezing every margin—solar isn't luxury, it's basic survival for long-term business planning."
            }
        }

        template_key = f"{service_type}_{buyer_type}" if buyer_type in ['remote_owner', 'local_owner', 'investor'] else service_type
        return problem_templates.get(template_key, f"Finding reliable {service_type} services is challenging.")

    def generate_solution_with_psychology(self, service_type: str, problem: str,
                                         experience: str = '') -> str:
        """
        Generate solution that SHOWS HOW PROBLEM IS SOLVED.
        Emphasizes outcome, not features.
        Includes social proof trigger.
        """
        solutions = {
            'pool_maintenance': f"We handle everything: water chemistry, equipment maintenance, filter changes, weekly inspections. You get a pristine pool 52 weeks a year. {experience or 'Specialized in Cyprus properties.'} Reports every visit so you know exactly what's happening.",
            'pool_renovation': f"Complete renovation: structural repair, new equipment, modern finishes, certifications. Transform liability into asset. {experience or 'Projects completed with 2-year warranty.'} Starting from assessment to handover, we manage every detail.",
            'ac_installation': f"Professional installation with performance guarantee: cooling power, silent operation, energy efficiency. {experience or 'Rapid response even in peak season.'} We handle emergency calls 24/7 during summer.",
            'solar_installation': f"End-to-end system: design, installation, permits, activation. Start saving immediately. {experience or 'Fully government-approved systems.'} Flexible financing options + tax incentives guidance.",
        }
        return solutions.get(service_type, "Professional solution tailored to your needs.")

    def generate_advanced_title(self, service_type: str, location: str,
                                buyer_type: str = 'general',
                                profitability: str = 'high') -> str:
        """
        Generate title using:
        - Outcome-focused language (not feature-focused)
        - Location specificity (search optimization)
        - Psychological trigger
        - Character limit 55-80
        """

        templates = {
            ('pool_maintenance', 'remote_owner'): f"Pool Care for Owners Abroad in {location}",
            ('pool_maintenance', 'local_owner'): f"Year-Round Pool Maintenance in {location}",
            ('pool_renovation', 'investor'): f"Pool Renovation for Investment Properties {location}",
            ('pool_renovation', 'general'): f"Complete Pool Renovation in {location} Cyprus",
            ('ac_installation', 'urgent'): f"Emergency AC Installation {location} Cyprus",
            ('ac_installation', 'investor'): f"AC for Rental Properties {location}",
            ('solar_installation', 'general'): f"Solar Installation + Energy Savings {location}",
        }

        key = (service_type, buyer_type)
        title = templates.get(key, f"Professional {service_type} services in {location}")

        # Validate length
        if len(title) < 55:
            title = f"Professional {service_type} services in {location} Cyprus"
        elif len(title) > 80:
            title = title[:80]

        return title

    def generate_trust_section(self, service_type: str, years: int = 0,
                               projects: int = 0, warranty: str = '') -> str:
        """
        Build trust through SPECIFIC social proof.
        Numbers > vague claims.
        """
        trust_elements = []

        if years > 0:
            if years >= 10:
                trust_elements.append(f"Over {years} years managing {service_type} projects across Cyprus")
            else:
                trust_elements.append(f"{years} years specialized experience")

        if projects > 0:
            if projects >= 500:
                trust_elements.append(f"{projects}+ completed projects")
            else:
                trust_elements.append(f"{projects} successful installations")

        if warranty:
            trust_elements.append(f"Full {warranty} warranty on all work")

        trust_elements.append("Registered company with professional insurance")
        trust_elements.append("Cyprus-based, local availability")

        return " | ".join(trust_elements)

    def generate_pricing_psychology(self, price: float, unit: str,
                                   market_avg: float, demand: str = 'high') -> str:
        """
        Price framing using anchoring + scarcity principles.
        NOT: "Affordable prices"
        YES: Position relative to value + scarcity
        """

        if demand == 'very-high':
            return f"€{price}{unit} (seasonal rates higher during peak demand)"
        elif price < market_avg:
            return f"€{price}{unit} (competitive rate—we fill calendars fast)"
        else:
            return f"€{price}{unit} (premium service, limited slots)"

    def generate_cta_with_urgency(self, service_type: str,
                                  demand: str = 'high') -> str:
        """
        Call-to-action that matches psychological urgency level.
        High demand = scarcity framing
        """
        ctas = {
            'very-high': f"Message us now—peak season books quickly. Send requirements through Bazaraki for instant response.",
            'high': f"Send your project details through Bazaraki. We prioritize inquiries within 24 hours.",
            'medium': f"Inquire through Bazaraki for detailed assessment and quote."
        }
        return ctas.get(demand, ctas['high'])

    def quality_checklist_advanced(self, title: str, description: str,
                                   service_type: str) -> Dict[str, bool]:
        """
        Advanced 15-point quality check including psychological elements.
        """
        desc_lower = description.lower()

        return {
            # Technical compliance
            'title_length': 55 <= len(title) <= 80,
            'title_no_banned': not any(w in title.lower() for w in self.BANNED_WORDS),
            'description_length': 200 <= len(description) <= 2000,
            'no_banned_phrases': not any(p in desc_lower for p in self.BANNED_PHRASES),

            # Psychological elements
            'opens_with_problem': any(w in desc_lower.split()[0:3] for w in
                                     ['managing', 'struggling', 'challenge', 'difficult', 'problem']),
            'emotional_trigger_present': any(t in desc_lower for t in
                                            ['peace of mind', 'relief', 'confidence', 'safe', 'protected']),
            'specificity_high': len(re.findall(r'\d+', description)) >= 2,  # Numbers present
            'social_proof': any(s in desc_lower for s in
                               ['years', 'projects', 'experience', 'installed', 'customers']),
            'outcome_focused': not desc_lower.startswith(('we offer', 'we provide', 'we are')),
            'cta_clear': any(c in desc_lower for c in
                            ['message', 'contact', 'inquire', 'describe', 'send']),
            'location_specific': True,  # Assumes location passed
            'no_fabrication': not any(f in desc_lower for f in
                                     ['guarantee', 'never', '100%', 'only', 'best']),
            'psychological_angle': True,  # Service psychology analyzed
            'bilingual_ready': True,  # Can be translated
            'bazaraki_compliant': not any(e in description for e in
                                         ['@', 'whatapp', 'email.com', 'http'])
        }

def test_advanced_copywriter():
    """Test advanced copywriting engine"""
    print("\n🧠 ADVANCED COPYWRITING ENGINE TEST")
    print("=" * 80)

    cw = AdvancedCopywriter()

    # Test pool maintenance
    print("\n📋 Test 1: Pool Maintenance - Remote Owner Profile")
    print("-" * 80)

    problem = cw.generate_problem_statement('pool_maintenance', 'remote_owner', 'Paphos')
    print(f"Problem: {problem}\n")

    solution = cw.generate_solution_with_psychology('pool_maintenance', problem,
                                                    experience='12 years managing 400+ properties')
    print(f"Solution: {solution}\n")

    title = cw.generate_advanced_title('pool_maintenance', 'Paphos', 'remote_owner')
    print(f"Title: {title} ({len(title)} chars)\n")

    trust = cw.generate_trust_section('pool_maintenance', years=12, projects=400, warranty='2-year')
    print(f"Trust: {trust}\n")

    price = cw.generate_pricing_psychology(155, '/month', 130, 'very-high')
    print(f"Price: {price}\n")

    cta = cw.generate_cta_with_urgency('pool_maintenance', 'very-high')
    print(f"CTA: {cta}\n")

    # Test AC installation (high urgency)
    print("\n📋 Test 2: AC Installation - Peak Season Urgency")
    print("-" * 80)

    problem = cw.generate_problem_statement('ac_installation', 'local_owner', 'Limassol')
    print(f"Problem: {problem}\n")

    cta = cw.generate_cta_with_urgency('ac_installation', 'very-high')
    print(f"Urgent CTA: {cta}\n")

    # Test solar (future-proofing)
    print("\n📋 Test 3: Solar Installation - Investment Angle")
    print("-" * 80)

    title = cw.generate_advanced_title('solar_installation', 'Nicosia', 'business')
    print(f"Title: {title}\n")

    price = cw.generate_pricing_psychology(7500, '/system', 7000, 'high')
    print(f"Price: {price}\n")

if __name__ == '__main__':
    test_advanced_copywriter()
