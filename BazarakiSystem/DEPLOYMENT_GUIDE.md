# نظام BAZARAKI المستقل - دليل النشر والتزامن

**التاريخ:** 2026-10-01  
**الإصدار:** النظام الرئيسي المتكامل v2  
**الحالة:** جاهز للنشر على Windows و GitHub  

---

## 📦 ملفات النظام الكاملة

### ملفات Python الأساسية (5 ملفات):

1. **market_intelligence.py** (600+ سطر)
   - محلل السوق القبرصي
   - بيانات التسعير والمنافسة
   - التعديلات الموسمية

2. **advanced_copywriting_engine.py** (350+ سطر)
   - محرك الكتابة النفسية المتقدمة
   - إطار عمل PASTOR
   - الحفزات النفسية

3. **image_verification_engine.py** (600+ سطر)
   - نظام التحقق من الصور (4 مستويات)
   - القواعس الدقيقة لكل خدمة
   - التوافق مع Bazaraki

4. **master_system.py** (450+ سطر)
   - نظام التكامل الرئيسي
   - خط أنابيب 9 مراحل
   - 10 بوابات صعبة الفشل

5. **database_ledger.py** (NEW - قاعدة بيانات الخدمات)
   - دفتر الخدمات (Service Ledger)
   - إزالة التكرار (Deduplication)
   - تتبع الإحصائيات

### ملفات الوثائق (3 ملفات):

1. **SYSTEM_ARCHITECTURE.md** - العمارة الكاملة للنظام
2. **ADVANCED_EXAMPLES.md** - 4 أمثلة حقيقية مع التفاصيل
3. **README.md** - دليل البدء السريع

---

## 🚀 خطوات النشر على Windows

### المرحلة 1: إعداد البيئة

```batch
# 1. تثبيت Python 3.10+
# (تحميل من python.org)

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# المتطلبات المطلوبة:
# - requests==2.31.0
# - pillow==10.0.0
# - imagehash==4.3.1
# - numpy==1.24.0
# - sqlite3 (مدمج)
```

### المرحلة 2: نسخ النظام إلى Windows

**المسار المقترح:** `C:\BazarakiSystem\`

```
C:\BazarakiSystem\
├── market_intelligence.py
├── advanced_copywriting_engine.py
├── image_verification_engine.py
├── master_system.py
├── database_ledger.py
├── config.json
├── data/
│   ├── market_data.db (SQLite)
│   ├── service_ledger.db
│   └── images/ (مجلد الصور)
├── output/
│   ├── generated_ads/
│   └── logs/
└── docs/
    ├── SYSTEM_ARCHITECTURE.md
    ├── ADVANCED_EXAMPLES.md
    └── README.md
```

### المرحلة 3: إنشاء ملف الإعدادات (config.json)

```json
{
  "system": {
    "name": "Bazaraki Autonomous System",
    "version": "2.0",
    "environment": "production"
  },
  "bazaraki": {
    "account_email": "your_bazaraki_email@example.com",
    "api_enabled": true,
    "auto_submit": false
  },
  "market": {
    "currency": "EUR",
    "locations": ["paphos", "limassol", "larnaca", "nicosia"],
    "update_frequency": "daily"
  },
  "images": {
    "minimum_per_ad": 5,
    "verification_strict": true,
    "quality_threshold": 75
  },
  "quality": {
    "hard_fail_gates": 10,
    "min_optimization_score": 75,
    "psychological_check": true
  },
  "batch_processing": {
    "daily_target": 100,
    "batch_size": 10,
    "time_between_batches_seconds": 300
  },
  "paths": {
    "database": "data/",
    "output": "output/",
    "images": "data/images/",
    "logs": "output/logs/"
  }
}
```

---

## 🔄 تزامن GitHub

### خطوة 1: إنشاء مستودع GitHub

```bash
# على جهاز Windows (في مجلد BazarakiSystem):

git init
git config user.name "Your Name"
git config user.email "leo@alshatnawe.com"

# إضافة الملفات
git add .

# الالتزام الأول
git commit -m "Initial commit: Bazaraki Autonomous System v2 - Complete integration with market intelligence, psychological copywriting, and image verification"

# إضافة بعيد GitHub
git remote add origin https://github.com/YOUR_USERNAME/bazaraki-autonomous-system.git

# الدفع
git push -u origin main
```

### خطوة 2: ملف .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# Output
output/generated_ads/
temp/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Sensitive
config_local.json
*.key
credentials.json
```

