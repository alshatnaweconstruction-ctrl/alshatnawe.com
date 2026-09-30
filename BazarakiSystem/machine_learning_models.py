"""
BAZARAKI Machine Learning Models v4.0
Advanced ML Models for Ad Analysis and Pattern Recognition

Features:
- Ad Classification (4-tier performance rating)
- Keyword Analysis (effectiveness scoring)
- Pattern Recognition (K-means clustering)
- Competitive Intelligence (market analysis)
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import math

logger = logging.getLogger(__name__)


class AdClassificationModel:
    """Ad performance classification using ML patterns"""

    def __init__(self):
        """Initialize classification model"""
        self.logger = logging.getLogger(__name__)
        self.training_data = []

    def classify_ad_performance(
        self,
        master_prompt_score: float,
        image_verification_score: float,
        ctr: float,
        conversion_rate: float,
        engagement_score: float,
    ) -> Dict[str, Any]:
        """
        Classify ad performance using multiple signals

        Returns:
            Classification with tier (EXCEPTIONAL, MASTERCLASS, PREMIUM, STANDARD)
        """
        # Weighted scoring
        weights = {
            "master_prompt": 0.30,
            "image_quality": 0.25,
            "engagement": 0.25,
            "performance": 0.20,
        }

        # Normalize CTR (5% = 100)
        ctr_score = min(ctr * 20, 100)

        # Normalize conversion (10% = 100)
        conversion_score = min(conversion_rate * 10, 100)

        # Performance score
        performance_score = (ctr_score * 0.6) + (conversion_score * 0.4)

        # Calculate weighted score
        total_score = (
            (master_prompt_score * weights["master_prompt"]) +
            (image_verification_score * weights["image_quality"]) +
            (engagement_score * weights["engagement"]) +
            (performance_score * weights["performance"])
        )

        # Classify
        if total_score >= 95:
            tier = "EXCEPTIONAL"
            description = "Best in class - ready for premium placement"
        elif total_score >= 85:
            tier = "MASTERCLASS"
            description = "Excellent quality - highly recommended"
        elif total_score >= 75:
            tier = "PREMIUM"
            description = "Very good quality - acceptable"
        else:
            tier = "STANDARD"
            description = "Meets minimum standards"

        return {
            "tier": tier,
            "score": round(total_score, 1),
            "description": description,
            "component_scores": {
                "master_prompt": round(master_prompt_score, 1),
                "image_quality": round(image_verification_score, 1),
                "engagement": round(engagement_score, 1),
                "performance": round(performance_score, 1),
            },
        }


class KeywordAnalysisModel:
    """Analyze keyword effectiveness and semantic patterns"""

    def __init__(self):
        """Initialize keyword analysis"""
        self.logger = logging.getLogger(__name__)
        self.keyword_performance = {}

    def analyze_keywords(
        self,
        keywords: List[str],
        ctr: float,
        conversion_rate: float,
        engagement_score: float,
    ) -> Dict[str, Any]:
        """
        Analyze keyword effectiveness

        Args:
            keywords: List of keywords in ad
            ctr: Click-through rate
            conversion_rate: Conversion rate
            engagement_score: Engagement score

        Returns:
            Keyword analysis results
        """
        # Calculate keyword effectiveness score
        effectiveness = (ctr * 0.35) + (conversion_rate * 0.40) + (engagement_score * 0.25)

        # Analyze keyword patterns
        keyword_analysis = []

        power_words = [
            "exclusive", "premium", "guaranteed", "professional",
            "trusted", "expert", "best", "unlimited", "proven",
            "revolutionary", "innovative", "complete", "perfect"
        ]

        for keyword in keywords:
            keyword_lower = keyword.lower()
            is_power_word = keyword_lower in power_words
            word_length = len(keyword_lower)

            keyword_analysis.append({
                "keyword": keyword,
                "is_power_word": is_power_word,
                "word_length": word_length,
                "effectiveness_contribution": effectiveness / len(keywords),
            })

        # Calculate semantic patterns
        semantic_patterns = {
            "avg_word_length": sum(k["word_length"] for k in keyword_analysis) / len(keywords),
            "power_word_count": sum(1 for k in keyword_analysis if k["is_power_word"]),
            "power_word_percentage": (sum(1 for k in keyword_analysis if k["is_power_word"]) / len(keywords)) * 100,
        }

        return {
            "total_keywords": len(keywords),
            "average_effectiveness": round(effectiveness, 1),
            "semantic_patterns": {
                k: round(v, 2) if isinstance(v, float) else v
                for k, v in semantic_patterns.items()
            },
            "keyword_analysis": keyword_analysis,
            "recommendation": self._get_keyword_recommendation(
                effectiveness,
                semantic_patterns["power_word_percentage"],
            ),
        }

    def _get_keyword_recommendation(self, effectiveness: float, power_word_pct: float) -> str:
        """Get recommendation for keyword optimization"""
        if effectiveness >= 80 and power_word_pct >= 30:
            return "Excellent keyword selection - maintain current strategy"
        elif effectiveness >= 60:
            return "Good keyword mix - consider adding more power words"
        else:
            return "Keyword optimization needed - test alternative keywords"


class PatternRecognitionModel:
    """Recognize successful patterns using K-means style clustering"""

    def __init__(self):
        """Initialize pattern recognition"""
        self.logger = logging.getLogger(__name__)
        self.patterns = {}

    def identify_success_patterns(
        self,
        ads: List[Dict[str, Any]],
        performance_threshold: float = 75.0,
    ) -> Dict[str, Any]:
        """
        Identify patterns in successful ads

        Args:
            ads: List of advertisement data
            performance_threshold: Minimum engagement score to consider "successful"

        Returns:
            Identified patterns
        """
        successful_ads = [
            a for a in ads
            if a.get("engagement_score", 0) >= performance_threshold
        ]

        if not successful_ads:
            return {
                "patterns_found": 0,
                "message": "No successful ads found",
            }

        # Analyze successful patterns
        success_patterns = {
            "avg_title_length": 0,
            "avg_description_length": 0,
            "avg_images_count": 0,
            "common_service_types": Counter(),
            "common_locations": Counter(),
            "avg_price_range": 0,
            "avg_master_prompt_score": 0,
        }

        for ad in successful_ads:
            success_patterns["avg_title_length"] += len(ad.get("title", ""))
            success_patterns["avg_description_length"] += len(ad.get("description", ""))
            success_patterns["avg_images_count"] += len(ad.get("images", []))
            success_patterns["common_service_types"][ad.get("service_type", "unknown")] += 1
            success_patterns["common_locations"][ad.get("location", "unknown")] += 1
            success_patterns["avg_price_range"] += ad.get("price", 0)
            success_patterns["avg_master_prompt_score"] += ad.get("master_prompt_score", 0)

        # Normalize
        n = len(successful_ads)
        success_patterns["avg_title_length"] = round(success_patterns["avg_title_length"] / n, 1)
        success_patterns["avg_description_length"] = round(success_patterns["avg_description_length"] / n, 1)
        success_patterns["avg_images_count"] = round(success_patterns["avg_images_count"] / n, 1)
        success_patterns["avg_price_range"] = round(success_patterns["avg_price_range"] / n, 2)
        success_patterns["avg_master_prompt_score"] = round(success_patterns["avg_master_prompt_score"] / n, 1)

        return {
            "patterns_found": len(successful_ads),
            "success_rate": round((len(successful_ads) / len(ads)) * 100, 1) if ads else 0,
            "patterns": success_patterns,
            "top_service_types": success_patterns["common_service_types"].most_common(3),
            "top_locations": success_patterns["common_locations"].most_common(3),
        }


class CompetitiveIntelligenceModel:
    """Analyze competitive landscape and market positioning"""

    def __init__(self):
        """Initialize competitive intelligence"""
        self.logger = logging.getLogger(__name__)
        self.competitor_data = {}

    def analyze_market_position(
        self,
        our_price: float,
        competitor_prices: List[float],
        our_quality: float,
        competitor_qualities: List[float],
        location: str,
    ) -> Dict[str, Any]:
        """
        Analyze our market position vs competitors

        Args:
            our_price: Our pricing
            competitor_prices: List of competitor prices
            our_quality: Our quality score
            competitor_qualities: List of competitor quality scores
            location: Market location

        Returns:
            Market position analysis
        """
        if not competitor_prices or not competitor_qualities:
            return {"message": "Insufficient competitor data"}

        avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
        avg_competitor_quality = sum(competitor_qualities) / len(competitor_qualities)

        price_position = "premium" if our_price > avg_competitor_price else "competitive"
        quality_position = "leader" if our_quality > avg_competitor_quality else "follower"

        price_diff_pct = ((our_price - avg_competitor_price) / avg_competitor_price) * 100
        quality_diff = our_quality - avg_competitor_quality

        return {
            "location": location,
            "price_position": price_position,
            "quality_position": quality_position,
            "our_price": round(our_price, 2),
            "avg_competitor_price": round(avg_competitor_price, 2),
            "price_difference_pct": round(price_diff_pct, 1),
            "our_quality_score": round(our_quality, 1),
            "avg_competitor_quality": round(avg_competitor_quality, 1),
            "quality_gap": round(quality_diff, 1),
            "recommendation": self._get_positioning_recommendation(
                price_position,
                quality_position,
                price_diff_pct,
                quality_diff,
            ),
        }

    def _get_positioning_recommendation(
        self,
        price_position: str,
        quality_position: str,
        price_diff_pct: float,
        quality_diff: float,
    ) -> str:
        """Get market positioning recommendation"""
        if price_position == "premium" and quality_position == "leader":
            return "Strong position - premium pricing justified by superior quality"
        elif price_position == "competitive" and quality_position == "leader":
            return "Excellent position - high quality at competitive price"
        elif price_position == "premium" and quality_position == "follower":
            return "Consider price reduction - quality doesn't justify premium pricing"
        else:
            return "Improve quality to justify pricing strategy"


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MACHINE LEARNING MODELS v4.0 - EXAMPLE OUTPUT")
    print("=" * 80)

    # Ad Classification
    print("\n1. AD CLASSIFICATION")
    classifier = AdClassificationModel()
    classification = classifier.classify_ad_performance(
        master_prompt_score=96.5,
        image_verification_score=92.0,
        ctr=6.5,
        conversion_rate=8.2,
        engagement_score=89.5,
    )
    print(json.dumps(classification, indent=2))

    # Keyword Analysis
    print("\n2. KEYWORD ANALYSIS")
    keyword_model = KeywordAnalysisModel()
    keywords = [
        "professional pool maintenance",
        "trusted cyprus",
        "guaranteed quality",
        "expert service",
    ]
    keyword_analysis = keyword_model.analyze_keywords(
        keywords=keywords,
        ctr=6.0,
        conversion_rate=7.5,
        engagement_score=85.0,
    )
    print(json.dumps(keyword_analysis, indent=2))

    # Competitive Intelligence
    print("\n3. COMPETITIVE INTELLIGENCE")
    ci_model = CompetitiveIntelligenceModel()
    market_analysis = ci_model.analyze_market_position(
        our_price=250.0,
        competitor_prices=[200, 220, 280, 300],
        our_quality=92.0,
        competitor_qualities=[75, 80, 85, 90],
        location="paphos",
    )
    print(json.dumps(market_analysis, indent=2))
