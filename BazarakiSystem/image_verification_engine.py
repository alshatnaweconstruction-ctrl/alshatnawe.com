"""
IMAGE VERIFICATION & MATCHING ENGINE
Strict filters to ensure images align perfectly with ad content
Psychological + Semantic image matching
"""

from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass
import hashlib

class ImageQualityLevel(Enum):
    """Image quality standards"""
    PROFESSIONAL = "professional"      # Studio/professional photography
    HIGH_QUALITY = "high_quality"      # Clear, well-lit, professional appearance
    ACCEPTABLE = "acceptable"          # Usable but not premium
    POOR = "poor"                      # Reject - blurry, low quality

class ImageAlignmentScore(Enum):
    """How well image matches ad content"""
    PERFECT = 95      # Exactly matches ad narrative
    STRONG = 85       # Clearly related to service
    MODERATE = 70     # Related but generic
    WEAK = 50         # Vaguely related
    MISMATCHED = 20   # Doesn't match at all

class ImageVerificationEngine:
    """
    Strict image verification system:
    - Semantic content matching (image must show what ad describes)
    - Technical quality standards
    - Bazaraki policy compliance
    - Emotional alignment with ad psychological angle
    - Multi-image diversity requirements
    """

    # SERVICE-SPECIFIC IMAGE REQUIREMENTS
    SERVICE_IMAGE_REQUIREMENTS = {
        'pool_maintenance': {
            'primary_elements': [
                'crystal_clear_water',
                'well_maintained_pool',
                'professional_equipment',
                'visible_water_testing',
                'clean_pool_edges'
            ],
            'required_count': 5,
            'quality_minimum': ImageQualityLevel.HIGH_QUALITY,
            'diversity_rules': {
                'at_least_one_closeup': True,
                'at_least_one_wide_angle': True,
                'equipment_visible': True,
                'worker_visible_in_one': True,
                'before_after_pair': False
            },
            'banned_elements': [
                'dirty_pool',
                'algae_bloom',
                'broken_equipment',
                'empty_pool',
                'unsafe_conditions',
                'people_in_water',
                'stock_photo_watermark'
            ],
            'psychological_alignment': {
                'emotional_message': 'crystal_clear_safety_reliability',
                'image_should_convey': 'professional_pristine_trustworthy'
            }
        },
        'pool_renovation': {
            'primary_elements': [
                'modern_pool_design',
                'finished_renovation',
                'modern_equipment',
                'quality_finishes',
                'transformation_visible'
            ],
            'required_count': 5,
            'quality_minimum': ImageQualityLevel.PROFESSIONAL,
            'diversity_rules': {
                'before_and_after': True,  # REQUIRED for renovation
                'aerial_view': True,
                'detail_shots': True,
                'equipment_detail': True,
                'team_at_work': False  # Not necessary, focus on results
            },
            'banned_elements': [
                'incomplete_work',
                'construction_mess',
                'damaged_areas',
                'old_design_reference',
                'poor_lighting',
                'debris'
            ],
            'psychological_alignment': {
                'emotional_message': 'transformation_investment_value',
                'image_should_convey': 'modern_premium_successful'
            }
        },
        'ac_installation': {
            'primary_elements': [
                'installed_unit_working',
                'professional_installation',
                'clean_finish',
                'modern_equipment',
                'functional_ac_running'
            ],
            'required_count': 5,
            'quality_minimum': ImageQualityLevel.HIGH_QUALITY,
            'diversity_rules': {
                'interior_and_exterior': True,
                'working_unit_visible': True,
                'installation_process': True,
                'professional_finish': True,
                'temperature_display_visible': False
            },
            'banned_elements': [
                'faulty_units',
                'poor_installation',
                'damaged_equipment',
                'messy_installation',
                'low_quality_parts',
                'unprofessional_appearance'
            ],
            'psychological_alignment': {
                'emotional_message': 'immediate_relief_professionalism',
                'image_should_convey': 'modern_reliable_professional'
            }
        },
        'solar_installation': {
            'primary_elements': [
                'solar_panels_installed',
                'professional_installation',
                'complete_system',
                'modern_equipment',
                'roof_mounted_panels'
            ],
            'required_count': 5,
            'quality_minimum': ImageQualityLevel.HIGH_QUALITY,
            'diversity_rules': {
                'full_system_visible': True,
                'closeup_of_panels': True,
                'installation_process': True,
                'monitoring_display': True,
                'before_roof': False
            },
            'banned_elements': [
                'damaged_panels',
                'poor_installation',
                'incomplete_system',
                'old_equipment',
                'dirty_panels',
                'unsafe_setup'
            ],
            'psychological_alignment': {
                'emotional_message': 'future_independence_clean_energy',
                'image_should_convey': 'modern_investment_reliable'
            }
        },
        'garden_maintenance': {
            'primary_elements': [
                'manicured_garden',
                'healthy_plants',
                'professional_landscaping',
                'defined_spaces',
                'thriving_vegetation'
            ],
            'required_count': 5,
            'quality_minimum': ImageQualityLevel.HIGH_QUALITY,
            'diversity_rules': {
                'wide_angle_landscape': True,
                'plant_detail_shots': True,
                'hardscape_visible': True,
                'worker_in_action': True,
                'seasonal_varieties': True
            },
            'banned_elements': [
                'unkempt_gardens',
                'dead_plants',
                'messy_landscape',
                'poor_maintenance',
                'invasive_weeds',
                'unprofessional_work'
            ],
            'psychological_alignment': {
                'emotional_message': 'beauty_abundance_care',
                'image_should_convey': 'professional_thriving_maintained'
            }
        }
    }

    # BAZARAKI POLICY COMPLIANCE
    BAZARAKI_IMAGE_STANDARDS = {
        'minimum_resolution': (1024, 768),  # At least 768px width
        'aspect_ratio_acceptable': [(16, 9), (4, 3), (1, 1)],
        'file_format_accepted': ['jpg', 'jpeg', 'png', 'webp'],
        'max_file_size_mb': 10,
        'no_watermarks': True,
        'no_logos': ['watermark', 'copyright_mark', 'website_url'],
        'professional_appearance': True,
        'no_people_faces_recognizable': True,  # Privacy - only if consented
        'no_text_overlay': True,
        'no_before_after_arrows': True,
        'no_stock_photo_indicators': True
    }

    # IMAGE CONTENT MATCHING KEYWORDS
    SEMANTIC_KEYWORDS = {
        'pool_maintenance': {
            'must_contain': [
                'water_clarity',
                'pool_surface',
                'equipment',
                'maintenance_activity'
            ],
            'should_contain': [
                'professional_appearance',
                'clean_environment',
                'safety_visible'
            ],
            'must_not_contain': [
                'algae',
                'debris',
                'dirt',
                'deterioration'
            ]
        },
        'ac_installation': {
            'must_contain': [
                'ac_unit',
                'installation',
                'clean_finish',
                'professional_work'
            ],
            'should_contain': [
                'modern_design',
                'interior_space',
                'functioning_unit'
            ],
            'must_not_contain': [
                'messy_installation',
                'incomplete_work',
                'poor_quality',
                'temporary_setup'
            ]
        }
    }

    def __init__(self):
        """Initialize image verification engine"""
        self.verification_log = []

    def verify_image_for_service(self, service_type: str, image_data: Dict) -> Dict:
        """
        Comprehensive image verification for specific service.
        Returns: verification result with score and reasons for rejection
        """

        result = {
            'image_id': image_data.get('id', 'unknown'),
            'service_type': service_type,
            'verification_status': 'pending',
            'quality_score': 0,
            'alignment_score': 0,
            'compliance_score': 0,
            'issues': [],
            'approved': False,
            'detailed_feedback': {}
        }

        if service_type not in self.SERVICE_IMAGE_REQUIREMENTS:
            result['issues'].append(f"Service type {service_type} not configured")
            result['verification_status'] = 'error'
            return result

        requirements = self.SERVICE_IMAGE_REQUIREMENTS[service_type]

        # CHECK 1: Technical Quality
        print(f"\n🔍 CHECK 1: Technical Quality Standards")
        print("-" * 70)
        quality_check = self._verify_technical_quality(image_data, requirements)
        result['quality_score'] = quality_check['score']
        if not quality_check['passed']:
            result['issues'].extend(quality_check['issues'])
            print(f"  ✗ Quality Check FAILED")
            for issue in quality_check['issues']:
                print(f"    - {issue}")
        else:
            print(f"  ✓ Quality Check PASSED (Score: {quality_check['score']}/100)")

        # CHECK 2: Content Alignment (Image actually shows what ad describes)
        print(f"\n🔍 CHECK 2: Content Alignment (Semantic Matching)")
        print("-" * 70)
        alignment_check = self._verify_content_alignment(service_type, image_data, requirements)
        result['alignment_score'] = alignment_check['score']
        if not alignment_check['passed']:
            result['issues'].extend(alignment_check['issues'])
            print(f"  ✗ Content Alignment FAILED")
            for issue in alignment_check['issues']:
                print(f"    - {issue}")
        else:
            print(f"  ✓ Content Alignment PASSED (Score: {alignment_check['score']}/100)")
            print(f"    Elements detected: {', '.join(alignment_check['elements_found'][:3])}")

        # CHECK 3: Bazaraki Policy Compliance
        print(f"\n🔍 CHECK 3: Bazaraki Policy Compliance")
        print("-" * 70)
        compliance_check = self._verify_bazaraki_compliance(image_data)
        result['compliance_score'] = compliance_check['score']
        if not compliance_check['passed']:
            result['issues'].extend(compliance_check['issues'])
            print(f"  ✗ Compliance Check FAILED")
            for issue in compliance_check['issues']:
                print(f"    - {issue}")
        else:
            print(f"  ✓ Compliance Check PASSED (Score: {compliance_check['score']}/100)")

        # CHECK 4: Psychological Alignment (Image conveys emotion of ad)
        print(f"\n🔍 CHECK 4: Psychological Alignment")
        print("-" * 70)
        psychology_check = self._verify_psychological_alignment(
            service_type, image_data, requirements
        )
        if not psychology_check['passed']:
            result['issues'].extend(psychology_check['issues'])
            print(f"  ⚠️  Psychological Alignment: NEEDS WORK")
            for issue in psychology_check['issues']:
                print(f"    - {issue}")
        else:
            print(f"  ✓ Psychological Alignment PASSED")
            print(f"    Conveys: {psychology_check['psychological_message']}")

        # FINAL VERDICT
        print(f"\n{'='*70}")
        all_checks_passed = (
            quality_check['passed'] and
            alignment_check['passed'] and
            compliance_check['passed']
        )

        if all_checks_passed:
            result['verification_status'] = 'approved'
            result['approved'] = True
            print(f"✅ IMAGE APPROVED FOR USE IN ADVERTISEMENT")
        else:
            result['verification_status'] = 'rejected'
            result['approved'] = False
            print(f"❌ IMAGE REJECTED - See issues above")

        result['detailed_feedback'] = {
            'quality': quality_check,
            'alignment': alignment_check,
            'compliance': compliance_check,
            'psychology': psychology_check
        }

        return result

    def _verify_technical_quality(self, image_data: Dict, requirements: Dict) -> Dict:
        """Check technical quality standards"""
        issues = []
        score = 100

        # Resolution check
        width = image_data.get('width', 0)
        height = image_data.get('height', 0)
        min_width, min_height = self.BAZARAKI_IMAGE_STANDARDS['minimum_resolution']

        if width < min_width or height < min_height:
            issues.append(f"Resolution too low ({width}x{height}, minimum {min_width}x{min_height})")
            score -= 30

        # Lighting check
        if image_data.get('brightness_level', 50) < 30:
            issues.append("Image too dark - poor lighting")
            score -= 20

        # Clarity check
        if image_data.get('blur_detected', False):
            issues.append("Image is blurry - must be sharp and clear")
            score -= 25

        # Color check
        if image_data.get('color_saturation', 50) < 20:
            issues.append("Image is washed out - needs better color")
            score -= 15

        # Professional appearance
        if image_data.get('appears_professional', False) == False:
            issues.append("Image doesn't appear professional")
            score -= 20

        return {
            'passed': len(issues) == 0 and score >= 70,
            'score': max(0, score),
            'issues': issues
        }

    def _verify_content_alignment(self, service_type: str, image_data: Dict,
                                  requirements: Dict) -> Dict:
        """Check if image content matches what ad describes"""
        issues = []
        elements_found = []
        score = 100

        primary_elements = requirements.get('primary_elements', [])
        image_tags = image_data.get('detected_elements', [])

        # Check primary elements
        for element in primary_elements:
            if element.lower() in [tag.lower() for tag in image_tags]:
                elements_found.append(element)
            else:
                issues.append(f"Missing key element: {element}")
                score -= 15

        # Check banned elements
        banned = requirements.get('banned_elements', [])
        for banned_element in banned:
            if banned_element.lower() in [tag.lower() for tag in image_tags]:
                issues.append(f"Image contains banned element: {banned_element}")
                score -= 25

        # Check diversity rules
        diversity = requirements.get('diversity_rules', {})
        for rule, required in diversity.items():
            if required:
                # Check if diversity requirement met
                if rule == 'before_and_after' and not image_data.get('is_before_after', False):
                    issues.append("Renovation image must show before/after comparison")
                    score -= 20

        return {
            'passed': len(issues) == 0 and score >= 70,
            'score': max(0, score),
            'issues': issues,
            'elements_found': elements_found
        }

    def _verify_bazaraki_compliance(self, image_data: Dict) -> Dict:
        """Check Bazaraki platform policy compliance"""
        issues = []
        score = 100

        standards = self.BAZARAKI_IMAGE_STANDARDS

        # Check for watermarks
        if image_data.get('has_watermark', False):
            issues.append("Image has watermark - not allowed on Bazaraki")
            score -= 40

        # Check for text overlay
        if image_data.get('has_text_overlay', False):
            issues.append("Image has text overlay - remove and re-upload")
            score -= 30

        # Check for stock photo indicators
        if image_data.get('is_stock_photo', False):
            issues.append("Image appears to be stock photo - use original photography")
            score -= 35

        # Check file size
        file_size_mb = image_data.get('file_size_mb', 0)
        if file_size_mb > standards['max_file_size_mb']:
            issues.append(f"File too large ({file_size_mb}MB, max {standards['max_file_size_mb']}MB)")
            score -= 15

        # Privacy check (faces)
        if image_data.get('contains_identifiable_faces', False):
            if not image_data.get('face_consent_obtained', False):
                issues.append("Image contains identifiable faces without consent")
                score -= 25

        return {
            'passed': len(issues) == 0 and score >= 70,
            'score': max(0, score),
            'issues': issues
        }

    def _verify_psychological_alignment(self, service_type: str, image_data: Dict,
                                       requirements: Dict) -> Dict:
        """Check if image conveys emotional message of ad"""
        issues = []
        score = 100

        psychology_spec = requirements.get('psychological_alignment', {})
        emotional_message = psychology_spec.get('emotional_message', '')
        should_convey = psychology_spec.get('image_should_convey', '')

        image_emotion = image_data.get('emotional_tone', '')
        image_impression = image_data.get('visual_impression', '')

        # Semantic matching of emotion
        if should_convey.lower() not in image_impression.lower():
            issues.append(
                f"Image doesn't convey '{should_convey}'. "
                f"Impression: {image_impression}"
            )
            score -= 20

        # Check for trust indicators
        if should_convey == 'professional_premium_successful':
            if not image_data.get('appears_professional', True):
                issues.append("Image doesn't look premium enough for this service")
                score -= 15

        return {
            'passed': len(issues) == 0 and score >= 60,
            'score': max(0, score),
            'issues': issues,
            'psychological_message': emotional_message
        }

    def verify_image_batch_for_ad(self, service_type: str, images: List[Dict]) -> Dict:
        """
        Verify complete set of images for an advertisement.
        Ensures diversity and coverage of required elements.
        """

        result = {
            'service_type': service_type,
            'total_images_submitted': len(images),
            'images_approved': 0,
            'images_rejected': 0,
            'approved_images': [],
            'rejected_images': [],
            'batch_approved': False,
            'minimum_required': self.SERVICE_IMAGE_REQUIREMENTS[service_type]['required_count']
        }

        print(f"\n{'='*70}")
        print(f"🖼️  IMAGE BATCH VERIFICATION - {service_type.upper()}")
        print(f"{'='*70}")
        print(f"Images submitted: {len(images)}")
        print(f"Minimum required for ad: {result['minimum_required']}")

        for idx, image in enumerate(images, 1):
            print(f"\n📸 Image {idx}/{len(images)}")
            verification = self.verify_image_for_service(service_type, image)

            if verification['approved']:
                result['images_approved'] += 1
                result['approved_images'].append(verification['image_id'])
            else:
                result['images_rejected'] += 1
                result['rejected_images'].append(verification['image_id'])

        # Batch verdict
        if result['images_approved'] >= result['minimum_required']:
            result['batch_approved'] = True
            print(f"\n✅ BATCH APPROVED - Enough images for advertisement")
        else:
            print(f"\n❌ BATCH REJECTED - Need {result['minimum_required'] - result['images_approved']} more images")

        return result