### خطوة 3: إعداد التزامن التلقائي

**للتزامن التلقائي يومياً (Windows Task Scheduler):**

```batch
REM ملف: sync_to_github.bat
cd C:\BazarakiSystem

REM سحب آخر التحديثات
git pull origin main

REM إضافة التغييرات
git add .

REM الالتزام (إذا كانت هناك تغييرات)
git commit -m "Daily update: %date% %time%"

REM الدفع
git push origin main

REM تسجيل الوقت
echo Synced at %date% %time% >> logs/sync_log.txt
```

**جدولة المهمة في Windows:**
1. افتح Task Scheduler
2. اختر: Create Basic Task
3. اسم المهمة: "Bazaraki GitHub Sync"
4. الجدول: يومياً في الساعة 08:00 صباحاً
5. الإجراء: تشغيل البرنامج `C:\BazarakiSystem\sync_to_github.bat`

---

## 🔐 إعداد GitHub Secrets (للأتمتة المستقبلية)

إذا كنت تريد إضافة CI/CD:

```yaml
# .github/workflows/daily_sync.yml
name: Daily Sync

on:
  schedule:
    - cron: '0 8 * * *'  # كل يوم في 08:00 UTC

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Pull latest changes
        run: git pull
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Daily update: $(date)" || true
      - name: Push changes
        run: git push
```

---

## 📊 هيكل قاعدة البيانات

### database_ledger.py (ملف جديد):

```python
"""
نظام دفتر الخدمات - إزالة التكرار والتتبع
"""

import sqlite3
from datetime import datetime
from typing import List, Dict

class ServiceLedger:
    """دفتر خدمات Bazaraki - تتبع الإعلانات والصور والإحصائيات"""
    
    def __init__(self, db_path: str = 'data/service_ledger.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الإعلانات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advertisements (
                ad_id TEXT PRIMARY KEY,
                service_type TEXT,
                location TEXT,
                title TEXT,
                description TEXT,
                price TEXT,
                quality_score REAL,
                optimization_score REAL,
                status TEXT,
                created_at TIMESTAMP,
                submitted_to_bazaraki BOOLEAN,
                inquiry_count INTEGER DEFAULT 0
            )
        ''')
        
        # جدول الصور
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                image_id TEXT PRIMARY KEY,
                image_path TEXT,
                quality_score REAL,
                alignment_score REAL,
                bazaraki_compliant BOOLEAN,
                psychological_alignment TEXT,
                used_in_ads INTEGER,
                created_at TIMESTAMP
            )
        ''')
        
        # جدول الخدمات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id TEXT PRIMARY KEY,
                service_type TEXT,
                subcategory TEXT,
                market_rate REAL,
                competitors INTEGER,
                demand_level TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        # جدول التعلم (الحفزات الناجحة)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                metric_id TEXT PRIMARY KEY,
                psychological_trigger TEXT,
                service_type TEXT,
                inquiry_rate REAL,
                conversion_rate REAL,
                effectiveness_score REAL,
                last_updated TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_advertisement(self, ad_data: Dict) -> bool:
        """إضافة إعلان إلى الدفتر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO advertisements 
            (ad_id, service_type, location, title, description, price, 
             quality_score, optimization_score, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ad_data['service_id'],
            ad_data['service_type'],
            ad_data['location'],
            ad_data['title'],
            ad_data['description'],
            ad_data['price'],
            ad_data['quality_score'],
            ad_data['optimization_score'],
            ad_data['status'],
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def prevent_duplicate(self, title: str, service_type: str, location: str) -> bool:
        """فحص التكرار - إذا وجد إعلان متطابق خلال آخر 30 يوم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM advertisements 
            WHERE title = ? AND service_type = ? AND location = ?
            AND datetime(created_at) > datetime('now', '-30 days')
        ''', (title, service_type, location))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count == 0  # True إذا لم يكن هناك تكرار
    
    def get_top_performing_triggers(self) -> List[Dict]:
        """الحصول على أفضل الحفزات النفسية الناجحة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT psychological_trigger, effectiveness_score, conversion_rate
            FROM learning_metrics
            ORDER BY effectiveness_score DESC
            LIMIT 10
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'trigger': r[0],
                'effectiveness': r[1],
                'conversion': r[2]
            }
            for r in results
        ]
```

---

## 🎯 تشغيل النظام على Windows

