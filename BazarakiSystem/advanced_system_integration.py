"""
ADVANCED BAZARAKI SYSTEM INTEGRATION v2
Combining Market Intelligence + Neuromarketing + Semantic Optimization
"""

from datetime import datetime
from typing import Dict, List
from market_intelligence import CyprusMarketAnalyzer
from advanced_copywriting_engine import AdvancedCopywriter

class AdvancedBazarakiSystem:
    """
    Next-generation advertisement generation combining:
    1. Cyprus market data (pricing, competition, seasonality)
    2. Psychological triggers (emotional drivers)
    3. Semantic SEO (buyer search intent)
    4. Buyer journey mapping (problem → solution → action)
    5. Economic pricing psychology
    """

    def __init__(self, db_path: str = None):
        print("\n🚀 INITIALIZING ADVANCED BAZARAKI SYSTEM v2")
        print("=" * 90)

        self.market_analyzer = CyprusMarketAnalyzer()
        self.copywriter = AdvancedCopywriter()

        print("✓ Market Intelligence Engine (Cyprus real-time data)")
        print("✓ Advanced Copywriter (Psychological + Semantic)")
        print("✓ Buyer Psychology Profiler")
        print("✓ Pricing Psychology Engine")
        print("✓ Multiservice Coverage (10+ categories)")
        print("\n" + "=" * 90)

    def generate_psychologically_optimized_ad(self, service_config: Dict) -> Dict:
        """
        Generate advertisement using complete psychological framework:
        1. Market research (what sells, at what price, with how much competition)
        2. Buyer psychology (emotional drivers, pain points)
        3. Copywriting (PASTOR + psychological triggers)
        4. Pricing psychology (anchoring, scarcity, value framing)
        5. SEO optimization (buyer search intent)
        """

        result = {
            'service_id': f"ADV_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'pipeline_status': 'processing',
            'advertisement': {},
            'market_analysis': {},
            'psychological_profile': {},
            'optimization_score': 0
        }

        service_type = service_config.get('type')
        subcategory = service_config.get('subcategory')
        location = service_config.get('location', 'paphos')
        buyer_type = service_config.get('buyer_type', 'general')
        years_experience = service_config.get('experience_years', 0)
        projects_count = service_config.get('projects_completed', 0)

        print(f"\n🎯 GENERATING PSYCHOLOGICALLY-OPTIMIZED AD")
        print("=" * 90)
        print(f"Service: {service_type} → {subcategory}")
        print(f"Location: {location.upper()}")
        print(f"Target Buyer: {buyer_type}")

        # STEP 1: Market Intelligence
        print(f"\n📊 STEP 1: Market Intelligence Analysis")
        print("-" * 90)

        market_rate = self.market_analyzer.get_market_rate(
            service_type, subcategory, location, 'Q2'
        )

        if 'error' in market_rate:
            result['pipeline_status'] = 'failed'
            result['error'] = market_rate['error']
            return result

        print(f"  Market Rate: €{market_rate['base_avg']:.2f} {market_rate['price_unit']}")
        print(f"  Recommended: €{market_rate['recommended_price']:.2f} {market_rate['price_unit']}")
        print(f"  Competitors: {market_rate['competitor_count']} (Saturation: {market_rate['market_saturation']})")
        print(f"  Demand Level: {market_rate['demand_level']}")
        print(f"  Seasonal Boost: {market_rate['seasonality_boost']}")

        result['market_analysis'] = market_rate

        # STEP 2: Buyer Psychology Analysis
        print(f"\n🧠 STEP 2: Buyer Psychology Profiling")
        print("-" * 90)

        psychology = self.copywriter.analyze_service_psychology(service_type)
        print(f"  Psychology: {psychology['psychology']}")
        print(f"  Pain Point: {psychology['pain_point']}")
        print(f"  Emotional Need: {psychology['emotional_need']}")
        print(f"  Primary Trigger: {psychology['trigger'].value}")
        print(f"  Time Sensitivity: {psychology['time_sensitivity']}")
        print(f"  Decision Factor: {psychology['decision_factor']}")

        result['psychological_profile'] = psychology

        # STEP 3: Problem Statement (Psychological Opening)
        print(f"\n💭 STEP 3: Psychological Problem Statement")
        print("-" * 90)

        problem = self.copywriter.generate_problem_statement(
            service_type, buyer_type, location
        )
        print(f"  {problem}")

        # STEP 4: Solution with Psychology
        print(f"\n✅ STEP 4: Solution Statement (Outcome-Focused)")
        print("-" * 90)

        experience_text = f"{years_experience} years, {projects_count}+ projects" if years_experience > 0 else ""
        solution = self.copywriter.generate_solution_with_psychology(
            service_type, problem, experience_text
        )
        print(f"  {solution[:200]}...")

        # STEP 5: Advanced Title Generation
        print(f"\n✍️  STEP 5: Psychologically-Optimized Title")
        print("-" * 90)

        title = self.copywriter.generate_advanced_title(
            service_type, location, buyer_type,
            service_config.get('profitability', 'high')
        )
        print(f"  {title}")
        print(f"  Length: {len(title)} chars ✓")

        # STEP 6: Trust Building Section
        print(f"\n🛡️  STEP 6: Social Proof & Trust Signals")
        print("-" * 90)

        trust = self.copywriter.generate_trust_section(
            service_type,
            years_experience,
            projects_count,
            service_config.get('warranty', '2-year')
        )
        print(f"  {trust}")

        # STEP 7: Pricing Psychology Framing
        print(f"\n💰 STEP 7: Pricing Psychology (Anchoring + Scarcity)")
        print("-" * 90)

        price_framing = self.copywriter.generate_pricing_psychology(
            market_rate['recommended_price'],
            market_rate['price_unit'],
            market_rate['base_avg'],
            market_rate['demand_level']
        )
        print(f"  {price_framing}")

        # STEP 8: Call-to-Action with Urgency Matching
        print(f"\n🎯 STEP 8: Psychologically-Matched CTA")
        print("-" * 90)

        cta = self.copywriter.generate_cta_with_urgency(
            service_type,
            market_rate['demand_level']
        )
        print(f"  {cta}")

        # STEP 9: Quality & Psychological Checklist
        print(f"\n✅ STEP 9: Advanced Quality Checklist")
        print("-" * 90)

        full_description = f"{problem}\n\n{solution}\n\n{trust}\n\n{price_framing}"

        checklist = self.copywriter.quality_checklist_advanced(title, full_description, service_type)
        passed = sum(1 for v in checklist.values() if v)

        print(f"  Quality Score: {passed}/{len(checklist)}")
        for check, status in list(checklist.items())[:8]:
            print(f"    {'✓' if status else '✗'} {check}")

        # Assemble final ad
        result['advertisement'] = {
            'service_id': result['service_id'],
            'title': title,
            'problem_statement': problem,
            'solution_statement': solution,
            'trust_signals': trust,
            'pricing': price_framing,
            'cta': cta,
            'service_type': service_type,
            'subcategory': subcategory,
            'location': location,
            'buyer_profile': buyer_type,
            'psychological_trigger': psychology['trigger'].value,
            'time_sensitivity': psychology['time_sensitivity'],
            'quality_score': f"{passed}/{len(checklist)}",
            'status': 'approved' if passed >= len(checklist) - 2 else 'needs_review'
        }

        result['pipeline_status'] = 'success'
        result['optimization_score'] = (passed / len(checklist)) * 100

        print(f"\n✨ FINAL RESULT: {result['optimization_score']:.1f}% Optimization Score")
        print(f"Status: {result['advertisement']['status'].upper()}")

        return result

    def generate_example_ad(self, service_type: str, location: str, buyer_type: str):
        """Generate a complete example ad"""

        service_config = {
            'type': service_type,
            'subcategory': self._get_subcategory(service_type),
            'location': location,
            'buyer_type': buyer_type,
            'experience_years': 12,
            'projects_completed': 400,
            'warranty': '2-year'
        }

        return self.generate_psychologically_optimized_ad(service_config)

    def _get_subcategory(self, service_type: str) -> str:
        """Map service type to default subcategory"""
        mapping = {
            'pool_services': 'pool_maintenance',
            'hvac_services': 'ac_installation',
            'solar_renewable': 'solar_installation',
            'garden_landscaping': 'garden_maintenance'
        }
        return mapping.get(service_type, service_type)

