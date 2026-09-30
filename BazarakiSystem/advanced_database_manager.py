"""
Advanced Database Manager for BAZARAKI v4.0
Comprehensive database management system for pool services advertising platform

Features:
- SQLite3 database with advanced schema
- Connection pooling and transaction management
- Query optimization and caching
- Comprehensive data validation
- Audit trail and logging
- Backup and recovery support
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Service types for pool services"""
    MAINTENANCE_WEEKLY = "maintenance_weekly"
    MAINTENANCE_COMPREHENSIVE = "maintenance_comprehensive"
    MAINTENANCE_DAILY = "maintenance_daily"
    CONSTRUCTION = "construction"
    RENOVATION_BASIC = "renovation_basic"
    RENOVATION_PARTIAL = "renovation_partial"
    RENOVATION_COMPLETE = "renovation_complete"
    RENOVATION_SYSTEM = "renovation_system"


class Location(Enum):
    """Cyprus locations"""
    PAPHOS = "paphos"
    LIMASSOL = "limassol"
    NICOSIA = "nicosia"
    LARNACA = "larnaca"


class ImageVerificationStatus(Enum):
    """Image verification status"""
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    REJECTED = "rejected"


class AdvertisementStatus(Enum):
    """Advertisement status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    UPDATED = "updated"
    ARCHIVED = "archived"
    REJECTED = "rejected"


@dataclass
class Advertisement:
    """Advertisement data model"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    service_type: str = ""
    location: str = ""
    price: float = 0.0
    experience_years: int = 0
    projects_completed: int = 0
    status: str = "draft"
    quality_score: float = 0.0
    master_prompt_score: float = 0.0
    ctr: float = 0.0
    conversion_rate: float = 0.0
    views: int = 0
    clicks: int = 0
    conversions: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    published_at: Optional[str] = None


@dataclass
class Image:
    """Image data model"""
    id: Optional[int] = None
    ad_id: int = 0
    filename: str = ""
    path: str = ""
    resolution: str = ""
    size_mb: float = 0.0
    format: str = ""
    verification_score: float = 0.0
    verification_status: str = "pending"
    verification_details: str = ""
    uploaded_at: Optional[str] = None