### الخيار 1: تشغيل يدوي

```batch
cd C:\BazarakiSystem
python master_system.py
```

### الخيار 2: جدولة النظام (أتمتة يومية)

**إنشاء ملف:**  `run_daily_batch.py`

```python
import schedule
import time
from master_system import BazarakiMasterSystem
from database_ledger import ServiceLedger

def run_daily_batch():
    system = BazarakiMasterSystem()
    ledger = ServiceLedger()
    
    # قائمة الخدمات اليومية
    services = [
        {'type': 'pool_services', 'subcategory': 'pool_maintenance'},
        {'type': 'pool_services', 'subcategory': 'pool_renovation'},
        {'type': 'hvac_services', 'subcategory': 'ac_installation'},
        {'type': 'solar_renewable', 'subcategory': 'solar_installation'},
        # ... إضافة 20 خدمة أخرى لإنتاج 100 إعلان يومياً
    ]
    
    for service in services:
        # إنشاء 10 إعلانات لكل خدمة = 100 إعلان يومياً
        for i in range(10):
            config = {
                'type': service['type'],
                'subcategory': service['subcategory'],
                'location': ['paphos', 'limassol', 'larnaca', 'nicosia'][i % 4],
                'buyer_type': ['remote_owner', 'local_owner', 'investor'][i % 3]
            }
            
            # تحميل الصور من المجلد
            images = get_verified_images_for_service(service['type'])
            
            # إنشاء الإعلان
            package = system.generate_complete_ad_package(config, images)
            
            if package:
                # حفظ في الدفتر
                ledger.add_advertisement(package.asdict())

# جدولة التشغيل الآلي
schedule.every().day.at("08:00").do(run_daily_batch)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**جدولة في Windows Task Scheduler:**
```batch
REM ملف: start_scheduled_system.bat
cd C:\BazarakiSystem
python run_daily_batch.py
```

---

## 📈 مراقبة الأداء

### لوحة تحكم الإحصائيات (stats_dashboard.py):

```python
def generate_daily_report():
    """تقرير يومي عن الأداء"""
    ledger = ServiceLedger()
    
    stats = {
        'total_ads_generated': len(ledger.get_all_advertisements()),
        'total_images_verified': len(ledger.get_all_images()),
        'avg_optimization_score': ledger.get_avg_optimization_score(),
        'top_performing_triggers': ledger.get_top_performing_triggers(),
        'total_inquiries': ledger.get_total_inquiries(),
        'conversion_rate': ledger.get_conversion_rate()
    }
    
    # طباعة التقرير
    print(f"""
    ═════════════════════════════════════════════
    تقرير اليوم - {datetime.now().strftime('%Y-%m-%d')}
    ═════════════════════════════════════════════
    
    إعلانات تم إنشاؤها: {stats['total_ads_generated']}
    صور تم التحقق منها: {stats['total_images_verified']}
    متوسط درجة التحسين: {stats['avg_optimization_score']:.1f}%
    إجمالي الاستفسارات: {stats['total_inquiries']}
    معدل التحويل: {stats['conversion_rate']:.1f}%
    
    أفضل الحفزات النفسية:
    """)
    
    for trigger in stats['top_performing_triggers']:
        print(f"  • {trigger['trigger']}: {trigger['effectiveness']:.1f}% فعالية")
```

---

## ✅ قائمة التحقق قبل الإطلاق

- [ ] تم تثبيت Python 3.10+
- [ ] تم تثبيت المتطلبات (requirements.txt)
- [ ] تم نسخ جميع ملفات .py الـ 5
- [ ] تم إنشاء مجلد data/ مع config.json
- [ ] تم إنشاء مستودع GitHub
- [ ] تم إضافة .gitignore
- [ ] تم اختبار تشغيل النظام يدويًا
- [ ] تم جدولة المهمة اليومية
- [ ] تم التحقق من السجلات (logs)

---

## 🆘 استكشاف الأخطاء

### مشكلة: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### مشكلة: الصور لم تتحقق
```bash
# تأكد من أن الصور في المسار الصحيح
# واختبر بصور عالية الجودة (1024x768+)
```

### مشكلة: قاعدة البيانات مغلقة
```bash
# أغلق جميع نسخ النظام
# احذف ملف .db المغلق
# أعد التشغيل
```

---

**النظام جاهز للنشر الكامل! 🚀**

آخر تحديث: 2026-10-01
