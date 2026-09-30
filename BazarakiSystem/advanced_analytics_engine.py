"""
BAZARAKI Advanced Analytics Engine v4.0
Real-Time Performance Tracking and Engagement Scoring

Features:
- Real-time performance tracking
- CTR, conversion rate, ROI calculations
- Engagement scoring (35% CTR + 40% conversion + 15% bounce + 10% duration)
- Ad status classification (5 tiers)
- Performance trending
- JSON export for integration
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class AdStatus(Enum):
    """Advertisement performance status"""
    EXCELLENT = ("excellent", 0.90)  # 90-100%
    GOOD = ("good", 0.75)  # 75-89%
    AVERAGE = ("average", 0.50)  # 50-74%
    POOR = ("poor", 0.25)  # 25-49%
    CRITICAL = ("critical", 0.0)  # <25%


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    date: str
    impressions: int
    clicks: int
    conversions: int
    ctr: float  # Click-through rate %
    conversion_rate: float  # %
    roi: float  # %
    bounce_rate: float  # %
    avg_duration: float  # seconds
    engagement_score: float  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class AdvancedAnalyticsEngine:
    """Real-time analytics and performance tracking"""

    def __init__(self):
        """Initialize analytics engine"""
        self.logger = logging.getLogger(__name__)
        self.performance_data = {}
        self.status_history = {}

    def calculate_ctr(self, clicks: int, impressions: int) -> float:
        """Calculate Click-Through Rate"""
        if impressions == 0:
            return 0.0
        return (clicks / impressions) * 100

    def calculate_conversion_rate(self, conversions: int, clicks: int) -> float:
        """Calculate conversion rate"""
        if clicks == 0:
            return 0.0
        return (conversions / clicks) * 100

    def calculate_roi(
        self,
        revenue: float,
        ad_spend: float,
    ) -> float:
        """Calculate Return on Investment"""
        if ad_spend == 0:
            return 0.0
        return ((revenue - ad_spend) / ad_spend) * 100

    def calculate_bounce_rate(
        self,
        bounces: int,
        sessions: int,
    ) -> float:
        """Calculate bounce rate"""
        if sessions == 0:
            return 0.0
        return (bounces / sessions) * 100

    def calculate_engagement_score(
        self,
        ctr: float,
        conversion_rate: float,
        bounce_rate: float,
        avg_duration: float,
        max_duration: float = 300.0,
    ) -> float:
        """
        Calculate comprehensive engagement score

        Formula:
        Engagement = (CTR × 0.35) + (Conversion × 0.40) + (Bounce_Inverted × 0.15) + (Duration × 0.10)

        Args:
            ctr: Click-through rate (%)
            conversion_rate: Conversion rate (%)
            bounce_rate: Bounce rate (%)
            avg_duration: Average time on page (seconds)
            max_duration: Maximum expected duration (seconds)

        Returns:
            Engagement score (0-100)
        """
        # Normalize metrics to 0-100 scale
        ctr_score = min(ctr * 2, 100)  # Max 5% CTR = 100
        conversion_score = min(conversion_rate * 10, 100)  # Max 10% conversion = 100
        bounce_inverted = max(0, 100 - bounce_rate)  # Inverted: lower bounce is better
        duration_score = min((avg_duration / max_duration) * 100, 100)

        # Calculate weighted engagement
        engagement = (
            (ctr_score * 0.35) +
            (conversion_score * 0.40) +
            (bounce_inverted * 0.15) +
            (duration_score * 0.10)
        )

        return min(engagement, 100.0)

    def classify_ad_status(self, engagement_score: float) -> Dict[str, Any]:
        """Classify advertisement status based on engagement"""
        if engagement_score >= 90:
            status = "excellent"
            description = "Outstanding performance - ready for scaling"
        elif engagement_score >= 75:
            status = "good"
            description = "Above average - performing well"
        elif engagement_score >= 50:
            status = "average"
            description = "Average performance - optimization recommended"
        elif engagement_score >= 25:
            status = "poor"
            description = "Below expectations - significant revision needed"
        else:
            status = "critical"
            description = "Critical performance - immediate action required"

        return {
            "status": status,
            "engagement_score": round(engagement_score, 1),
            "description": description,
            "action": self._get_recommended_action(status),
        }

    def _get_recommended_action(self, status: str) -> str:
        """Get recommended action for status"""
        actions = {
            "excellent": "Monitor performance, consider scaling budget",
            "good": "Continue current strategy, minor optimizations",
            "average": "A/B test different creatives and copy",
            "poor": "Revise targeting, copy, and creative elements",
            "critical": "Pause ad, completely redesign approach",
        }
        return actions.get(status, "Review performance data")

    def track_performance(
        self,
        ad_id: str,
        impressions: int,
        clicks: int,
        conversions: int,
        bounces: int,
        sessions: int,
        revenue: float,
        ad_spend: float,
        avg_duration: float,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track comprehensive ad performance

        Args:
            ad_id: Advertisement ID
            impressions: Number of impressions
            clicks: Number of clicks
            conversions: Number of conversions
            bounces: Number of bounce sessions
            sessions: Total sessions
            revenue: Revenue generated
            ad_spend: Ad spend
            avg_duration: Average session duration (seconds)
            date: Date of tracking (defaults to today)

        Returns:
            Performance metrics dictionary
        """
        if date is None:
            date = datetime.now().isoformat().split("T")[0]

        # Calculate metrics
        ctr = self.calculate_ctr(clicks, impressions)
        conversion_rate = self.calculate_conversion_rate(conversions, clicks)
        bounce_rate = self.calculate_bounce_rate(bounces, sessions)
        roi = self.calculate_roi(revenue, ad_spend)
        engagement_score = self.calculate_engagement_score(
            ctr, conversion_rate, bounce_rate, avg_duration
        )

        # Classify status
        status_info = self.classify_ad_status(engagement_score)

        # Store metrics
        metric = PerformanceMetric(
            date=date,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            ctr=round(ctr, 2),
            conversion_rate=round(conversion_rate, 2),
            roi=round(roi, 2),
            bounce_rate=round(bounce_rate, 2),
            avg_duration=round(avg_duration, 1),
            engagement_score=round(engagement_score, 1),
        )

        if ad_id not in self.performance_data:
            self.performance_data[ad_id] = []

        self.performance_data[ad_id].append(metric)

        result = {
            "ad_id": ad_id,
            "date": date,
            "metrics": metric.to_dict(),
            "status": status_info,
            "roi": round(roi, 2),
            "tracked_at": datetime.now().isoformat(),
        }

        self.logger.info(
            f"Performance tracked for ad {ad_id}: "
            f"CTR {ctr:.2f}%, Conversion {conversion_rate:.2f}%, "
            f"Engagement {engagement_score:.1f}"
        )

        return result

    def get_performance_trend(
        self,
        ad_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get performance trends over time"""
        if ad_id not in self.performance_data:
            return {"ad_id": ad_id, "trend": None, "message": "No data available"}

        metrics = self.performance_data[ad_id][-days:]

        if not metrics:
            return {"ad_id": ad_id, "trend": None, "message": "No data for period"}

        # Calculate trend
        first = metrics[0]
        last = metrics[-1]

        ctr_change = last.ctr - first.ctr
        conversion_change = last.conversion_rate - first.conversion_rate
        engagement_change = last.engagement_score - first.engagement_score

        trend_direction = "improving" if engagement_change > 0 else "declining"

        return {
            "ad_id": ad_id,
            "period_days": len(metrics),
            "trend_direction": trend_direction,
            "changes": {
                "ctr": round(ctr_change, 2),
                "conversion_rate": round(conversion_change, 2),
                "engagement_score": round(engagement_change, 1),
            },
            "first_day": {
                "date": first.date,
                "engagement": first.engagement_score,
                "ctr": first.ctr,
            },
            "last_day": {
                "date": last.date,
                "engagement": last.engagement_score,
                "ctr": last.ctr,
            },
        }

    def get_summary_stats(self, ad_id: str) -> Dict[str, Any]:
        """Get summary statistics for an ad"""
        if ad_id not in self.performance_data:
            return {"ad_id": ad_id, "message": "No data available"}

        metrics = self.performance_data[ad_id]

        total_impressions = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        avg_ctr = sum(m.ctr for m in metrics) / len(metrics) if metrics else 0
        avg_conversion = sum(m.conversion_rate for m in metrics) / len(metrics) if metrics else 0
        avg_engagement = sum(m.engagement_score for m in metrics) / len(metrics) if metrics else 0

        return {
            "ad_id": ad_id,
            "total_data_points": len(metrics),
            "date_range": {
                "start": metrics[0].date,
                "end": metrics[-1].date,
            },
            "totals": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
            },
            "averages": {
                "ctr": round(avg_ctr, 2),
                "conversion_rate": round(avg_conversion, 2),
                "engagement_score": round(avg_engagement, 1),
            },
            "current_status": self.classify_ad_status(avg_engagement),
        }

    def export_to_json(self, ad_id: str, filename: str) -> str:
        """Export analytics data to JSON"""
        try:
            data = {
                "ad_id": ad_id,
                "exported_at": datetime.now().isoformat(),
                "summary": self.get_summary_stats(ad_id),
                "trend": self.get_performance_trend(ad_id),
                "all_metrics": [
                    m.to_dict() for m in self.performance_data.get(ad_id, [])
                ],
            }

            with open(filename, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Analytics exported to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Error exporting analytics: {e}")
            raise


# Example usage
if __name__ == "__main__":
    engine = AdvancedAnalyticsEngine()

    # Track performance over 7 days
    print("\n" + "=" * 80)
    print("ADVANCED ANALYTICS ENGINE v4.0 - EXAMPLE OUTPUT")
    print("=" * 80)

    for day in range(7):
        date = (datetime.now() - timedelta(days=7-day)).isoformat().split("T")[0]

        # Simulate improving performance
        impressions = 1000 + (day * 100)
        clicks = int(impressions * (0.03 + day * 0.002))
        conversions = max(1, int(clicks * (0.02 + day * 0.003)))

        result = engine.track_performance(
            ad_id="ad_123",
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            bounces=int(impressions * 0.15),
            sessions=clicks * 1.2,
            revenue=conversions * 50,
            ad_spend=100,
            avg_duration=45 + (day * 5),
            date=date,
        )

        print(f"\nDay {day + 1}: {result['date']}")
        print(f"  CTR: {result['metrics']['ctr']}%")
        print(f"  Conversion: {result['metrics']['conversion_rate']}%")
        print(f"  Engagement: {result['metrics']['engagement_score']}")
        print(f"  Status: {result['status']['status'].upper()}")

    # Get summary
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    summary = engine.get_summary_stats("ad_123")
    print(json.dumps(summary, indent=2))

    # Get trend
    print("\n" + "=" * 80)
    print("PERFORMANCE TREND")
    print("=" * 80)
    trend = engine.get_performance_trend("ad_123", days=7)
    print(json.dumps(trend, indent=2))
