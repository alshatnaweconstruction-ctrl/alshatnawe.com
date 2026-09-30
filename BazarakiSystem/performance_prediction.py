"""
BAZARAKI Performance Prediction Engine v4.0
ML-Based Forecasting of Advertisement Success Metrics

Features:
- Regression Model (30+ day CTR, conversion, ROI forecasting)
- Success Probability Model (logistic regression)
- Ad Optimization Advisor (parameter-specific recommendations)
"""

import logging
import json
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)


class RegressionPredictor:
    """Linear regression model for CTR, conversion, and ROI prediction"""

    def __init__(self):
        """Initialize regression predictor"""
        self.logger = logging.getLogger(__name__)
        self.model_data = {}

    def predict_ctr_30days(
        self,
        current_ctr: float,
        historical_data: Optional[List[float]] = None,
        trend: str = "stable",
    ) -> Dict[str, Any]:
        """
        Predict CTR for next 30 days

        Args:
            current_ctr: Current CTR %
            historical_data: Historical CTR values
            trend: "improving", "declining", or "stable"

        Returns:
            CTR prediction for 30 days
        """
        if historical_data and len(historical_data) >= 7:
            # Calculate trend from historical data
            recent_avg = sum(historical_data[-7:]) / 7
            older_avg = sum(historical_data[:7]) / min(7, len(historical_data))
            trend_direction = recent_avg - older_avg
        else:
            # Use provided trend
            trend_direction = {
                "improving": 0.1,
                "declining": -0.1,
                "stable": 0.0,
            }.get(trend, 0.0)

        # Regression model: predict 30-day trend
        base_growth_rate = 0.02 if trend_direction > 0 else (-0.01 if trend_direction < 0 else 0)
        predicted_ctr_30d = current_ctr * (1 + (base_growth_rate * 30))

        # Industry benchmark: 5-8% for quality ads, 2-3% average
        if current_ctr > 5:
            # Already performing well, slight growth expected
            confidence = 0.85
        elif current_ctr > 3:
            # Above average, moderate growth potential
            confidence = 0.80
        else:
            # Below average, high variability
            confidence = 0.70

        return {
            "current_ctr": round(current_ctr, 2),
            "predicted_ctr_30days": round(predicted_ctr_30d, 2),
            "daily_growth_rate": round((predicted_ctr_30d - current_ctr) / 30, 4),
            "confidence": round(confidence, 2),
            "vs_industry_benchmark": (
                "above average" if current_ctr > 3 else "below average"
            ),
        }

    def predict_conversion_30days(
        self,
        current_conversion: float,
        ctr: float,
        historical_data: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Predict conversion rate for next 30 days"""
        if historical_data and len(historical_data) >= 7:
            recent_avg = sum(historical_data[-7:]) / 7
            older_avg = sum(historical_data[:7]) / min(7, len(historical_data))
            trend_direction = recent_avg - older_avg
        else:
            trend_direction = 0

        # Regression: conversion depends on CTR quality and message
        base_growth = 0.03 if trend_direction > 0 else (-0.02 if trend_direction < 0 else 0)
        predicted_conversion_30d = current_conversion * (1 + (base_growth * 30))

        # Conversion depends on quality of traffic (CTR)
        quality_multiplier = min(ctr / 3, 1.5)  # Higher CTR = better quality
        predicted_conversion_30d *= quality_multiplier

        # Industry benchmark: 2-3% average, 6-10% for quality ads
        if current_conversion > 6:
            confidence = 0.85
        elif current_conversion > 2:
            confidence = 0.80
        else:
            confidence = 0.70

        return {
            "current_conversion": round(current_conversion, 2),
            "predicted_conversion_30days": round(predicted_conversion_30d, 2),
            "daily_growth_rate": round((predicted_conversion_30d - current_conversion) / 30, 4),
            "confidence": round(confidence, 2),
            "vs_industry_benchmark": (
                "above average" if current_conversion > 2 else "below average"
            ),
        }

    def predict_roi_30days(
        self,
        current_roi: float,
        ctr: float,
        conversion: float,
        avg_customer_value: float,
        current_ad_spend: float,
    ) -> Dict[str, Any]:
        """Predict ROI for next 30 days"""
        # ROI depends on CTR, conversion, and customer value
        # Formula: ROI = (Revenue - Spend) / Spend

        # Project 30-day revenue
        projected_visits = 1000 * (ctr / 3)  # Normalize to 1000 base impressions
        projected_conversions = projected_visits * (conversion / 100)
        projected_revenue = projected_conversions * avg_customer_value

        # 30-day spend
        spend_30d = current_ad_spend * 30

        # Calculate projected ROI
        projected_roi = ((projected_revenue - spend_30d) / spend_30d) * 100 if spend_30d > 0 else 0

        # Confidence based on metrics quality
        if ctr > 5 and conversion > 6:
            confidence = 0.90
        elif ctr > 3 and conversion > 2:
            confidence = 0.80
        else:
            confidence = 0.65

        return {
            "current_roi": round(current_roi, 2),
            "predicted_roi_30days": round(projected_roi, 2),
            "projected_revenue_30d": round(projected_revenue, 2),
            "projected_spend_30d": round(spend_30d, 2),
            "projected_profit_30d": round(projected_revenue - spend_30d, 2),
            "confidence": round(confidence, 2),
            "break_even_rate": round((spend_30d / avg_customer_value) if avg_customer_value > 0 else 0, 0),
        }


class SuccessProbabilityModel:
    """Predict success probability using logistic regression"""

    def __init__(self):
        """Initialize success probability model"""
        self.logger = logging.getLogger(__name__)

    def predict_success_probability(
        self,
        master_prompt_score: float,
        image_verification_score: float,
        quality_gates_passed: int,
        ctr: float,
        conversion: float,
        engagement_score: float,
    ) -> Dict[str, Any]:
        """
        Predict success probability using logistic regression

        Args:
            master_prompt_score: Quality of description (0-100)
            image_verification_score: Quality of images (0-100)
            quality_gates_passed: Gates passed (0-10)
            ctr: Current CTR %
            conversion: Current conversion %
            engagement_score: Engagement score (0-100)

        Returns:
            Success probability (0-100%)
        """
        # Normalize inputs
        prompt_norm = master_prompt_score / 100
        image_norm = image_verification_score / 100
        gates_norm = quality_gates_passed / 10
        ctr_norm = min(ctr / 5, 1.0)  # 5% = 100%
        conversion_norm = min(conversion / 10, 1.0)  # 10% = 100%
        engagement_norm = engagement_score / 100

        # Weights for success factors
        weights = {
            "prompt": 0.25,
            "images": 0.20,
            "gates": 0.15,
            "ctr": 0.15,
            "conversion": 0.15,
            "engagement": 0.10,
        }

        # Calculate weighted score
        score = (
            (prompt_norm * weights["prompt"]) +
            (image_norm * weights["images"]) +
            (gates_norm * weights["gates"]) +
            (ctr_norm * weights["ctr"]) +
            (conversion_norm * weights["conversion"]) +
            (engagement_norm * weights["engagement"])
        )

        # Apply logistic function for probability (S-curve)
        # Logistic: 1 / (1 + e^(-k*(x-0.5)))
        k = 6  # Steepness of curve
        probability = 100 / (1 + math.exp(-k * (score - 0.5)))

        # Determine success level
        if probability >= 90:
            level = "VERY HIGH"
            recommendation = "Ready for scaling - high confidence of success"
        elif probability >= 75:
            level = "HIGH"
            recommendation = "Good prospects - recommended for deployment"
        elif probability >= 60:
            level = "MODERATE"
            recommendation = "Fair prospects - A/B test recommended"
        elif probability >= 40:
            level = "LOW"
            recommendation = "Revise before deployment - significant risks"
        else:
            level = "VERY LOW"
            recommendation = "Not recommended - major revisions needed"

        return {
            "success_probability": round(probability, 1),
            "probability_level": level,
            "recommendation": recommendation,
            "confidence_factors": {
                "master_prompt": round(prompt_norm * 100, 1),
                "image_quality": round(image_norm * 100, 1),
                "quality_gates": round(gates_norm * 100, 1),
                "current_ctr": round(ctr_norm * 100, 1),
                "current_conversion": round(conversion_norm * 100, 1),
                "engagement_score": round(engagement_norm * 100, 1),
            },
            "risk_assessment": self._assess_risks(
                prompt_norm,
                image_norm,
                gates_norm,
            ),
        }

    def _assess_risks(
        self,
        prompt_norm: float,
        image_norm: float,
        gates_norm: float,
    ) -> List[str]:
        """Assess potential risks"""
        risks = []

        if prompt_norm < 0.75:
            risks.append("Description quality below target (>75%)")
        if image_norm < 0.75:
            risks.append("Image quality below target (>75%)")
        if gates_norm < 0.80:
            risks.append("Quality gates not fully passed")

        if not risks:
            risks = ["None identified"]

        return risks


class AdOptimizationAdvisor:
    """Provide parameter-specific optimization recommendations"""

    def __init__(self):
        """Initialize optimization advisor"""
        self.logger = logging.getLogger(__name__)

    def get_optimization_recommendations(
        self,
        ctr: float,
        conversion: float,
        engagement: float,
        master_prompt_score: float,
        image_quality: float,
    ) -> Dict[str, Any]:
        """
        Get specific recommendations for optimization

        Args:
            ctr: Current CTR %
            conversion: Current conversion %
            engagement: Engagement score (0-100)
            master_prompt_score: Description quality (0-100)
            image_quality: Image quality score (0-100)

        Returns:
            Specific optimization recommendations
        """
        recommendations = {
            "ctr_recommendations": [],
            "conversion_recommendations": [],
            "engagement_recommendations": [],
            "overall_priority": [],
        }

        # CTR Analysis
        if ctr < 3:
            recommendations["ctr_recommendations"].append(
                "Increase visibility: Expand audience, improve targeting"
            )
            recommendations["ctr_recommendations"].append(
                "Test alternative headlines (shorter, benefit-focused)"
            )
        elif ctr < 5:
            recommendations["ctr_recommendations"].append(
                "A/B test different images for higher appeal"
            )
        else:
            recommendations["ctr_recommendations"].append(
                "CTR is excellent - maintain current strategy"
            )

        # Conversion Analysis
        if conversion < 2:
            recommendations["conversion_recommendations"].append(
                "CRITICAL: Improve landing page and call-to-action"
            )
            recommendations["conversion_recommendations"].append(
                "Test different price points or offers"
            )
            recommendations["overall_priority"].append("Conversion Rate")
        elif conversion < 6:
            recommendations["conversion_recommendations"].append(
                "Test different value propositions in copy"
            )
            recommendations["conversion_recommendations"].append(
                "Add social proof and testimonials"
            )
        else:
            recommendations["conversion_recommendations"].append(
                "Conversion rate is strong - maintain current approach"
            )

        # Engagement Analysis
        if engagement < 50:
            recommendations["engagement_recommendations"].append(
                "Content engagement low - revise message entirely"
            )
            recommendations["overall_priority"].append("Message Quality")
        elif engagement < 75:
            recommendations["engagement_recommendations"].append(
                "Improve emotional connection in description"
            )
            recommendations["engagement_recommendations"].append(
                "Add more specific benefits and outcomes"
            )
        else:
            recommendations["engagement_recommendations"].append(
                "Engagement excellent - continue current messaging"
            )

        # Master Prompt Analysis
        if master_prompt_score < 80:
            recommendations["overall_priority"].append("Description Quality")

        # Image Quality Analysis
        if image_quality < 80:
            recommendations["overall_priority"].append("Image Quality")

        return {
            "recommendations": recommendations,
            "estimated_improvement": self._estimate_improvement(
                ctr, conversion, engagement
            ),
        }

    def _estimate_improvement(self, ctr: float, conversion: float, engagement: float) -> Dict[str, str]:
        """Estimate potential improvements"""
        return {
            "if_optimize_ctr": f"+{min(3, 8-ctr):.1f}% to {ctr + min(3, 8-ctr):.1f}%",
            "if_optimize_conversion": f"+{min(4, 10-conversion):.1f}% to {conversion + min(4, 10-conversion):.1f}%",
            "if_optimize_engagement": f"+{min(20, 100-engagement):.1f} to {engagement + min(20, 100-engagement):.1f}",
        }


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PERFORMANCE PREDICTION ENGINE v4.0 - EXAMPLE OUTPUT")
    print("=" * 80)

    regressor = RegressionPredictor()

    # CTR Prediction
    print("\n1. CTR PREDICTION (30 days)")
    ctr_pred = regressor.predict_ctr_30days(
        current_ctr=5.5,
        trend="improving",
    )
    print(json.dumps(ctr_pred, indent=2))

    # Conversion Prediction
    print("\n2. CONVERSION PREDICTION (30 days)")
    conv_pred = regressor.predict_conversion_30days(
        current_conversion=7.2,
        ctr=5.5,
    )
    print(json.dumps(conv_pred, indent=2))

    # ROI Prediction
    print("\n3. ROI PREDICTION (30 days)")
    roi_pred = regressor.predict_roi_30days(
        current_roi=120,
        ctr=5.5,
        conversion=7.2,
        avg_customer_value=150,
        current_ad_spend=20,
    )
    print(json.dumps(roi_pred, indent=2))

    # Success Probability
    print("\n4. SUCCESS PROBABILITY")
    success_model = SuccessProbabilityModel()
    success_prob = success_model.predict_success_probability(
        master_prompt_score=96,
        image_verification_score=91,
        quality_gates_passed=10,
        ctr=5.5,
        conversion=7.2,
        engagement_score=88,
    )
    print(json.dumps(success_prob, indent=2))

    # Optimization Recommendations
    print("\n5. OPTIMIZATION RECOMMENDATIONS")
    advisor = AdOptimizationAdvisor()
    recommendations = advisor.get_optimization_recommendations(
        ctr=5.5,
        conversion=7.2,
        engagement=88,
        master_prompt_score=96,
        image_quality=91,
    )
    print(json.dumps(recommendations, indent=2))
