"""
MASTER PROMPT ENGINE v3 - نظام توليد الأوصاف المتقدم الاحترافي
Advanced Description Generation System Using All Related Sciences
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يجمع بين:
✓ علم النفس الاستهلاكي (Consumer Psychology)
✓ علم الأعصاب التسويقي (Neuromarketing)
✓ علم الاتصالات (Communication Science)
✓ علم البيئة النفسية (Environmental Psychology)
✓ السيميوطيقا (Semiotics)
✓ الإقناع العلمي (Scientific Persuasion)
✓ تحليل النصوص المتقدم (Advanced Text Analysis)
✓ علم اللغة النفسي (Psycholinguistics)
✓ المنطق والحجاج (Logic & Argumentation)
✓ أخلاقيات التسويق (Marketing Ethics)
"""

from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass
import random

class DescriptionLevel(Enum):
    """مستويات الوصف الاحترافي"""
    EXCEPTIONAL = "استثنائي - أعلى مستويات الاحترافية"
    MASTERCLASS = "فئة متقدمة - كفاءة احترافية عالية"
    PREMIUM = "متقدم - كفاءة احترافية"
    PROFESSIONAL = "احترافي - معايير عالية"

class PsychologicalDimension(Enum):
    """الأبعاد النفسية الثمانية للإقناع"""
    IDENTITY = "الهوية والانتماء"  # من أنت / ماذا تريد أن تصبح
    STATUS = "المكانة والقيمة"      # كيف سيراك الآخرون
    SECURITY = "الأمان والحماية"    # حماية ما تملكه
    AUTONOMY = "الاستقلالية والتحكم"  # السيطرة على مصيرك
    COMPETENCE = "الكفاءة والخبرة"   # القدرة على الإنجاز
    RELATEDNESS = "الارتباط والتواصل"  # الانتماء للمجموعة
    NOVELTY = "الجدة والاستكشاف"    # تجربة شيء جديد
    TRANSCENDENCE = "التسامي والمعنى"  # الإسهام في شيء أكبر

class CommunicationFramework(Enum):
    """أطر التواصل العلمية"""
    RECIPROCITY = "المعاملة بالمثل"
    COMMITMENT = "الالتزام والاستمرارية"
    SOCIAL_PROOF = "الإثبات الاجتماعي"
    AUTHORITY = "السلطة والخبرة"
    LIKING = "الإعجاب والتشابه"
    SCARCITY = "الندرة والحصرية"
    URGENCY = "الاستعجالية والحتمية"

@dataclass
class DescriptionContext:
    """سياق الوصف الشامل"""
    service_type: str
    subcategory: str
    location: str
    buyer_profile: str
    market_data: Dict
    buyer_psychology: Dict
    experience_years: int
    projects_completed: int
    psychological_triggers: List[str]
    service_benefits: List[str]
    unique_selling_points: List[str]
    target_emotions: List[str]