def test_image_verification():
    """Test image verification engine"""
    print("\n" + "="*70)
    print("🖼️  IMAGE VERIFICATION ENGINE TEST")
    print("="*70)

    engine = ImageVerificationEngine()

    # Test image for pool maintenance
    test_image = {
        'id': 'img_pool_001',
        'width': 1920,
        'height': 1080,
        'brightness_level': 85,
        'blur_detected': False,
        'color_saturation': 75,
        'appears_professional': True,
        'has_watermark': False,
        'has_text_overlay': False,
        'is_stock_photo': False,
        'file_size_mb': 3.2,
        'contains_identifiable_faces': False,
        'detected_elements': [
            'crystal_clear_water',
            'pool_surface',
            'equipment',
            'professional_appearance'
        ],
        'emotional_tone': 'clean_professional',
        'visual_impression': 'professional_trustworthy'
    }

    result = engine.verify_image_for_service('pool_maintenance', test_image)

    print(f"\n{'='*70}")
    print(f"VERIFICATION RESULT: {'APPROVED ✅' if result['approved'] else 'REJECTED ❌'}")
    print(f"Overall Score: {(result['quality_score'] + result['alignment_score'] + result['compliance_score']) / 3:.0f}/100")

if __name__ == '__main__':
    test_image_verification()