def main():
    """Test advanced system with pool services example"""
    print("\n" + "=" * 90)
    print("BAZARAKI ADVANCED SYSTEM v2 - POOL MAINTENANCE EXAMPLE")
    print("=" * 90)

    system = AdvancedBazarakiSystem()

    # Generate pool maintenance ad for remote owner
    result = system.generate_example_ad(
        service_type='pool_services',
        location='paphos',
        buyer_type='remote_owner'
    )

    print("\n\n" + "=" * 90)
    print("📄 GENERATED ADVERTISEMENT")
    print("=" * 90)

    if result['pipeline_status'] == 'success':
        ad = result['advertisement']
        print(f"\n🎯 TITLE:\n{ad['title']}\n")
        print(f"💭 OPENING (Problem):\n{ad['problem_statement']}\n")
        print(f"✅ SOLUTION:\n{ad['solution_statement']}\n")
        print(f"🛡️  TRUST:\n{ad['trust_signals']}\n")
        print(f"💰 PRICING:\n{ad['pricing']}\n")
        print(f"🎯 CALL-TO-ACTION:\n{ad['cta']}\n")
        print(f"Quality: {ad['quality_score']} | Optimization: {result['optimization_score']:.1f}%")

    print("\n" + "=" * 90)

if __name__ == '__main__':
    main()
