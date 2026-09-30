"""
BAZARAKI AUTONOMOUS SYSTEM INTEGRATION
Master orchestrator bringing all modules together
"""

import json
from datetime import datetime
from typing import Dict, List
from bazaraki_system import (
    ServiceInventoryLedger, ImageDeduplicationEngine, SupervisorOrchestrator,
    LearningSystem, AutonomousDailyLoop, ServiceListing, AdStatus
)
from copywriting_engine import PASTORCopywriter, AdCopy
from market_intelligence import CyprusMarketAnalyzer

class BazarakiAutonomousSystem:
    """
    Complete BAZARAKI AUTONOMOUS OPERATING SYSTEM
    Orchestrates all components for end-to-end advertisement generation and publishing
    """

    def __init__(self, db_path: str):
        print("\n🚀 INITIALIZING BAZARAKI AUTONOMOUS SYSTEM")
        print("=" * 80)

        # Initialize core modules
        self.ledger = ServiceInventoryLedger(db_path)
        self.dedup_engine = ImageDeduplicationEngine(self.ledger)
        self.supervisor = SupervisorOrchestrator(self.ledger, self.dedup_engine)
        self.learning_system = LearningSystem(self.ledger)
        self.daily_loop = AutonomousDailyLoop(self.ledger, self.supervisor, self.learning_system)

        # Initialize specialized modules
        self.copywriter = PASTORCopywriter()
        self.market_analyzer = CyprusMarketAnalyzer()

        self.db_path = db_path
        self.session_id = datetime.now().isoformat()
        self.daily_generated_ads = []

        print("✓ Service Inventory Ledger initialized")
        print("✓ Image Deduplication Engine initialized")
        print("✓ Multi-Agent Orchestrator initialized")
        print("✓ PASTOR Copywriting Engine initialized")
        print("✓ Cyprus Market Intelligence initialized")
        print("✓ Continuous Learning System initialized")
        print("✓ Autonomous Daily Loop initialized")
        print("\n" + "=" * 80)

    def generate_service_advertisement(self, service_config: Dict) -> Dict:
        """
        PHASE: COMPLETE ADVERTISEMENT GENERATION
        Takes service config and generates market-optimized, compliance-verified ad
        """

        result = {
            'service_id': service_config.get('id'),
            'timestamp': datetime.now().isoformat(),
            'pipeline_status': 'processing',
            'generated_ads': [],
            'warnings': [],
            'errors': []
        }

        # Extract service details
        service_type = service_config.get('type')  # e.g., 'plasterboard', 'painting'
        subcategory = service_config.get('subcategory')  # e.g., 'partition_walls'
        location = service_config.get('location', 'paphos')
        unique_aspect = service_config.get('unique_aspect', 'quality work')
        problem_statement = service_config.get('problem', '')
        solution_statement = service_config.get('solution', '')

        # STEP 1: Market Intelligence Research
        print(f"\n📊 STEP 1: Market Intelligence - {service_type} in {location}")
        print("-" * 80)

        market_rate = self.market_analyzer.get_market_rate(
            service_type, subcategory, location, 'Q2'
        )

        if 'error' in market_rate:
            result['errors'].append(market_rate['error'])
            result['pipeline_status'] = 'failed'
            return result

        competition = self.market_analyzer.analyze_competitor_landscape(service_type, location)
        pricing_analysis = self.market_analyzer.get_pricing_commercial_analysis(
            service_type, subcategory, location
        )

        recommended_price = market_rate['recommended_price']
        price_unit = market_rate['price_unit']

        print(f"  Market Rate: €{market_rate['base_avg']:.2f} {price_unit}")
        print(f"  Recommended Price: €{recommended_price:.2f} {price_unit}")
        print(f"  Competitors: {competition['estimated_competitors']}")
        print(f"  Saturation: {market_rate['market_saturation']}")
        print(f"  Demand: {market_rate['demand_level']}")

        # STEP 2: Deduplication Check
        print(f"\n🔍 STEP 2: Deduplication Check")
        print("-" * 80)

        canonical_name = f"{service_type}_{subcategory}_{location}".lower()
        duplicate = self.ledger.check_duplicate_service(canonical_name)

        if duplicate:
            result['warnings'].append(f"Similar service already exists: {duplicate}")
            print(f"  ⚠️  Duplicate detected: {duplicate}")
        else:
            print(f"  ✓ Service is unique")

        # STEP 3: Copywriting (English Title)
        print(f"\n✍️  STEP 3: Copywriting Engine - Title Generation")
        print("-" * 80)

        english_title = self.copywriter.generate_english_title(service_type, location, unique_aspect)
        title_valid, title_errors = self.copywriter.validate_title(english_title)

        if not title_valid:
            # Regenerate with stricter constraints
            english_title = f"Professional {service_type} services in {location}: {unique_aspect}"
            title_valid, title_errors = self.copywriter.validate_title(english_title)

        print(f"  Title: {english_title}")
        print(f"  Length: {len(english_title)} chars | Valid: {'✓' if title_valid else '✗'}")

        if title_errors:
            result['warnings'].extend(title_errors)

        # STEP 4: Copywriting (Description)
        print(f"\n✍️  STEP 4: Copywriting Engine - Description Generation")
        print("-" * 80)

        english_description = self.copywriter.generate_english_description(
            problem_statement or f"Need professional {service_type} services?",
            solution_statement or f"We provide expert {service_type} solutions.",
            f"{location} and surrounding areas"
        )

        desc_valid, desc_errors = self.copywriter.validate_description(english_description)
        print(f"  Description length: {len(english_description)} chars | Valid: {'✓' if desc_valid else '✗'}")

        if desc_errors:
            result['warnings'].extend(desc_errors)

        # STEP 5: Search Terms Generation
        print(f"\n🔎 STEP 5: Search Terms Generation")
        print("-" * 80)

        search_terms = self.copywriter.generate_search_terms(
            service_type, location,
            [subcategory.replace('_', ' '), f"Cyprus {service_type}"]
        )

        print(f"  Generated {len(search_terms)} terms: {', '.join(search_terms[:4])}...")

        # STEP 6: Quality Checklist
        print(f"\n✅ STEP 6: Quality Checklist")
        print("-" * 80)

        test_ad = AdCopy(
            language='en',
            title=english_title,
            description=english_description,
            search_terms=search_terms
        )

        checklist = self.copywriter.quality_checklist(test_ad)
        passed = sum(1 for v in checklist.values() if v)

        print(f"  Quality Score: {passed}/{len(checklist)}")
        for check, status in checklist.items():
            print(f"    {'✓' if status else '✗'} {check}")

        if passed < len(checklist) - 2:  # Allow max 2 failures
            result['errors'].append("Quality checklist failed too many items")
            result['pipeline_status'] = 'failed'
            return result

        # STEP 7: IMAGE-FIRST RULE ENFORCEMENT
        print(f"\n🖼️  STEP 7: IMAGE-FIRST RULE - Checking Image Requirements")
        print("-" * 80)

        image_ids = service_config.get('image_ids', [])
        if not image_ids or len(image_ids) < 1:
            result['errors'].append("NO ADVERTISEMENT MAY ENTER PUBLISH QUEUE WITHOUT VERIFIED MATCHING IMAGES")
            result['pipeline_status'] = 'failed'
            print("  ✗ HARD FAIL: No images provided")
            return result

        print(f"  ✓ {len(image_ids)} image(s) provided")

        # STEP 8: Bazaraki Compliance Check
        print(f"\n⚖️  STEP 8: Bazaraki Policy Compliance")
        print("-" * 80)

        compliance_checks = {
            'no_fabricated_claims': not any(claim in english_description.lower() for claim in ['guarantee', 'never fails', '100% success']),
            'no_banned_words': not any(w in english_title.lower() for w in self.copywriter.BANNED_WORDS),
            'location_specific': location.lower() in english_title.lower() or location.lower() in english_description.lower(),
            'trust_signals': any(sig in english_description.lower() for sig in ['professional', 'experienced', 'certified'])
        }

        all_compliant = all(compliance_checks.values())
        for check, status in compliance_checks.items():
            print(f"  {'✓' if status else '✗'} {check}")

        if not all_compliant:
            result['errors'].append("Compliance checks failed")
            result['pipeline_status'] = 'failed'
            return result

        # STEP 9: Final Advertisement Object
        print(f"\n📦 STEP 9: Assembling Final Advertisement")
        print("-" * 80)

        service_id = f"SVC_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        final_ad = {
            'service_id': service_id,
            'canonical_name': canonical_name,
            'language': 'en',
            'title': english_title,
            'description': english_description,
            'category': service_type,
            'subcategory': subcategory,
            'location': location,
            'price': recommended_price,
            'price_unit': price_unit,
            'search_terms': search_terms,
            'image_count': len(image_ids),
            'image_ids': image_ids,
            'market_rate': market_rate['base_avg'],
            'competitor_count': competition['estimated_competitors'],
            'demand': market_rate['demand_level'],
            'saturation': market_rate['market_saturation'],
            'quality_score': passed,
            'compliance_status': 'approved',
            'generated_at': datetime.now().isoformat(),
            'status': 'pending_approval'
        }

        result['generated_ads'].append(final_ad)
        result['pipeline_status'] = 'success'

        print(f"  Service ID: {service_id}")
        print(f"  Title: {english_title[:60]}...")
        print(f"  Price: €{recommended_price:.2f} {price_unit}")
        print(f"  Status: READY FOR APPROVAL ✓")

        self.daily_generated_ads.append(final_ad)

        return result

    def generate_bazaraki_xml(self, ad: Dict) -> str:
        """Generate Bazaraki-compliant XML from advertisement"""
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<advertisement>
    <external_id>{ad['service_id']}</external_id>
    <title>{self._escape_xml(ad['title'])}</title>
    <description>{self._escape_xml(ad['description'])}</description>
    <category>{ad['category']}</category>
    <subcategory>{ad['subcategory']}</subcategory>
    <location>{ad['location']}</location>
    <price>{ad['price']}</price>
    <price_unit>{ad['price_unit']}</price_unit>
    <images count="{ad['image_count']}">
        {''.join(f'<image id="{img_id}" />' for img_id in ad['image_ids'][:5])}
    </images>
    <search_terms>{','.join(ad['search_terms'])}</search_terms>
    <status>pending</status>
    <generated_at>{ad['generated_at']}</generated_at>