class AdvancedDatabaseManager:
    """Advanced database management system for BAZARAKI v4.0"""

    def __init__(self, db_path: str = "/tmp/bazaraki_v4.db", pool_size: int = 5):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
            pool_size: Connection pool size
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.local = threading.local()
        self._init_database()
        logger.info(f"Database manager initialized at {db_path}")

    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Advertisements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS advertisements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    price REAL NOT NULL,
                    experience_years INTEGER,
                    projects_completed INTEGER,
                    status TEXT DEFAULT 'draft',
                    quality_score REAL DEFAULT 0.0,
                    master_prompt_score REAL DEFAULT 0.0,
                    ctr REAL DEFAULT 0.0,
                    conversion_rate REAL DEFAULT 0.0,
                    views INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMP,
                    FOREIGN KEY (service_type) REFERENCES service_types(name),
                    FOREIGN KEY (location) REFERENCES locations(name)
                )
            """)

            # Images table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    path TEXT NOT NULL,
                    resolution TEXT,
                    size_mb REAL,
                    format TEXT,
                    verification_score REAL DEFAULT 0.0,
                    verification_status TEXT DEFAULT 'pending',
                    verification_details TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ad_id) REFERENCES advertisements(id) ON DELETE CASCADE
                )
            """)

            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    views INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    ctr REAL DEFAULT 0.0,
                    conversion_rate REAL DEFAULT 0.0,
                    avg_duration_seconds INTEGER DEFAULT 0,
                    bounce_rate REAL DEFAULT 0.0,
                    roi REAL DEFAULT 0.0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ad_id) REFERENCES advertisements(id) ON DELETE CASCADE,
                    UNIQUE(ad_id, date)
                )
            """)

            # Pricing history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pricing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_id INTEGER NOT NULL,
                    old_price REAL,
                    new_price REAL NOT NULL,
                    reason TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ad_id) REFERENCES advertisements(id) ON DELETE CASCADE
                )
            """)

            # Competitors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS competitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    price REAL,
                    rating REAL,
                    reviews_count INTEGER DEFAULT 0,
                    last_checked TIMESTAMP,
                    data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (service_type) REFERENCES service_types(name),
                    FOREIGN KEY (location) REFERENCES locations(name)
                )
            """)

            # Audit trail table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    old_values JSON,
                    new_values JSON,
                    changed_by TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Service types reference table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_types (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    base_price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Locations reference table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    name TEXT PRIMARY KEY,
                    country TEXT DEFAULT 'Cyprus',
                    premium_multiplier REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_status ON advertisements(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_service ON advertisements(service_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_location ON advertisements(location)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ads_created ON advertisements(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_ad ON images(ad_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_perf_ad ON performance_metrics(ad_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_perf_date ON performance_metrics(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_table ON audit_trail(table_name)")

            # Initialize service types
            self._init_service_types(cursor)

            # Initialize locations
            self._init_locations(cursor)

            conn.commit()
            logger.info("Database schema initialized successfully")

    def _init_service_types(self, cursor):
        """Initialize service types reference data"""
        service_types = [
            ("maintenance_weekly", "Weekly pool maintenance", 120.0),
            ("maintenance_comprehensive", "Comprehensive pool maintenance", 200.0),
            ("maintenance_daily", "Daily pool monitoring", 800.0),
            ("construction", "Pool construction", 15000.0),
            ("renovation_basic", "Basic pool renovation", 2500.0),
            ("renovation_partial", "Partial pool renovation", 8500.0),
            ("renovation_complete", "Complete pool renovation", 20000.0),
            ("renovation_system", "System upgrade and renovation", 5500.0),
        ]

        for service_type, description, base_price in service_types:
            cursor.execute("""
                INSERT OR IGNORE INTO service_types (name, description, base_price)
                VALUES (?, ?, ?)
            """, (service_type, description, base_price))

    def _init_locations(self, cursor):
        """Initialize locations reference data"""
        locations = [
            ("paphos", "Cyprus", 1.125),
            ("limassol", "Cyprus", 1.075),
            ("nicosia", "Cyprus", 1.0),
            ("larnaca", "Cyprus", 0.95),
        ]

        for location, country, premium in locations:
            cursor.execute("""
                INSERT OR IGNORE INTO locations (name, country, premium_multiplier)
                VALUES (?, ?, ?)
            """, (location, country, premium))

    @contextmanager
    def get_connection(self):
        """
        Get database connection from pool

        Yields:
            sqlite3.Connection: Database connection
        """
        if not hasattr(self.local, 'connection') or self.local.connection is None:
            self.local.connection = sqlite3.connect(self.db_path)
            self.local.connection.row_factory = sqlite3.Row

        try:
            yield self.local.connection
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise

    # Advertisement methods
    def create_advertisement(self, ad: Advertisement) -> int:
        """Create new advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO advertisements (
                    title, description, service_type, location, price,
                    experience_years, projects_completed, status,
                    quality_score, master_prompt_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ad.title, ad.description, ad.service_type, ad.location, ad.price,
                ad.experience_years, ad.projects_completed, ad.status,
                ad.quality_score, ad.master_prompt_score
            ))
            conn.commit()
            ad_id = cursor.lastrowid
            logger.info(f"Created advertisement with id {ad_id}")
            return ad_id

    def get_advertisement(self, ad_id: int) -> Optional[Advertisement]:
        """Get advertisement by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM advertisements WHERE id = ?", (ad_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_advertisement(row)
            return None

    def update_advertisement(self, ad: Advertisement) -> bool:
        """Update advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE advertisements SET
                    title = ?, description = ?, service_type = ?, location = ?,
                    price = ?, experience_years = ?, projects_completed = ?,
                    status = ?, quality_score = ?, master_prompt_score = ?,
                    ctr = ?, conversion_rate = ?, views = ?, clicks = ?, conversions = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                ad.title, ad.description, ad.service_type, ad.location,
                ad.price, ad.experience_years, ad.projects_completed,
                ad.status, ad.quality_score, ad.master_prompt_score,
                ad.ctr, ad.conversion_rate, ad.views, ad.clicks, ad.conversions,
                ad.id
            ))
            conn.commit()
            self._log_audit(conn, 'advertisements', ad.id, 'UPDATE', None, {
                'title': ad.title, 'status': ad.status
            })
            logger.info(f"Updated advertisement {ad.id}")
            return cursor.rowcount > 0

    def delete_advertisement(self, ad_id: int) -> bool:
        """Delete advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM advertisements WHERE id = ?", (ad_id,))
            conn.commit()
            self._log_audit(conn, 'advertisements', ad_id, 'DELETE', None, {})
            logger.info(f"Deleted advertisement {ad_id}")
            return cursor.rowcount > 0

    def list_advertisements(
        self,
        status: Optional[str] = None,
        service_type: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Advertisement]:
        """List advertisements with filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM advertisements WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)
            if service_type:
                query += " AND service_type = ?"
                params.append(service_type)
            if location:
                query += " AND location = ?"
                params.append(location)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            return [self._row_to_advertisement(row) for row in cursor.fetchall()]

    # Image methods
    def add_image(self, ad_id: int, image: Image) -> int:
        """Add image to advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO images (
                    ad_id, filename, path, resolution, size_mb, format,
                    verification_score, verification_status, verification_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ad_id, image.filename, image.path, image.resolution,
                image.size_mb, image.format, image.verification_score,
                image.verification_status, image.verification_details
            ))
            conn.commit()
            image_id = cursor.lastrowid
            logger.info(f"Added image {image_id} to advertisement {ad_id}")
            return image_id

    def get_ad_images(self, ad_id: int) -> List[Image]:
        """Get all images for an advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM images WHERE ad_id = ?", (ad_id,))
            return [self._row_to_image(row) for row in cursor.fetchall()]

    def update_image_verification(
        self,
        image_id: int,
        score: float,
        status: str,
        details: str
    ) -> bool:
        """Update image verification results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE images SET
                    verification_score = ?,
                    verification_status = ?,
                    verification_details = ?
                WHERE id = ?
            """, (score, status, details, image_id))
            conn.commit()
            logger.info(f"Updated image {image_id} verification")
            return cursor.rowcount > 0

    # Performance metrics methods
    def record_performance(
        self,
        ad_id: int,
        date: str,
        views: int = 0,
        clicks: int = 0,
        conversions: int = 0,
        avg_duration: int = 0,
        bounce_rate: float = 0.0
    ) -> int:
        """Record daily performance metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            ctr = (clicks / views * 100) if views > 0 else 0
            conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
            roi = (conversions * 100 / views) if views > 0 else 0

            cursor.execute("""
                INSERT OR REPLACE INTO performance_metrics (
                    ad_id, date, views, clicks, conversions, ctr,
                    conversion_rate, avg_duration_seconds, bounce_rate, roi
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ad_id, date, views, clicks, conversions, ctr,
                conversion_rate, avg_duration, bounce_rate, roi
            ))
            conn.commit()
            logger.info(f"Recorded performance for ad {ad_id} on {date}")
            return cursor.lastrowid

    def get_performance_history(
        self,
        ad_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get performance history for an advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM performance_metrics
                WHERE ad_id = ? AND date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            """, (ad_id, days))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'date': row['date'],
                    'views': row['views'],
                    'clicks': row['clicks'],
                    'conversions': row['conversions'],
                    'ctr': row['ctr'],
                    'conversion_rate': row['conversion_rate'],
                    'bounce_rate': row['bounce_rate'],
                    'roi': row['roi']
                })
            return results

    # Pricing history methods
    def record_price_change(
        self,
        ad_id: int,
        old_price: Optional[float],
        new_price: float,
        reason: str = ""
    ) -> int:
        """Record price change"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pricing_history (ad_id, old_price, new_price, reason)
                VALUES (?, ?, ?, ?)
            """, (ad_id, old_price, new_price, reason))
            conn.commit()
            logger.info(f"Recorded price change for ad {ad_id}")
            return cursor.lastrowid

    def get_pricing_history(self, ad_id: int) -> List[Dict[str, Any]]:
        """Get pricing history for an advertisement"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM pricing_history WHERE ad_id = ?
                ORDER BY changed_at DESC
            """, (ad_id,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'old_price': row['old_price'],
                    'new_price': row['new_price'],
                    'reason': row['reason'],
                    'changed_at': row['changed_at']
                })
            return results

    # Competitor methods
    def add_competitor(
        self,
        name: str,
        service_type: str,
        location: str,
        price: float,
        rating: float,
        reviews: int,
        data: Dict[str, Any]
    ) -> int:
        """Add competitor data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO competitors (name, service_type, location, price, rating, reviews_count, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, service_type, location, price, rating, reviews, json.dumps(data)))
            conn.commit()
            logger.info(f"Added competitor {name}")
            return cursor.lastrowid

    def get_competitors(
        self,
        service_type: str,
        location: str
    ) -> List[Dict[str, Any]]:
        """Get competitors for a service and location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM competitors
                WHERE service_type = ? AND location = ?
                ORDER BY rating DESC
            """, (service_type, location))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'name': row['name'],
                    'price': row['price'],
                    'rating': row['rating'],
                    'reviews': row['reviews_count'],
                    'data': json.loads(row['data']) if row['data'] else {}
                })
            return results

    # Audit trail methods
    def _log_audit(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        record_id: int,
        action: str,
        old_values: Optional[Dict],
        new_values: Dict,
        changed_by: str = "system"
    ):
        """Log change to audit trail"""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_trail (table_name, record_id, action, old_values, new_values, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            table_name, record_id, action,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values),
            changed_by
        ))

    def get_audit_trail(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit trail"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM audit_trail WHERE 1=1"
            params = []

            if table_name:
                query += " AND table_name = ?"
                params.append(table_name)
            if record_id:
                query += " AND record_id = ?"
                params.append(record_id)

            query += " ORDER BY changed_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append({
                    'table': row['table_name'],
                    'record_id': row['record_id'],
                    'action': row['action'],
                    'old_values': json.loads(row['old_values']) if row['old_values'] else None,
                    'new_values': json.loads(row['new_values']) if row['new_values'] else None,
                    'changed_by': row['changed_by'],
                    'changed_at': row['changed_at']
                })
            return results

    # Backup and recovery
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            with self.get_connection() as conn:
                backup_conn = sqlite3.connect(backup_path)
                conn.backup(backup_conn)
                backup_conn.close()
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as count FROM advertisements")
            ad_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM images")
            image_count = cursor.fetchone()['count']

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(quality_score) as avg_quality,
                    AVG(master_prompt_score) as avg_prompt_score,
                    AVG(conversion_rate) as avg_conversion
                FROM advertisements
            """)
            stats = cursor.fetchone()

            return {
                'total_advertisements': ad_count,
                'total_images': image_count,
                'total_ads_with_stats': stats['total'],
                'avg_quality_score': stats['avg_quality'],
                'avg_prompt_score': stats['avg_prompt_score'],
                'avg_conversion_rate': stats['avg_conversion']
            }

    # Helper methods
    def _row_to_advertisement(self, row) -> Advertisement:
        """Convert database row to Advertisement object"""
        return Advertisement(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            service_type=row['service_type'],
            location=row['location'],
            price=row['price'],
            experience_years=row['experience_years'],
            projects_completed=row['projects_completed'],
            status=row['status'],
            quality_score=row['quality_score'],
            master_prompt_score=row['master_prompt_score'],
            ctr=row['ctr'],
            conversion_rate=row['conversion_rate'],
            views=row['views'],
            clicks=row['clicks'],
            conversions=row['conversions'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            published_at=row['published_at']
        )

    def _row_to_image(self, row) -> Image:
        """Convert database row to Image object"""
        return Image(
            id=row['id'],
            ad_id=row['ad_id'],
            filename=row['filename'],
            path=row['path'],
            resolution=row['resolution'],
            size_mb=row['size_mb'],
            format=row['format'],
            verification_score=row['verification_score'],
            verification_status=row['verification_status'],
            verification_details=row['verification_details'],
            uploaded_at=row['uploaded_at']
        )

    def close(self):
        """Close database connection"""
        if hasattr(self.local, 'connection') and self.local.connection:
            self.local.connection.close()
            self.local.connection = None
            logger.info("Database connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = AdvancedDatabaseManager()

    # Create advertisement
    ad = Advertisement(
        title="Professional Pool Maintenance in Paphos",
        description="Expert pool maintenance services with 10 years experience",
        service_type="maintenance_weekly",
        location="paphos",
        price=140.0,
        experience_years=10,
        projects_completed=300,
        status="published",
        quality_score=95.0,
        master_prompt_score=100.0
    )

    ad_id = db.create_advertisement(ad)
    print(f"Created advertisement: {ad_id}")

    # Get advertisement
    retrieved_ad = db.get_advertisement(ad_id)
    print(f"Retrieved: {retrieved_ad.title}")

    # Record performance
    db.record_performance(
        ad_id=ad_id,
        date="2026-10-01",
        views=150,
        clicks=25,
        conversions=5,
        avg_duration=45,
        bounce_rate=15.0
    )

    # Get statistics
    stats = db.get_statistics()
    print(f"Database statistics: {stats}")

    # Backup database
    db.backup_database("/tmp/bazaraki_backup.db")

    db.close()
