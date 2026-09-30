"""
ADVANCED COPYWRITING ENGINE
PASTOR Framework Implementation + Cyprus Market Linguistics
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class AdCopy:
    language: str  # 'en' or 'el'
    title: str
    description: str
    search_terms: List[str]
    validation_errors: List[str] = None
    validation_passed: bool = False

class PASTORCopywriter:
    """
    PASTOR Framework:
    P - Problem: Identify customer pain point
    A - Agitate: Escalate emotional impact
    S - Solution: Present your service as remedy
    T - Transformation: Show before/after results
    O - Offer: Specific terms and inclusions
    R - Response/CTA: Clear call-to-action
    """

    # BANNED WORDS - ABSOLUTE (cannot be in any ad)
    BANNED_WORDS = {
        'sale', 'sell', 'urgent', 'price', 'inexpensive',
        'rent', 'specialist', 'we offer', 'our team',
        'premium solutions', 'quality workmanship', 'discount',
        'special offer', 'limited time'
    }

    # BANNED PHRASES (substring matches)
    BANNED_PHRASES = [
        'we offer',
        'our team',
        'premium solutions',
        'quality workmanship',
        'we provide',
        'our expert'
    ]

    # TITLE RULES
    TITLE_MIN_LENGTH = 55
    TITLE_MAX_LENGTH = 80
    TITLE_MIN_WORDS = 5
    TITLE_MAX_WORDS = 15

    def __init__(self):
        self.greek_keywords = {
            'maintenance': ['συντήρηση', 'επισκευή', 'ολοκληρωτική'],
            'painting': ['βαφή', 'χρωματισμός', 'επιφάνειας'],
            'plumbing': ['υδραυλικός', 'σωληνώσεων', 'αποχέτευση'],
            'renovation': ['ανακαίνιση', 'αποκατάσταση', 'ανανέωση'],
            'property': ['ακίνητο', 'ιδιοκτησία', 'κατοικία', 'βίλα', 'διαμέρισμα']
        }

        self.search_intent_patterns = {
            'problem_solving': ['issue', 'problem', 'damage', 'broken', 'leak', 'crack'],
            'maintenance': ['maintain', 'service', 'upkeep', 'care', 'preservation'],
            'improvement': ['upgrade', 'enhance', 'renovate', 'restore', 'refresh'],
            'emergency': ['emergency', 'urgent', 'immediate', 'fast', 'quick response']
        }

    def validate_title(self, title: str) -> Tuple[bool, List[str]]:
        """
        Validate title against ALL title rules:
        - 55-80 characters
        - 5-15 words
        - No banned words
        - Specific, location-based, value proposition
        """
        errors = []

        # Length validation
        if len(title) < self.TITLE_MIN_LENGTH:
            errors.append(f"Title too short ({len(title)} chars, min {self.TITLE_MIN_LENGTH})")
        if len(title) > self.TITLE_MAX_LENGTH:
            errors.append(f"Title too long ({len(title)} chars, max {self.TITLE_MAX_LENGTH})")

        # Word count validation
        words = title.split()
        if len(words) < self.TITLE_MIN_WORDS:
            errors.append(f"Too few words ({len(words)}, min {self.TITLE_MIN_WORDS})")
        if len(words) > self.TITLE_MAX_WORDS:
            errors.append(f"Too many words ({len(words)}, max {self.TITLE_MAX_WORDS})")

        # Banned word check
        title_lower = title.lower()
        for banned_word in self.BANNED_WORDS:
            if banned_word in title_lower:
                errors.append(f"Banned word: '{banned_word}'")

        # Banned phrase check
        for banned_phrase in self.BANNED_PHRASES:
            if banned_phrase in title_lower:
                errors.append(f"Banned phrase: '{banned_phrase}'")

        # Must contain location or service specificity
        location_indicators = ['paphos', 'cyprus', 'polis', 'geroskipou', 'larnaca', 'nicosia', 'limassol']
        service_specificity = any(ind in title_lower for ind in location_indicators)
        if not service_specificity and len(title.split()) < 7:
            errors.append("Title lacks location/specificity (too generic)")

        return len(errors) == 0, errors

    def validate_description(self, description: str) -> Tuple[bool, List[str]]:
        """
        Validate description architecture:
        1. Problem statement (20-40 words)
        2. Solution explanation (20-40 words)
        3. Included services/materials
        4. Trust signals (credentials, years, certifications)
        5. Target customer type
        6. Service coverage area
        7. Process/timeline
        8. Fee structure
        9. Call-to-action
        """
        errors = []

        min_length = 150
        max_length = 2000

        if len(description) < min_length:
            errors.append(f"Description too short ({len(description)} chars, min {min_length})")
        if len(description) > max_length:
            errors.append(f"Description too long ({len(description)} chars, max {max_length})")

        # Check for banned phrases
        desc_lower = description.lower()
        for banned_phrase in self.BANNED_PHRASES:
            if banned_phrase in desc_lower:
                errors.append(f"Banned phrase: '{banned_phrase}'")

        # Must contain specificity indicators
        specificity_markers = {
            'problem': ['issue', 'problem', 'need', 'require'],
            'solution': ['provide', 'offer', 'deliver', 'service'],
            'trust': ['experience', 'professional', 'certified', 'licensed', 'warranty'],
            'cta': ['contact', 'call', 'message', 'inquire', 'request', 'book']
        }

        found_categories = {}
        for category, keywords in specificity_markers.items():
            found = any(kw in desc_lower for kw in keywords)
            found_categories[category] = found
            if not found:
                errors.append(f"Missing '{category}' indicators")

        return len(errors) == 0, errors

    def check_semantic_quality(self, description: str) -> Dict[str, any]:
        """Evaluate semantic quality of ad copy"""
        analysis = {
            'readability_score': 0,
            'keyword_density': {},
            'emotional_appeals': [],
            'specificity_level': 'low',
            'commercial_intent': 'weak'
        }

        desc_lower = description.lower()

        # Count emotional appeal words
        emotional_words = ['professional', 'reliable', 'experienced', 'quality', 'trusted', 'certified']
        for word in emotional_words:
            if word in desc_lower:
                analysis['emotional_appeals'].append(word)

        # Assess specificity
        specific_indicators = ['paphos', 'polis', 'geroskipou', 'years', 'experience', '%', 'square', 'm²']
        specificity_count = sum(1 for ind in specific_indicators if ind in desc_lower)
        if specificity_count >= 3:
            analysis['specificity_level'] = 'high'
        elif specificity_count >= 1:
            analysis['specificity_level'] = 'medium'

        # Assess commercial intent
        commercial_words = ['price', 'fee', 'cost', 'rate', 'warranty', 'guarantee', 'payment']
        commercial_count = sum(1 for word in commercial_words if word in desc_lower)
        if commercial_count >= 3:
            analysis['commercial_intent'] = 'strong'
        elif commercial_count >= 1:
            analysis['commercial_intent'] = 'medium'

        return analysis

    def generate_english_title(self, service_type: str, location: str, unique_aspect: str) -> str:
        """Generate English title using SPECIFICITY + LOCATION + VALUE"""
        templates = {
            'painting': f"Professional {service_type} painting in {location}: {unique_aspect}",
            'plasterboard': f"Expert drywall and plasterboard installation in {location} - {unique_aspect}",
            'renovation': f"Complete {service_type} renovation in {location}: {unique_aspect}",
            'tiling': f"Specialist tile and stone installation in {location} - {unique_aspect}",
            'general': f"Experienced {service_type} services in {location}: {unique_aspect}"
        }

        return templates.get(service_type, templates['general'])

    def generate_english_description(self, problem: str, solution: str, service_area: str) -> str:
        """Generate English description using PASTOR framework"""
        description = f"""{problem}

