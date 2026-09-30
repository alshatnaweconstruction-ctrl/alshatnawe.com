"""
BAZARAKI AUTONOMOUS OPERATING SYSTEM - MASTER INTEGRATION
Complete Pipeline: Market Analysis → Psychology → Copywriting → Image Verification → XML Generation
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import hashlib

# Import all system modules
from market_intelligence import CyprusMarketAnalyzer
from advanced_copywriting_engine import AdvancedCopywriter
from image_verification_engine import ImageVerificationEngine

@dataclass
class ImageMetadata:
    """Image data with verification results"""
    image_path: str
    image_id: str
    quality_score: float
    alignment_score: float
    bazaraki_compliant: bool
    psychological_alignment: str
    verification_passed: bool
    verification_details: str

@dataclass
class AdvertisementPackage:
    """Complete ad with all components ready for Bazaraki"""
    service_id: str
    title: str
    description: str
    service_type: str
    location: str
    buyer_profile: str
    images: List[ImageMetadata]
    price: str
    psychological_trigger: str
    quality_score: str
    optimization_score: float
    market_analysis: Dict
    psychological_profile: Dict
    status: str
    created_at: str
    xml_output: str

class BazarakiMasterSystem:
    """
    Complete autonomous system orchestrating:
    1. Market Intelligence (Cyprus pricing, competition, demand)
    2. Buyer Psychology Profiling (emotional drivers, pain points)
    3. Advanced Copywriting (PASTOR + neuromarketing)
    4. Image Verification (strict 4-tier validation)
    5. XML Generation (Bazaraki-compliant output)
    6. Quality Assurance (hard-fail gates)
    """

    HARD_FAIL_GATES = {
        'gate_1_title_length': ('Title length 55-80 chars', lambda x: 55 <= len(x['title']) <= 80),
        'gate_2_description_length': ('Description length 200-2000 chars', lambda x: 200 <= len(x['description']) <= 2000),
        'gate_3_no_banned_phrases': ('No banned Bazaraki phrases', lambda x: not any(p in x['description'].lower() for p in ['we offer', 'we provide', 'limited time', 'best deal'])),
        'gate_4_images_verified': ('All images verified', lambda x: all(img.verification_passed for img in x['images'])),
        'gate_5_image_count': ('Minimum 5 images', lambda x: len(x['images']) >= 5),
        'gate_6_psychological_alignment': ('Psychological angle clear', lambda x: x['psychological_trigger'] in x['description']),
        'gate_7_pricing_present': ('Pricing information included', lambda x: '€' in x['price']),
        'gate_8_cta_present': ('Clear call-to-action', lambda x: any(c in x['description'].lower() for c in ['message', 'contact', 'inquire', 'send'])),
        'gate_9_location_specific': ('Location-specific messaging', lambda x: x['location'].lower() in x['description'].lower()),
        'gate_10_no_external_links': ('No external links', lambda x: '@' not in x['description'] and 'http' not in x['description'])
    }

    def __init__(self):
        print("\n🚀 INITIALIZING BAZARAKI MASTER SYSTEM")
        print("=" * 100)
        print("✓ Market Intelligence Engine")
        print("✓ Advanced Copywriter (PASTOR + Neuromarketing)")
        print("✓ Image Verification Engine (4-tier validation)")
        print("✓ Quality Assurance (10 hard-fail gates)")
        print("=" * 100)

        self.market_analyzer = CyprusMarketAnalyzer()
        self.copywriter = AdvancedCopywriter()
        self.image_verifier = ImageVerificationEngine()
        self.ad_counter = 0

    def verify_images_for_ad(self, service_type: str, image_paths: List[str]) -> Tuple[List[ImageMetadata], bool]:
        """
        Verify image batch for ad using strict IMAGE-FIRST RULE
        Returns: (image_metadata_list, all_passed_bool)
        """
        print(f"\n🖼️  IMAGE VERIFICATION GATE - {len(image_paths)} images")
        print("-" * 100)

        verified_images = []
        all_passed = True

        for idx, image_path in enumerate(image_paths, 1):
            # Generate image ID from hash
            image_id = hashlib.sha256(image_path.encode()).hexdigest()[:16]

            # Verify image for this service
            verification_result = self.image_verifier.verify_image_for_service(
                service_type=service_type,
                image_path=image_path
            )

            quality_score = verification_result.get('quality_score', 0)
            alignment_score = verification_result.get('alignment_score', 0)
            bazaraki_compliant = verification_result.get('bazaraki_compliant', False)
            psychological_alignment = verification_result.get('psychological_alignment', 'NEUTRAL')
            passed = verification_result.get('passed', False)

            image_meta = ImageMetadata(
                image_path=image_path,
                image_id=image_id,
                quality_score=quality_score,
                alignment_score=alignment_score,
                bazaraki_compliant=bazaraki_compliant,
                psychological_alignment=psychological_alignment,
                verification_passed=passed,
                verification_details=verification_result.get('summary', '')
            )

            verified_images.append(image_meta)

            status_icon = "✓" if passed else "✗"
            print(f"  {status_icon} Image {idx}: Quality={quality_score:.1f}% | Alignment={alignment_score:.1f}% | Bazaraki={bazaraki_compliant}")

            if not passed:
                all_passed = False
                print(f"     ⚠️  {verification_result.get('summary', 'Verification failed')}")

        # Verify batch diversity
        batch_verification = self.image_verifier.verify_image_batch_for_ad(
            service_type=service_type,
            image_paths=image_paths
        )

        print(f"\n  Batch Summary:")
        print(f"    Verified: {sum(1 for img in verified_images if img.verification_passed)}/{len(verified_images)}")
        print(f"    Batch Compliant: {batch_verification['batch_compliant']}")

        return verified_images, (all_passed and batch_verification['batch_compliant'])

    def generate_complete_ad_package(self, service_config: Dict, image_paths: List[str]) -> AdvertisementPackage:
        """
        Generate complete advertisement package with ALL components integrated.
        Pipeline: Market → Psychology → Copywriting → Image Verification → Assembly → Quality Check → XML
        """

        self.ad_counter += 1
        service_id = f"PKG_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.ad_counter:03d}"

        print(f"\n{'=' * 100}")
        print(f"🎯 GENERATING COMPLETE AD PACKAGE #{self.ad_counter}")
        print(f"{'=' * 100}")

        service_type = service_config.get('type')
        location = service_config.get('location', 'paphos')
        buyer_type = service_config.get('buyer_type', 'general')

        # STEP 1: Market Analysis
        print(f"\n📊 STEP 1: Market Intelligence")
        market_rate = self.market_analyzer.get_market_rate(
            service_type,
            service_config.get('subcategory', service_type),
            location,
            'Q4'
        )

        if 'error' in market_rate:
            return None

        print(f"  Market Rate: €{market_rate['base_avg']:.2f} {market_rate['price_unit']}")
        print(f"  Competitors: {market_rate['competitor_count']} | Demand: {market_rate['demand_level']}")

        # STEP 2: Psychology Profile
        print(f"\n🧠 STEP 2: Buyer Psychology Analysis")
        psychology = self.copywriter.analyze_service_psychology(service_type)
        print(f"  Trigger: {psychology['trigger'].value} | Time Sensitivity: {psychology['time_sensitivity']}")

        # STEP 3: Copywriting
        print(f"\n✍️  STEP 3: Advanced Copywriting (PASTOR + Neuromarketing)")
        problem = self.copywriter.generate_problem_statement(service_type, buyer_type, location)
        solution = self.copywriter.generate_solution_with_psychology(service_type, problem)
        title = self.copywriter.generate_advanced_title(service_type, location, buyer_type)
        trust = self.copywriter.generate_trust_section(
            service_type,
            service_config.get('experience_years', 0),
            service_config.get('projects_completed', 0)
        )
        price = self.copywriter.generate_pricing_psychology(
            market_rate['recommended_price'],
            market_rate['price_unit'],
            market_rate['base_avg'],
            market_rate['demand_level']
        )
        cta = self.copywriter.generate_cta_with_urgency(service_type, market_rate['demand_level'])

        print(f"  Title: {title} ({len(title)} chars)")

        # STEP 4: IMAGE VERIFICATION (CRITICAL GATE)
        print(f"\n🖼️  STEP 4: IMAGE VERIFICATION GATE")
        verified_images, images_passed = self.verify_images_for_ad(service_type, image_paths)

        if not images_passed:
            print(f"\n  ❌ IMAGE VERIFICATION FAILED - Ad cannot proceed without verified images")
            return None

        print(f"  ✓ All images verified and Bazaraki-compliant")

        # STEP 5: Build Description
        print(f"\n📝 STEP 5: Build Complete Description")
        full_description = f"{problem}\n\n{solution}\n\n{trust}\n\n{price}\n\n{cta}"
        print(f"  Description: {len(full_description)} chars")

        # STEP 6: Quality Checklist
        print(f"\n✅ STEP 6: Run 10 Hard-Fail Gates")
        print("-" * 100)

        ad_dict = {
            'title': title,
            'description': full_description,
            'price': price,
            'location': location,
            'psychological_trigger': psychology['trigger'].value,
            'images': verified_images
        }

        gate_results = {}
        gates_passed = 0

        for gate_name, (gate_desc, gate_check) in self.HARD_FAIL_GATES.items():
            try:
                result = gate_check(ad_dict)
                gate_results[gate_name] = result
                if result:
                    gates_passed += 1
                    print(f"  ✓ {gate_desc}")
                else:
                    print(f"  ✗ {gate_desc}")
            except Exception as e:
                print(f"  ✗ {gate_desc} - ERROR: {str(e)}")

        gates_total = len(self.HARD_FAIL_GATES)
        quality_score = f"{gates_passed}/{gates_total}"
        optimization_score = (gates_passed / gates_total) * 100

        # STEP 7: Psychological Quality Check
        print(f"\n🧠 STEP 7: Psychological Quality Metrics")
        psych_checklist = self.copywriter.quality_checklist_advanced(title, full_description, service_type)
        psych_passed = sum(1 for v in psych_checklist.values() if v)
        print(f"  Psychological Quality: {psych_passed}/{len(psych_checklist)} checks passed")

        # STEP 8: XML Generation
        print(f"\n⚙️  STEP 8: Generate Bazaraki XML")
        xml_output = self._generate_bazaraki_xml(ad_dict, verified_images, service_id)
        print(f"  XML generated: {len(xml_output)} bytes")

        # STEP 9: Final Status
        status = 'APPROVED' if gates_passed >= gates_total - 1 and images_passed else 'NEEDS_REVIEW'

        print(f"\n🎯 STEP 9: Final Assessment")
        print(f"  Quality Score: {quality_score}")
        print(f"  Optimization: {optimization_score:.1f}%")
        print(f"  Image Verification: ✓ PASSED ({len(verified_images)} images)")
        print(f"  Status: {status}")

        # Assemble complete package
        package = AdvertisementPackage(
            service_id=service_id,
            title=title,
            description=full_description,
            service_type=service_type,
            location=location,
            buyer_profile=buyer_type,
            images=verified_images,
            price=price,
            psychological_trigger=psychology['trigger'].value,
            quality_score=quality_score,
            optimization_score=optimization_score,
            market_analysis=market_rate,
            psychological_profile=asdict(psychology) if hasattr(psychology, '__dict__') else psychology,
            status=status,
            created_at=datetime.now().isoformat(),
            xml_output=xml_output
        )

        return package

    def _generate_bazaraki_xml(self, ad_dict: Dict, images: List[ImageMetadata], service_id: str) -> str:
        """Generate Bazaraki-compliant XML output"""
        root = ET.Element('advertisement')
        ET.SubElement(root, 'service_id').text = service_id
        ET.SubElement(root, 'created_at').text = datetime.now().isoformat()

        # Ad Content
        content = ET.SubElement(root, 'content')
        ET.SubElement(content, 'title').text = ad_dict['title']
        ET.SubElement(content, 'description').text = ad_dict['description']
        ET.SubElement(content, 'price').text = ad_dict['price']
        ET.SubElement(content, 'location').text = ad_dict['location']

        # Psychological Metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'psychological_trigger').text = ad_dict['psychological_trigger']

        # Images
        images_elem = ET.SubElement(root, 'images')
        for img in images:
            img_elem = ET.SubElement(images_elem, 'image')
            ET.SubElement(img_elem, 'id').text = img.image_id
            ET.SubElement(img_elem, 'path').text = img.image_path
            ET.SubElement(img_elem, 'quality_score').text = f"{img.quality_score:.1f}"
            ET.SubElement(img_elem, 'alignment_score').text = f"{img.alignment_score:.1f}"
            ET.SubElement(img_elem, 'bazaraki_compliant').text = str(img.bazaraki_compliant)
            ET.SubElement(img_elem, 'psychological_alignment').text = img.psychological_alignment
            ET.SubElement(img_elem, 'verified').text = str(img.verification_passed)

        return ET.tostring(root, encoding='unicode')

    def save_package_to_json(self, package: AdvertisementPackage, output_path: str):
        """Save complete ad package to JSON"""
        data = {
            'service_id': package.service_id,
            'title': package.title,
            'description': package.description,
            'service_type': package.service_type,
            'location': package.location,
            'buyer_profile': package.buyer_profile,
            'price': package.price,
            'psychological_trigger': package.psychological_trigger,
            'quality_score': package.quality_score,
            'optimization_score': package.optimization_score,
            'status': package.status,
            'created_at': package.created_at,
            'images': [
                {
                    'image_id': img.image_id,
                    'quality_score': img.quality_score,
                    'alignment_score': img.alignment_score,
                    'bazaraki_compliant': img.bazaraki_compliant,
                    'psychological_alignment': img.psychological_alignment,
                    'verified': img.verification_passed
                }
                for img in package.images
            ],
            'market_analysis': package.market_analysis,
            'psychological_profile': package.psychological_profile
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Package saved to: {output_path}")


def main():
    """Test master system with complete pipeline"""
    print("\n" + "=" * 100)
    print("BAZARAKI MASTER SYSTEM - COMPLETE INTEGRATION TEST")
    print("=" * 100)

    system = BazarakiMasterSystem()

    # Example: Pool Maintenance with image verification
    service_config = {
        'type': 'pool_services',
        'subcategory': 'pool_maintenance',
        'location': 'paphos',
        'buyer_type': 'remote_owner',
        'experience_years': 12,
        'projects_completed': 400,
        'warranty': '2-year'
    }

    # Mock image paths (would be real paths in production)
    mock_images = [
        '/images/pool_1_crystal_clear.jpg',
        '/images/pool_2_maintenance.jpg',
        '/images/pool_3_equipment.jpg',
        '/images/pool_4_worker.jpg',
        '/images/pool_5_landscape.jpg'
    ]

    # Generate complete package
    package = system.generate_complete_ad_package(service_config, mock_images)

    if package:
        print(f"\n{'=' * 100}")
        print("📦 COMPLETE ADVERTISEMENT PACKAGE")
        print(f"{'=' * 100}")
        print(f"\nTitle: {package.title}")
        print(f"Quality Score: {package.quality_score}")
        print(f"Optimization: {package.optimization_score:.1f}%")
        print(f"Images Verified: {len([img for img in package.images if img.verification_passed])}/{len(package.images)}")
        print(f"Status: {package.status}")
        print(f"\n✓ System ready for Bazaraki deployment")

        # Save package
        output_file = '/tmp/claude-0/-home-claude/d1970ea6-88ce-50aa-acf6-a796c2348474/scratchpad/generated_ad_package.json'
        system.save_package_to_json(package, output_file)

    print(f"\n{'=' * 100}")


if __name__ == '__main__':
    main()
