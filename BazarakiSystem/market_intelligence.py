"""
MARKET INTELLIGENCE ENGINE
Cyprus Marketplace Analysis & Competitive Intelligence
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import json

@dataclass
class MarketSegment:
    category: str
    subcategory: str
    market_rate_min: float
    market_rate_max: float
    market_rate_avg: float
    price_unit: str
    seasonality_factor: float
    demand_level: str
    competitor_count: int
    market_saturation: str

class CyprusMarketAnalyzer:
    """
    Analyzes Cyprus Bazaraki marketplace:
    - Service pricing by category
    - Seasonal demand patterns
    - Competitor density
    - Geographic price variations
    - Search volume trends
    """

    MARKET_DATA = {
        'painting': {
            'interior_painting': {
                'min': 15, 'max': 35, 'avg': 25,
                'unit': '€/m²',
                'demand': 'high',
                'seasonality': 1.3,  # 30% seasonal boost
                'competitors': 45,
                'saturation': 'medium'
            },
            'exterior_painting': {
                'min': 20, 'max': 45, 'avg': 32,
                'unit': '€/m²',
                'demand': 'high',
                'seasonality': 1.5,  # 50% seasonal boost (spring/summer)
                'competitors': 38,
                'saturation': 'medium'
            },
            'protective_coatings': {
                'min': 25, 'max': 60, 'avg': 42,
                'unit': '€/m²',
                'demand': 'medium',
                'seasonality': 1.2,
                'competitors': 22,
                'saturation': 'low-medium'
            }
        },
        'plasterboard': {
            'partition_walls': {
                'min': 30, 'max': 80, 'avg': 55,
                'unit': '€/m²',
                'demand': 'high',
                'seasonality': 1.1,
                'competitors': 52,
                'saturation': 'high'
            },
            'ceiling_installation': {
                'min': 25, 'max': 70, 'avg': 48,
                'unit': '€/m²',
                'demand': 'high',
                'seasonality': 1.15,
                'competitors': 41,
                'saturation': 'medium-high'
            },
            'repair_patching': {
                'min': 15, 'max': 40, 'avg': 27,
                'unit': '€/m²',
                'demand': 'medium',
                'seasonality': 1.0,
                'competitors': 35,
                'saturation': 'medium'
            }
        },
        'tiling': {
            'floor_tiling': {
                'min': 20, 'max': 50, 'avg': 35,
                'unit': '€/m²',
                'demand': 'high',
                'seasonality': 1.2,
                'competitors': 48,
                'saturation': 'medium-high'
            },
            'wall_tiling': {
                'min': 18, 'max': 45, 'avg': 31,
                'unit': '€/m²',
                'demand': 'high',
                'seasonality': 1.15,
                'competitors': 44,
                'saturation': 'medium-high'
            },
            'specialty_tiling': {
                'min': 35, 'max': 80, 'avg': 57,
                'unit': '€/m²',
                'demand': 'low-medium',
                'seasonality': 1.0,
                'competitors': 18,
                'saturation': 'low'
            }
        },
        'plumbing': {
            'installation': {
                'min': 60, 'max': 150, 'avg': 100,
                'unit': '€/job',
                'demand': 'high',
                'seasonality': 1.2,
                'competitors': 42,
                'saturation': 'medium'
            },
            'repair': {
                'min': 40, 'max': 100, 'avg': 70,
                'unit': '€/call',
                'demand': 'high',
                'seasonality': 1.3,  # More emergency calls in winter
                'competitors': 55,
                'saturation': 'high'
            },
            'maintenance': {
                'min': 30, 'max': 80, 'avg': 55,
                'unit': '€/visit',
                'demand': 'medium',
                'seasonality': 1.1,
                'competitors': 33,
                'saturation': 'medium'
            }
        },
        'electrical': {
            'installation': {
                'min': 80, 'max': 200, 'avg': 140,
                'unit': '€/job',
                'demand': 'high',
                'seasonality': 1.15,
                'competitors': 38,
                'saturation': 'medium'
            },
            'repair': {
                'min': 50, 'max': 120, 'avg': 85,
                'unit': '€/call',
                'demand': 'high',
                'seasonality': 1.2,
                'competitors': 44,
                'saturation': 'medium-high'
            },
            'maintenance': {
                'min': 40, 'max': 100, 'avg': 70,
                'unit': '€/visit',
                'demand': 'medium',
                'seasonality': 1.0,
                'competitors': 28,
                'saturation': 'medium'
            }
        },
        'renovation': {
            'kitchen_renovation': {
                'min': 3000, 'max': 12000, 'avg': 7500,
                'unit': 'EUR/job',
                'demand': 'high',
                'seasonality': 1.2,
                'competitors': 32,
                'saturation': 'medium'
            },
            'bathroom_renovation': {
                'min': 2500, 'max': 10000, 'avg': 6000,
                'unit': 'EUR/job',
                'demand': 'high',
                'seasonality': 1.2,
                'competitors': 35,
                'saturation': 'medium'
            },
            'full_renovation': {
                'min': 15000, 'max': 80000, 'avg': 45000,
                'unit': 'EUR/job',
                'demand': 'medium',
                'seasonality': 1.1,
                'competitors': 22,
                'saturation': 'low-medium'
            }
        },
        'pool_services': {
            'pool_maintenance': {
                'min': 80, 'max': 200, 'avg': 140,
                'unit': '€/month',
                'demand': 'very-high',
                'seasonality': 1.6,  # 60% seasonal boost (summer peak)
                'competitors': 22,
                'saturation': 'low-medium',
                'profitability': 'very-high'
            },
            'pool_renovation': {
                'min': 4000, 'max': 25000, 'avg': 12000,
                'unit': 'EUR/job',
                'demand': 'high',
                'seasonality': 1.4,  # Spring preparation
                'competitors': 15,
                'saturation': 'low',
                'profitability': 'very-high'
            },
            'pool_cleaning': {
                'min': 40, 'max': 120, 'avg': 75,
                'unit': '€/visit',
                'demand': 'high',
                'seasonality': 1.5,  # Summer peak
                'competitors': 35,
                'saturation': 'medium',
                'profitability': 'high'
            },
            'pool_equipment_repair': {
                'min': 100, 'max': 300, 'avg': 180,
                'unit': '€/call',
                'demand': 'high',
                'seasonality': 1.4,
                'competitors': 20,
                'saturation': 'low-medium',
                'profitability': 'very-high'
            }
        },
        'hvac_services': {
            'ac_installation': {
                'min': 600, 'max': 1500, 'avg': 1000,
                'unit': 'EUR/unit',
                'demand': 'very-high',
                'seasonality': 1.8,  # 80% seasonal boost (summer heat)
                'competitors': 25,
                'saturation': 'low-medium',
                'profitability': 'very-high'
            },
            'ac_repair_maintenance': {
                'min': 60, 'max': 150, 'avg': 100,
                'unit': '€/call',
                'demand': 'very-high',
                'seasonality': 1.7,
                'competitors': 30,
                'saturation': 'medium',
                'profitability': 'high'
            }
        },
        'garden_landscaping': {
            'garden_design': {
                'min': 1000, 'max': 5000, 'avg': 2500,
                'unit': 'EUR/project',
                'demand': 'high',
                'seasonality': 1.3,
                'competitors': 20,
                'saturation': 'low-medium',
                'profitability': 'high'
            },
            'garden_maintenance': {
                'min': 50, 'max': 150, 'avg': 90,
                'unit': '€/visit',
                'demand': 'high',
                'seasonality': 1.4,
                'competitors': 40,
                'saturation': 'medium-high',
                'profitability': 'medium-high'
            },
            'landscaping': {
                'min': 2000, 'max': 15000, 'avg': 7000,
                'unit': 'EUR/project',
                'demand': 'medium-high',
                'seasonality': 1.2,
                'competitors': 25,
                'saturation': 'medium',
                'profitability': 'high'
            }
        },
        'solar_renewable': {
            'solar_installation': {
                'min': 3500, 'max': 12000, 'avg': 7500,
                'unit': 'EUR/system',
                'demand': 'very-high',
                'seasonality': 1.2,
                'competitors': 18,
                'saturation': 'low',
                'profitability': 'very-high'
            },
            'solar_maintenance': {
                'min': 80, 'max': 200, 'avg': 130,
                'unit': '€/year',
                'demand': 'high',
                'seasonality': 1.1,
                'competitors': 22,
                'saturation': 'low-medium',
                'profitability': 'high'
            }
        }
    }

    GEOGRAPHIC_ADJUSTMENTS = {
        'paphos': 1.0,      # Baseline
        'polis': 1.0,       # Similar to Paphos
        'larnaca': 1.05,    # Slightly higher demand
        'limassol': 1.1,    # Higher demand, urban
        'nicosia': 1.15,    # Capital, highest demand
        'famagusta': 0.9    # Lower demand
    }

    SEASONAL_FACTORS = {
        'Q1': 1.0,   # January-March (low)
        'Q2': 1.4,   # April-June (high - spring work)
        'Q3': 1.3,   # July-September (high - pre-winter)
        'Q4': 0.8    # October-December (low - winter)
    }

    def get_market_rate(self, category: str, subcategory: str,
                       location: str = 'paphos', season: str = 'Q2') -> Dict:
        """
        Calculate market rate for service with adjustments:
        - Base market rate for category
        - Geographic adjustment (±15%)
        - Seasonal adjustment (±40%)
        - Demand factor
        """
        if category not in self.MARKET_DATA:
            return {'error': f'Category {category} not found'}

        if subcategory not in self.MARKET_DATA[category]:
            return {'error': f'Subcategory {subcategory} not found'}

        base_data = self.MARKET_DATA[category][subcategory]

        # Geographic multiplier
        geo_multiplier = self.GEOGRAPHIC_ADJUSTMENTS.get(location.lower(), 1.0)

        # Seasonal multiplier
        seasonal_multiplier = self.SEASONAL_FACTORS.get(season, 1.0)

        # Calculate adjusted rates
        return {
            'category': category,
            'subcategory': subcategory,
            'location': location,
            'season': season,
            'base_min': base_data['min'],
            'base_max': base_data['max'],
            'base_avg': base_data['avg'],
            'price_unit': base_data['unit'],
            'geo_adjusted_min': round(base_data['min'] * geo_multiplier, 2),
            'geo_adjusted_max': round(base_data['max'] * geo_multiplier, 2),
            'geo_adjusted_avg': round(base_data['avg'] * geo_multiplier, 2),
            'season_adjusted_min': round(base_data['min'] * geo_multiplier * seasonal_multiplier, 2),
            'season_adjusted_max': round(base_data['max'] * geo_multiplier * seasonal_multiplier, 2),
            'season_adjusted_avg': round(base_data['avg'] * geo_multiplier * seasonal_multiplier, 2),
            'recommended_price': round(base_data['avg'] * geo_multiplier * seasonal_multiplier * 0.95, 2),  # 5% discount for competitiveness
            'demand_level': base_data['demand'],
            'seasonality_boost': f"{(seasonal_multiplier - 1) * 100:+.0f}%",
            'competitor_count': base_data['competitors'],
            'market_saturation': base_data['saturation']
        }

    def get_search_volume_trends(self, category: str) -> Dict:
        """Get estimated search volume and trend data"""
        search_data = {
            'painting': {'monthly_searches': 450, 'trend': 'stable', 'growth': 0.05},
            'plasterboard': {'monthly_searches': 380, 'trend': 'growing', 'growth': 0.12},
            'tiling': {'monthly_searches': 420, 'trend': 'stable', 'growth': 0.03},
            'plumbing': {'monthly_searches': 520, 'trend': 'stable', 'growth': 0.08},
            'electrical': {'monthly_searches': 480, 'trend': 'growing', 'growth': 0.10},
            'renovation': {'monthly_searches': 350, 'trend': 'growing', 'growth': 0.15}
        }
        return search_data.get(category, {'monthly_searches': 300, 'trend': 'unknown', 'growth': 0})

    def analyze_competitor_landscape(self, category: str, location: str = 'paphos') -> Dict:
        """Analyze competitive environment"""
        base_competitors = self.MARKET_DATA.get(category, {})

        total_competitors = sum(
            data.get('competitors', 0)
            for data in base_competitors.values()
        )

        geo_adjustment = self.GEOGRAPHIC_ADJUSTMENTS.get(location.lower(), 1.0)
        local_competitors = int(total_competitors * geo_adjustment)

        avg_rating = 4.2  # Placeholder: would come from actual Bazaraki data
        avg_response_time = '2-4 hours'  # Placeholder

        return {
            'category': category,
            'location': location,
            'estimated_competitors': local_competitors,
            'competition_level': 'high' if local_competitors > 40 else 'medium' if local_competitors > 20 else 'low',
            'market_opportunity': 'low' if local_competitors > 50 else 'medium' if local_competitors > 25 else 'high',
            'avg_competitor_rating': avg_rating,
            'avg_response_time': avg_response_time,
            'saturation_risk': 'high' if local_competitors > 50 else 'medium' if local_competitors > 30 else 'low'
        }

    def get_pricing_commercial_analysis(self, category: str, subcategory: str,
                                       location: str = 'paphos') -> Dict:
        """
        Advanced pricing analysis separating:
        - Market price (what market charges)
        - Listed price (what competitors list)
        - Negotiation price (what customers actually pay)
        - Minimum viable (break-even cost)
        - Customer value (what customers perceive value as)
        """
        rate_data = self.get_market_rate(category, subcategory, location)

        if 'error' in rate_data:
            return rate_data

        base_avg = rate_data['season_adjusted_avg']

        return {
            'market_price': base_avg,
            'listed_price': round(base_avg * 1.1, 2),  # Competitors list 10% higher
            'negotiation_price': round(base_avg * 0.92, 2),  # Customers negotiate down 8%
            'minimum_viable': round(base_avg * 0.65, 2),  # Minimum cost to deliver
            'customer_value': round(base_avg * 1.25, 2),  # Perceived value by customer
            'recommended_position': 'competitive',  # Position strategy
            'margin_guidance': f"{((base_avg - (base_avg * 0.65)) / base_avg * 100):.0f}% gross margin"
        }

def test_market_intelligence():
    """Test market intelligence engine"""
    print("\n📊 CYPRUS MARKET INTELLIGENCE TEST")
    print("=" * 70)

    analyzer = CyprusMarketAnalyzer()

    # Test 1: Market rate calculation
    print("\nMarket Rate Analysis - Plasterboard Partition Walls:")
    print("-" * 70)
    rate = analyzer.get_market_rate('plasterboard', 'partition_walls', 'paphos', 'Q2')
    for key, value in rate.items():
        print(f"  {key}: {value}")

    # Test 2: Competitor analysis
    print("\n\nCompetitor Landscape - Paphos Painting Services:")
    print("-" * 70)
    comp = analyzer.analyze_competitor_landscape('painting', 'paphos')
    for key, value in comp.items():
        print(f"  {key}: {value}")

    # Test 3: Search volume trends
    print("\n\nSearch Volume Trends - Plasterboard Category:")
    print("-" * 70)
    trends = analyzer.get_search_volume_trends('plasterboard')
    for key, value in trends.items():
        print(f"  {key}: {value}")

    # Test 4: Pricing commercial analysis
    print("\n\nCommercial Pricing Analysis - Interior Painting in Limassol:")
    print("-" * 70)
    pricing = analyzer.get_pricing_commercial_analysis('painting', 'interior_painting', 'limassol')
    for key, value in pricing.items():
        print(f"  {key}: {value}")

    # Test 5: Geographic comparison
    print("\n\nGeographic Price Comparison - Plasterboard Partition Walls (Q2):")
    print("-" * 70)
    locations = ['paphos', 'larnaca', 'limassol', 'nicosia']
    for loc in locations:
        rate = analyzer.get_market_rate('plasterboard', 'partition_walls', loc, 'Q2')
        print(f"  {loc.upper():12} - Recommended: €{rate['recommended_price']:.2f}/m² | Competitors: {rate['competitor_count']:2d} | Saturation: {rate['market_saturation']}")

if __name__ == '__main__':
    test_market_intelligence()