</advertisement>'''
        return xml

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))

    def generate_daily_batch(self, service_configs: List[Dict], target_count: int = 10) -> Dict:
        """
        Generate daily batch of advertisements (up to 100/day)
        Each ad passes through complete quality pipeline before being queued
        """
        print(f"\n\n{'='*80}")
        print(f"🚀 DAILY BATCH GENERATION - Target: {target_count} ads")
        print(f"{'='*80}")

        batch_result = {
            'timestamp': datetime.now().isoformat(),
            'target_count': target_count,
            'generated_count': 0,
            'failed_count': 0,
            'ads': [],
            'summary': {}
        }

        for idx, config in enumerate(service_configs[:target_count], 1):
            print(f"\n\n{'─'*80}")
            print(f"📌 ADVERTISEMENT #{idx}/{target_count}")
            print(f"{'─'*80}")

            result = self.generate_service_advertisement(config)

            if result['pipeline_status'] == 'success':
                batch_result['generated_count'] += 1
                batch_result['ads'].extend(result['generated_ads'])
            else:
                batch_result['failed_count'] += 1
                print(f"\n  ✗ GENERATION FAILED")
                if result['errors']:
                    for err in result['errors']:
                        print(f"    - {err}")

        batch_result['summary'] = {
            'success_rate': f"{(batch_result['generated_count'] / target_count * 100):.1f}%",
            'ads_generated': batch_result['generated_count'],
            'ads_failed': batch_result['failed_count'],
            'ready_for_publication': batch_result['generated_count']
        }

        return batch_result

def test_complete_system():
    """Test complete system with sample data"""
    print("\n" + "="*80)
    print("🧪 COMPLETE SYSTEM TEST - End-to-End Advertisement Generation")
    print("="*80)

    db_path = '/tmp/claude-0/-home-claude/d1970ea6-88ce-50aa-acf6-a796c2348474/scratchpad/bazaraki_production.db'
    system = BazarakiAutonomousSystem(db_path)

    # Sample service configurations
    sample_services = [
        {
            'id': 'SVC_001',
            'type': 'plasterboard',
            'subcategory': 'partition_walls',
            'location': 'paphos',
            'unique_aspect': 'expert interior walls',
            'problem': 'Need to reconfigure your space with new walls?',
            'solution': 'Professional partition wall installation with certified workmanship.',
            'image_ids': ['img_001', 'img_002', 'img_003']
        },
        {
            'id': 'SVC_002',
            'type': 'painting',
            'subcategory': 'interior_painting',
            'location': 'paphos',
            'unique_aspect': 'residential interior finishes',
            'problem': 'Your interior needs fresh paint and color refresh?',
            'solution': 'Expert interior painting with professional finishing.',
            'image_ids': ['img_004', 'img_005']
        },
        {
            'id': 'SVC_003',
            'type': 'tiling',
            'subcategory': 'floor_tiling',
            'location': 'limassol',
            'unique_aspect': 'high-quality ceramic installation',
            'problem': 'Looking for professional floor tiling work?',
            'solution': 'Specialist tile installation with premium materials.',
            'image_ids': ['img_006', 'img_007', 'img_008']
        }
    ]

    # Generate batch
    batch_result = system.generate_daily_batch(sample_services, target_count=3)

    # Print summary
    print(f"\n\n{'='*80}")
    print("📊 BATCH GENERATION SUMMARY")
    print(f"{'='*80}")
    print(f"Generated: {batch_result['generated_count']}/{batch_result['target_count']}")
    print(f"Failed: {batch_result['failed_count']}")
    print(f"Success Rate: {batch_result['summary']['success_rate']}")

    # Show first generated ad
    if batch_result['ads']:
        print(f"\n✓ First Generated Advertisement:")
        ad = batch_result['ads'][0]
        print(f"  Service ID: {ad['service_id']}")
        print(f"  Title: {ad['title']}")
        print(f"  Price: €{ad['price']:.2f} {ad['price_unit']}")
        print(f"  Quality Score: {ad['quality_score']}/10")
        print(f"  Status: {ad['status']}")

        # Generate XML
        print(f"\n📄 Generated Bazaraki XML:")
        xml = system.generate_bazaraki_xml(ad)
        print(xml[:500] + "...")

if __name__ == '__main__':
    test_complete_system()