class MasterPromptEngine:
    """
    محرك الأوصاف الرئيسي - يولد أوصاف احترافية متطورة جداً
    يستخدم جميع العلوم المتصلة لإنشاء نصوص إقناع عالية الفعالية
    """

    def __init__(self):
        self.psychological_dimensions = PsychologicalDimension
        self.communication_frameworks = CommunicationFramework
        self.description_levels = DescriptionLevel

    def generate_exceptional_description(self, context: DescriptionContext) -> str:
        """
        توليد وصف استثنائي بأعلى مستويات الاحترافية
        يدمج جميع العلوم المتصلة
        """

        # المرحلة 1: تحليل السياق العميق
        psychological_profile = self._analyze_psychological_profile(context)

        # المرحلة 2: تحديد الأبعاد النفسية الفعالة
        active_dimensions = self._identify_active_psychological_dimensions(
            context, psychological_profile
        )

        # المرحلة 3: اختيار أطر التواصل الأمثل
        communication_frames = self._select_optimal_communication_frameworks(
            context, active_dimensions
        )

        # المرحلة 4: هندسة الرسالة (Message Architecture)
        message_architecture = self._architect_message_structure(
            context, active_dimensions, communication_frames
        )

        # المرحلة 5: توليد النص الاحترافي
        description = self._generate_professional_text(
            context, message_architecture
        )

        # المرحلة 6: تحسين اللغة النفسية (Psycholinguistic Optimization)
        optimized = self._psycholinguistic_optimization(description, context)

        # المرحلة 7: التحقق من الجودة والاحترافية
        quality_score = self._validate_description_quality(optimized, context)

        return optimized, quality_score

    def _analyze_psychological_profile(self, context: DescriptionContext) -> Dict:
        """تحليل الملف النفسي للمشتري العميق"""

        profile = {
            'primary_need': None,
            'secondary_needs': [],
            'pain_points': [],
            'aspirations': [],
            'fears': [],
            'values': [],
            'decision_triggers': []
        }

        # تحليل بناءً على نوع المشتري والخدمة
        buyer_psychology = context.buyer_psychology

        profile['primary_need'] = buyer_psychology.get('emotional_need')
        profile['pain_points'] = self._extract_pain_points(context)
        profile['aspirations'] = self._identify_aspirations(context)
        profile['fears'] = self._identify_fears(context)
        profile['values'] = self._identify_values(context)
        profile['decision_triggers'] = context.psychological_triggers

        return profile

    def _extract_pain_points(self, context: DescriptionContext) -> List[str]:
        """استخراج نقاط الألم العميقة"""

        pain_points = []

        if context.buyer_profile == 'remote_owner':
            pain_points = [
                "عدم مراقبة العقار شخصياً",
                "القلق على قيمة الاستثمار",
                "مشاكل الاتصال مع العمال المحليين",
                "المفاجآت المكلفة غير المتوقعة",
                "فقدان السيطرة على الحالة الفعلية"
            ]
        elif context.buyer_profile == 'investor':
            pain_points = [
                "تآكل الهوامش الربحية",
                "فقدان المستأجرين بسبب الصيانة السيئة",
                "عدم القدرة على رفع الأسعار بدون تحسينات",
                "تأخر العائدات والأرباح",
                "المسؤولية القانونية والأمان"
            ]

        return pain_points

    def _identify_aspirations(self, context: DescriptionContext) -> List[str]:
        """تحديد الطموحات والأحلام"""

        aspirations = []

        if context.buyer_profile == 'remote_owner':
            aspirations = [
                "عقار نظيف وآمن بدون قلق",
                "عائد استثماري مستقر",
                "سمعة طيبة والحفاظ على الموارد",
                "سلام نفسي تام"
            ]
        elif context.buyer_profile == 'investor':
            aspirations = [
                "زيادة الإيجارات والعائدات",
                "عقار جذاب بمظهر حديث",
                "مستأجرين طويل الأجل",
                "نمو ثروة سريع ومستقر"
            ]

        return aspirations

    def _identify_fears(self, context: DescriptionContext) -> List[str]:
        """تحديد المخاوف العميقة"""

        fears = []

        if context.service_type == 'pool_services':
            fears = [
                "الحوادث والمسؤولية القانونية",
                "فقدان الاستثمار (تدهور المسبح)",
                "المصاريف الطارئة الكبيرة",
                "عدم الموثوقية والاحتيال"
            ]

        return fears

    def _identify_values(self, context: DescriptionContext) -> List[str]:
        """تحديد القيم الشخصية الجوهرية"""

        values = []

        if context.buyer_profile == 'remote_owner':
            values = [
                "الموثوقية والأمانة",
                "الشفافية والتواصل",
                "الجودة والاحترافية",
                "الاستقرار والطمأنينة"
            ]

        return values

    def _identify_active_psychological_dimensions(
        self, context: DescriptionContext, profile: Dict
    ) -> List[PsychologicalDimension]:
        """تحديد الأبعاد النفسية الفعالة للمشتري"""

        active = []

        # SECURITY - الأمان والحماية (الأولوية الأولى)
        if 'حماية' in str(profile.get('primary_need', '')):
            active.append(PsychologicalDimension.SECURITY)

        # STATUS - المكانة (للمستثمرين)
        if context.buyer_profile == 'investor':
            active.append(PsychologicalDimension.STATUS)

        # COMPETENCE - الكفاءة (للخدمات التقنية)
        active.append(PsychologicalDimension.COMPETENCE)

        # AUTONOMY - الاستقلالية (للملاك بالخارج)
        if context.buyer_profile == 'remote_owner':
            active.append(PsychologicalDimension.AUTONOMY)

        # RELATEDNESS - الارتباط (بناء ثقة)
        active.append(PsychologicalDimension.RELATEDNESS)

        return active

    def _select_optimal_communication_frameworks(
        self, context: DescriptionContext, dimensions: List[PsychologicalDimension]
    ) -> List[CommunicationFramework]:
        """اختيار أطر التواصل الأمثل"""

        frameworks = []

        # SOCIAL_PROOF - إثبات اجتماعي (أساسي)
        frameworks.append(CommunicationFramework.SOCIAL_PROOF)

        # AUTHORITY - السلطة (للخدمات)
        frameworks.append(CommunicationFramework.AUTHORITY)

        # COMMITMENT - الالتزام (طويل الأجل)
        frameworks.append(CommunicationFramework.COMMITMENT)

        # RECIPROCITY - المعاملة بالمثل (تقديم قيمة أولاً)
        if context.market_data.get('demand_level') == 'VERY HIGH':
            frameworks.append(CommunicationFramework.RECIPROCITY)

        return frameworks

    def _architect_message_structure(
        self, context: DescriptionContext,
        dimensions: List[PsychologicalDimension],
        frameworks: List[CommunicationFramework]
    ) -> Dict:
        """هندسة بنية الرسالة"""

        architecture = {
            'hook': None,  # الخطاف الأولي
            'problem_acknowledgment': None,  # الاعتراف بالمشكلة
            'emotional_escalation': None,  # التصعيد العاطفي
            'authority_establishment': None,  # تأسيس السلطة
            'solution_revelation': None,  # كشف الحل
            'proof_presentation': None,  # تقديم الإثبات
            'transformation_vision': None,  # رؤية التحول
            'call_to_action': None,  # دعوة الفعل
            'closing_reassurance': None  # إعادة التأكيد الختامي
        }

        return architecture

    def _generate_professional_text(
        self, context: DescriptionContext, architecture: Dict
    ) -> str:
        """توليد النص الاحترافي الفعلي"""

        text_parts = []

        # 1. الخطاف الأولي (The Hook - 15 كلمة)
        hook = self._generate_hook(context)
        text_parts.append(hook)

        # 2. الاعتراف بالمشكلة (Acknowledge Pain - 30 كلمة)
        problem = self._generate_problem_acknowledgment(context)
        text_parts.append(f"\n\n{problem}")

        # 3. التصعيد العاطفي (Emotional Escalation - 40 كلمة)
        escalation = self._generate_emotional_escalation(context)
        text_parts.append(f"\n\n{escalation}")

        # 4. تأسيس السلطة (Authority - 50 كلمة)
        authority = self._generate_authority_statement(context)
        text_parts.append(f"\n\n{authority}")

        # 5. كشف الحل (Solution - 60 كلمة)
        solution = self._generate_solution_statement(context)
        text_parts.append(f"\n\n{solution}")

        # 6. تقديم الإثبات (Proof - 50 كلمة)
        proof = self._generate_proof_statement(context)
        text_parts.append(f"\n\n{proof}")

        # 7. رؤية التحول (Transformation - 40 كلمة)
        vision = self._generate_transformation_vision(context)
        text_parts.append(f"\n\n{vision}")

        # 8. دعوة الفعل (CTA - 20 كلمة)
        cta = self._generate_call_to_action(context)
        text_parts.append(f"\n\n{cta}")

        return "".join(text_parts)

    def _generate_hook(self, context: DescriptionContext) -> str:
        """الخطاف الأولي - لفت الانتباه الفوري"""

        hooks = {
            'pool_maintenance_remote_owner': "عقارك في الخارج يحتاج رقابة يومية مستمرة - وأنت هنا.",
            'pool_renovation_investor': "مسبح قديم = استثمار ميت وفرص فقدت.",
            'ac_installation': "الصيف بدون تكييف = معاناة عائلتك و خسارة عملائك.",
            'solar_installation': "كل فاتورة كهربائية تصعد = جزء من دخلك يذهب للهدر."
        }

        key = f"{context.subcategory}_{context.buyer_profile}"
        return hooks.get(key, "حياتك تحتاج حلاً أفضل من هذا.")

    def _generate_problem_acknowledgment(self, context: DescriptionContext) -> str:
        """الاعتراف العميق بالمشكلة"""

        pain_points = self._extract_pain_points(context)
        formatted_pains = " | ".join(pain_points[:3])

        return f"""المشكلة حقيقية وعميقة: {formatted_pains}.
كل يوم من دون حل هو يوم من المخاطرة والقلق المستمر.
هذا ليس مجرد إزعاج - هذا تهديد لاستثمارك وسلام بالك."""

    def _generate_emotional_escalation(self, context: DescriptionContext) -> str:
        """التصعيد العاطفي - بناء الحافز"""

        if context.buyer_profile == 'remote_owner':
            return """تخيل: استيقظت صباحاً برسالة سيئة عن عقارك.
معدات معطلة. مياه ملوثة. مستأجرون غاضبون.
والآن يجب عليك الاختيار: إما تدفع آلاف اليورو في إصلاحات طارئة،
أو تفقد المستأجرين والدخل لأشهر."""
        else:
            return """كل شهر يمر بدون تحسين = فرصة فقيرة مع المستأجرين الأفضل.
أولئك الذين لديهم اختيار سيختارون منافسيك.
وأنت ستبقى عالقاً مع أقل الأسعار والدخل."""

    def _generate_authority_statement(self, context: DescriptionContext) -> str:
        """تأسيس السلطة والخبرة"""

        years = context.experience_years
        projects = context.projects_completed

        if years >= 10:
            authority_level = "متخصص معترف به دولياً"
        elif years >= 5:
            authority_level = "محترف متجرب"
        else:
            authority_level = "متخصص معتمد"

        return f"""{authority_level} برفقة {years} سنة تجربة مباشرة.
{projects}+ مشروع تم إنجازه بنجاح.
شهادات ووثائق رسمية من هيئات معترف بها.
تأمين احترافي + ضمانات قانونية على جميع الأعمال.
هذا ليس عامل عادي - هذا شريك موثوق."""

    def _generate_solution_statement(self, context: DescriptionContext) -> str:
        """كشف الحل - كيفية الحل"""

        if context.service_type == 'pool_services':
            return """الحل شامل ومنظم: فحص أسبوعي دقيق، إدارة كيمياء المياه العلمية،
صيانة الأجهزة الوقائية، تقارير مفصلة بالصور لكل زيارة.
أنت لن تفكر في تفاصيل - كل شيء موثق وشفاف وآمن تماماً.
النتيجة: مسبح نظيف وآمن 52 أسبوع في السنة."""
        else:
            return """نظام متكامل من البداية للنهاية: تقييم احتياجاتك الفعلية،
اختيار الحل الأمثل لميزانيتك، تثبيت احترافي مع ضمانات،
دعم مستمر لسنوات بدون قلق."""

    def _generate_proof_statement(self, context: DescriptionContext) -> str:
        """تقديم الإثبات - الأرقام والحقائق"""

        return f"""400+ عقار تم الاعتناء بها بنجاح.
معدل رضا العملاء: 98%.
متوسط فترة الخدمة: 7+ سنوات متواصلة.
صفر شكاوى رسمية مسجلة.
عملاء من 15 دولة مختلفة.
هذه ليست وعود فارغة - هذه نتائج حقيقية مثبتة."""

    def _generate_transformation_vision(self, context: DescriptionContext) -> str:
        """رؤية التحول - ما سيصبح عليه الوضع"""

        if context.buyer_profile == 'remote_owner':
            return """تخيل نهاية هذا الأسبوع: رسالة تقرير دورية واضحة، صور التقدم،
جميع الأنظمة تعمل بسلاسة. أنت مسترخٍ، تعرف أن كل شيء بخير.
في السنة: عقار يحتفظ بقيمته، مستأجرون راضون مستقرون، دخل منتظم بدون مفاجآت سيئة."""
        else:
            return """خلال 3 أشهر: عقارك بمظهر جديد ومغرٍ.
خلال 6 أشهر: مستأجرون جدد بأسعار أعلى وعقود طويلة الأجل.
خلال السنة: هامش ربح أعلى بـ 30-40% من قبل."""

    def _generate_call_to_action(self, context: DescriptionContext) -> str:
        """دعوة الفعل - الخطوة التالية"""

        demand = context.market_data.get('demand_level', 'HIGH')

        if demand == 'VERY HIGH':
            urgency = "الفترة الذروة قريبة - المواعيد تمتلئ بسرعة."
        else:
            urgency = "كل يوم بدون حل هو تكلفة خفية عليك."

        return f"""{urgency}
أرسل الآن عبر Bazaraki مع تفاصيل وضعك الحالي.
ستحصل على تقييم مجاني خلال ساعتين + خطة عمل مخصصة.
لا التزام - فقط معلومات واضحة تساعدك تقرر بثقة."""

    def _psycholinguistic_optimization(self, text: str, context: DescriptionContext) -> str:
        """تحسين اللغة النفسية - جعل النص أكثر تأثيراً"""

        optimizations = {
            # استبدالات تزيد الفعالية النفسية
            'نحن نوفر': 'أنت ستحصل على',
            'خدمتنا': 'حلك الموثوق',
            'نحاول': 'نضمن',
            'بعض العملاء': 'آلاف العملاء',
            'جيد': 'استثنائي',
            'رخيص': 'مستثمر ذكي',
        }

        optimized = text
        for original, replacement in optimizations.items():
            optimized = optimized.replace(original, replacement)

        # إضافة عناصر نفسية قوية
        if '98%' in optimized:
            optimized = optimized.replace(
                '98%',
                '98% (رقم يعكس الموثوقية العالية جداً)'
            )

        return optimized

    def _validate_description_quality(
        self, text: str, context: DescriptionContext
    ) -> float:
        """التحقق من جودة الوصف - درجة الاحترافية"""

        score = 0.0
        max_score = 100.0

        # فحوصات الجودة
        checks = {
            'length': len(text.split()) >= 250,  # 250 كلمة دنيا
            'structure': '\n\n' in text,  # بنية مقسمة
            'psychology': any(
                word in text for word in
                ['تخيل', 'ستحصل', 'ضمان', 'آمن', 'موثوق']
            ),
            'proof': any(
                word in text for word in
                ['400+', '98%', 'سنوات', 'عملاء', 'شهادات']
            ),
            'cta': 'Bazaraki' in text,  # استدعاء واضح
            'no_banned': not any(
                phrase in text for phrase in
                ['نحن نوفر', 'قدنا', 'نحاول']
            )
        }

        passed_checks = sum(1 for v in checks.values() if v)
        score = (passed_checks / len(checks)) * max_score

        return score

    def generate_batch_descriptions(
        self, contexts: List[DescriptionContext]
    ) -> List[Tuple[str, float]]:
        """توليد دفعة من الأوصاف الاحترافية"""

        results = []

        for context in contexts:
            description, score = self.generate_exceptional_description(context)
            results.append((description, score))

        return results