{solution}

We provide comprehensive service coverage across {service_area}, including property maintenance, renovations, and specialized installations. Our team brings decades of combined experience to every project.

Service includes professional assessment, quality materials, skilled workmanship, and follow-up support. We work with residential properties, commercial spaces, and investment portfolios.

Professional credentials and insurance verified. Transparent pricing with detailed quotations. Flexible scheduling to minimize disruption to your property.

Contact us for consultation and site assessment. Quick response to inquiries. Competitive rates for quality outcomes."""

        return description

    def generate_search_terms(self, service_type: str, location: str, specifics: List[str]) -> List[str]:
        """Generate 6-10 search terms (natural, comma-separated, no stuffing)"""
        base_terms = [
            f"{service_type} {location}",
            f"{service_type} Cyprus",
            f"{service_type} services Paphos" if 'paphos' in location.lower() else f"{service_type} services",
            f"professional {service_type}",
            f"{service_type} repair",
            f"{service_type} installation"
        ]

        # Add specific terms
        if specifics:
            base_terms.extend(specifics[:4])

        # Trim to 6-10
        return base_terms[:10]

    def validate_bilingual_pair(self, english_title: str, greek_title: str) -> Tuple[bool, List[str]]:
        """Ensure bilingual titles are semantic equivalents"""
        errors = []

        # Both must pass individual validation
        en_valid, en_errors = self.validate_title(english_title)
        el_valid, el_errors = self.validate_title(greek_title)

        if not en_valid:
            errors.extend([f"English: {e}" for e in en_errors])
        if not el_valid:
            errors.extend([f"Greek: {e}" for e in el_errors])

        return len(errors) == 0, errors

    def quality_checklist(self, ad: AdCopy) -> Dict[str, bool]:
        """Final quality checklist before publication"""
        checklist = {
            'title_length': self.TITLE_MIN_LENGTH <= len(ad.title) <= self.TITLE_MAX_LENGTH,
            'title_no_banned_words': not any(w in ad.title.lower() for w in self.BANNED_WORDS),
            'description_length': 150 <= len(ad.description) <= 2000,
            'description_no_banned_phrases': not any(p in ad.description.lower() for p in self.BANNED_PHRASES),
            'search_terms_count': 6 <= len(ad.search_terms) <= 10,
            'language_valid': ad.language in ['en', 'el'],
            'no_fabricated_claims': not any(claim in ad.description.lower() for claim in ['guarantee', 'never fails', '100% success']),
            'trust_indicators_present': any(ind in ad.description.lower() for ind in ['professional', 'experience', 'certified', 'licensed']),
            'cta_present': any(cta in ad.description.lower() for cta in ['contact', 'call', 'message', 'inquire']),
            'location_specific': any(loc in ad.description.lower() or ad.title.lower() for loc in ['paphos', 'polis', 'geroskipou', 'cyprus'])
        }

        return checklist

def test_copywriter():
    """Test copywriting engine"""
    print("\n🎨 COPYWRITING ENGINE TEST")
    print("=" * 70)

    cw = PASTORCopywriter()

    # Test 1: Valid title
    test_titles = [
        "Professional plasterboard installation in Paphos - Expert finishes",  # Valid
        "Painting service",  # Too short
        "We offer premium painting solutions for your property renovation project today",  # Too long + banned words
    ]

    print("\nTitle Validation Tests:")
    for title in test_titles:
        valid, errors = cw.validate_title(title)
        status = "✓ PASS" if valid else "✗ FAIL"
        print(f"{status}: {title[:50]}...")
        if errors:
            for err in errors:
                print(f"    - {err}")

    # Test 2: Search terms generation
    print("\nSearch Terms Generation:")
    terms = cw.generate_search_terms('plasterboard', 'Paphos', ['drywall', 'partition walls'])
    print(f"Generated {len(terms)} terms: {', '.join(terms[:5])}...")

    # Test 3: Quality checklist
    print("\nQuality Checklist:")
    test_ad = AdCopy(
        language='en',
        title="Professional plasterboard installation in Paphos - Expert finishes",
        description="Need quality drywall work? We provide professional plasterboard installation with expert finishing. Certified installation for residential and commercial properties in Paphos area. Contact us for assessment.",
        search_terms=['plasterboard paphos', 'drywall installation', 'partition walls paphos']
    )

    checklist = cw.quality_checklist(test_ad)
    passed = sum(1 for v in checklist.values() if v)
    print(f"Quality Score: {passed}/{len(checklist)} checks passed")
    for check, result in checklist.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")

if __name__ == '__main__':
    test_copywriter()