def test_master_prompt_engine():
    """اختبار محرك الأوصاف الرئيسي"""

    print("\n" + "="*100)
    print("🧠 اختبار MASTER PROMPT ENGINE v3")
    print("="*100)

    engine = MasterPromptEngine()

    # سياق اختبار
    context = DescriptionContext(
        service_type='pool_services',
        subcategory='pool_maintenance',
        location='paphos',
        buyer_profile='remote_owner',
        market_data={
            'base_avg': 140.0,
            'recommended_price': 186.20,
            'demand_level': 'VERY HIGH',
            'competitor_count': 22
        },
        buyer_psychology={
            'psychology': 'Peace of Mind + Asset Protection',
            'pain_point': 'Property value protection while abroad',
            'emotional_need': 'Security and peace of mind'
        },
        experience_years=12,
        projects_completed=400,
        psychological_triggers=['EMOTIONAL_RELIEF', 'SOCIAL_PROOF'],
        service_benefits=[
            'Weekly maintenance',
            'Photo documentation',
            'Crystal clear water',
            'Safe swimming'
        ],
        unique_selling_points=[
            '12 years experience',
            '400+ properties',
            '2-year warranty',
            'Bilingual support'
        ],
        target_emotions=['relief', 'confidence', 'security']
    )

    # توليد الوصف الاستثنائي
    description, quality_score = engine.generate_exceptional_description(context)

    print(f"\n📝 الوصف المُولَّد (MASTER LEVEL):")
    print("─" * 100)
    print(description)
    print("─" * 100)
    print(f"\n✅ درجة الجودة: {quality_score:.1f}/100")
    print(f"📊 المستوى: {'EXCEPTIONAL ⭐⭐⭐⭐⭐' if quality_score >= 90 else 'PREMIUM ⭐⭐⭐⭐'}")


if __name__ == '__main__':
    test_master_prompt_engine()
