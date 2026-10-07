"""STEP 13.1: Advanced Ad Standard (owner's "Master Prompt v2" rules), as data.

Sources, in order of authority:
1. Owner instructions of 2026-10-03 (STEP 13.1 message, "MASTER PROMPT v2" rules). No file named
   "Master Prompt v2" exists on disk; the rules are taken from the owner's message.
2. Official Bazaraki XML guide (title text and digits, max 70, stop words, no price in title).
3. "Advanced Bazaraki Cyprus Service Ad Generator (Very Advanced Version)" prompt (Downloads/bazaraki)
   and prompts/MASTER_PROMPT_v3_corrected.md.
4. Salvaged from the failed v5 system (BazarakiSystem/, bazaraki-v4.0): extra banned words and
   openings only. Its texts, prices and image checks are NOT reused (fabricated or stubbed).

All patterns are matched against accent-folded, lower-cased text (validate.fold).
"""

from __future__ import annotations

# ---------------------------------------------------------------- identity (hard block, D-057)
COMPANY_IDENTITY = [
    r"al\s*-?\s*shatnawe", r"shatnawe", r"σατναου", r"σατνάου", r"verteks", r"βερτεκς",
    r"\b(?:he|ηε)\s*-?\s*\d{5,6}\b", r"\b495105\b", r"\b443151\b",
    r"\bs\.?\s?a\.?\s+construction\b", r"\bltd\b", r"\bλτδ\b", r"\blimited\b",
    r"registration (?:no|number)", r"\breg\.? ?no\b", r"company number", r"αριθμος εγγραφης", r"αρ\.? εγγραφης",
    r"agapinoros", r"αγαπηνορος", r"\boffice (?:in|at)\b", r"\bour office\b", r"\bγραφειο\b",
    r"p\.?o\.? box", r"\bτ\.?θ\.?\s*\d", r"\b\d{1,3}[a-z]?\s*(?:street|str\.|avenue|ave\.)", r"\b(?:οδος|λεωφορος|λεωφ\.)\s",
    r"alshatnawe\.com", r"\bbrand\b",
]
CONTACT = [
    r"https?://", r"\bwww\.", r"\S+@\S+\.\w+", r"\b[\w-]+\.(?:com|cy|net|org|eu)\b",
    r"whats\s?app", r"viber", r"telegram", r"facebook", r"\bfb\.com", r"instagram", r"tiktok", r"linkedin", r"youtube",
    r"(?:\+?357[\s-]?)?\b(?:9\d|2\d)\s?\d{2}\s?\d{2}\s?\d{2}\b", r"\bcall (?:us|me|now)\b", r"\bτηλεφων",
]

# ---------------------------------------------------------------- generic / AI wording
BANNED_PHRASES = [
    # owner list
    r"\bwe offer\b", r"\bour team provides\b", r"\bour team\b", r"\bwe are proud\b", r"\blooking for\b",
    r"\bpremium solutions?\b", r"\btailored services?\b", r"\bcutting[- ]edge\b", r"\bbest[- ]in[- ]class\b",
    r"\bsatisfaction guaranteed\b", r"\baffordable\b", r"\bnumber one\b", r"\bquality workmanship\b",
    r"\ball types of (?:work|works|jobs)\b",
    # salvaged from v5 lists + common AI filler
    r"\bwe provide\b", r"\bour experts?\b", r"\bleading\b", r"\bpremium\b", r"\btop[- ]notch\b", r"\btop quality\b",
    r"\bstate[- ]of[- ]the[- ]art\b", r"\bsecond to none\b", r"\blook no further\b", r"\bone[- ]stop\b",
    r"\bunparalleled\b", r"\bunmatched\b", r"\bseamless(?:ly)?\b", r"\belevate\b", r"\btrusted partner\b",
    r"\bdream (?:home|house)\b", r"\bhigh[- ]quality\b", r"\bexceptional\b", r"\bwelcome\b", r"\b100\s?%",
    r"\bnever fails\b", r"\bspecial offer\b", r"\blimited time\b", r"\bdiscount\b",
    # Greek equivalents
    r"προσφερουμε", r"η ομαδα μας", r"ειμαστε (?:περηφανοι|υπερηφανοι)", r"ψαχνετε", r"κορυφαι", r"εξατομικευμεν",
    r"προσιτες τιμες", r"οικονομικες τιμες", r"νουμερο ενα", r"ποιοτικη (?:δουλεια|εργασια|κατασκευη)",
    r"ολων των ειδων", r"αριστη ποιοτητα", r"υψηλης ποιοτητας", r"καλως ηρθατε", r"ονειρεμεν", r"αξεπεραστ",
    r"εκπτωσ", r"προσφορα περιορισμεν",
]
BANNED_OPENINGS = [r"^we\b", r"^our\b", r"^welcome\b", r"^looking\b", r"^εμεις\b", r"^η εταιρεια\b", r"^καλως"]

# ---------------------------------------------------------------- claims that need evidence (none on file)
UNSUPPORTED_CLAIMS = [
    r"\b\d+\+?\s*(?:years?|yrs)\b", r"\byears of experience\b", r"\bexperienced\b", r"\bexperience\b",
    r"\b\d+\+?\s*(?:projects?|jobs|homes|villas|clients|customers)\b", r"\bprojects? completed\b", r"\bcompleted projects\b",
    r"\blicen[cs]ed?\b", r"\blicen[cs]e\b", r"\binsured\b", r"\binsurance\b", r"\bwarrant(?:y|ies|ed)\b",
    r"\bguarantee[ds]?\b", r"\bcertifi(?:ed|cate|cation)s?\b", r"\biso\s?\d", r"\baccredited\b", r"\bapproved by\b",
    r"\btestimonials?\b", r"\breviews?\b", r"\bsatisfied (?:clients|customers)\b", r"\bclients say\b", r"\brecommended by\b",
    r"\b24/7\b", r"\bavailable (?:now|today|immediately|any ?time)\b", r"\bsame[- ]day\b", r"\bimmediate start\b",
    r"\bwithin \d+\s*(?:hours?|days?|weeks?)\b", r"\bin \d+\s*(?:hours?|days?|weeks?)\b", r"\bon time\b", r"\bon budget\b",
    r"\bfixed[- ]price\b", r"\bprogress reports?\b", r"\bfast\b", r"\bquick(?:ly)?\b", r"\breliable\b", r"\btrusted\b",
    r"\bbest\b", r"\bcheapest\b", r"\b#1\b", r"\bfree\b", r"\bspecialists?\b", r"\bexperts?\b", r"\bprofessionals?\b",
    r"εμπειρια", r"\b\d+\+?\s*χρονια", r"\bετων\b", r"\b\d+\+?\s*(?:εργα|εργων|εργασιες|πελατες)", r"ολοκληρωμενα εργα",
    r"αδειουχ", r"αδεια ασκησης", r"ασφαλισμεν", r"ασφαλιση", r"εγγυηση", r"εγγυημεν", r"πιστοποι", r"διαπιστευ",
    r"ικανοποιημενοι πελατες", r"κριτικες", r"αμεσα διαθεσιμ", r"αμεση εναρξη", r"εντος \d+", r"σε \d+\s*(?:ημερες|μερες|ωρες|εβδομαδες)",
    r"σταθερη τιμη", r"αναφορες προοδου", r"γρηγορ", r"αξιοπιστ", r"δωρεαν", r"φθηνοτερ", r"ειδικοι\b", r"εξειδικευμεν",
    r"επαγγελματιες", r"\b(?:ο|η|οι|το|τον|την|τα|τους|τις)\s+καλυτερ",
]

# Approved coverage wording only (owner decision, STEP 6 "D5": all Cyprus with caveat). Anything else = claim.
APPROVED_COVERAGE = {
    "el": "Εξυπηρετούμε όλη την Κύπρο. Η διαθεσιμότητα της υπηρεσίας επιβεβαιώνεται ανάλογα με την τοποθεσία του ακινήτου και τις απαιτήσεις του έργου.",
    "en": "We serve all of Cyprus. Service availability is confirmed depending on the property location and project requirements.",
}
# Fixed, approved lines that are allowed to repeat between ads (excluded from template similarity).
PHOTO_NOTE = {"el": "Οι φωτογραφίες είναι ενδεικτικές και δείχνουν παραδείγματα αυτού του είδους εργασιών.",
              "en": "The photos are illustrative examples of this type of work."}
# Disclosure for AI illustrative images (owner wording, D-083). Required in both languages whenever an ad uses one.
AI_NOTE = {"el": "Ορισμένες φωτογραφίες είναι υπολογιστικές απεικονίσεις αυτού του τύπου εργασιών.",
           "en": "Some photos are computer-generated illustrations of this type of work."}
FEE_ENQUIRY = {"el": "Η αμοιβή για την υπηρεσία δίνεται αφού εξετάσουμε τις απαιτήσεις σας.",      # owner wording, D-063
               "en": "Service fee is provided after reviewing your requirements."}
STOCK_AS_OWN = [r"\bour (?:completed )?(?:work|works|projects?|jobs?)\b", r"\bcompleted by us\b", r"\bwe (?:completed|built|did) (?:this|these)\b",
                r"\bphotos? of our\b", r"τα\s+εργα\s+μας", r"η\s+δουλεια\s+μας", r"(?:εργα|εργασιες)\s+που\s+(?:ολοκληρωσαμε|κανα?με)"]
INTERNAL_WORDS = [r"\bmargin\b", r"\bmark-?up\b", r"\bcost price\b", r"\binternal cost\b", r"\bformula\b", r"περιθωρι",
                  r"κοστος\s+αγορας", r"εσωτερικο\s+κοστος"]

# ---------------------------------------------------------------- PASTOR (owner definition, STEP 13.1)
# P problem · A answer (what it solves) · S scope (exact) · T trust (verified only, optional) ·
# O owner/customer type · R reach (coverage, only if confirmed, optional) · then process, fee, CTA.
PASTOR_REQUIRED = ("problem", "solution", "scope", "customers", "process", "cta")
PASTOR_OPTIONAL = ("trust", "coverage", "limits")   # limits = scope exclusions / conditions
MIN_SCOPE_ITEMS = 3
TRUST_EVIDENCE_REQUIRED = True        # any "trust" text needs a matching registry claim id

# ---------------------------------------------------------------- titles
TITLE_MIN, TITLE_MAX = 55, 70
TITLE_WORDS_MIN, TITLE_WORDS_MAX = 5, 15
TITLE_CHARS = set(" ,.-'")
TITLE_HYPE = [r"\bbest\b", r"\bpremium\b", r"\bluxury\b", r"\btop\b", r"\bperfect\b", r"\bamazing\b", r"\bultimate\b",
              r"\bcheap\b", r"\baffordable\b", r"\bleading\b", r"\bexpert\b", r"\bprofessional\b", r"\bguarantee",
              r"\btoday\b", r"\bnow\b", r"κορυφαι", r"πολυτελ", r"τελει", r"φθην", r"καλυτερ", r"επαγγελματικ"]
# Main keyword per service (folded stems; one must appear in each title).
SERVICE_KEYWORDS = {
    "new-build": (["villa", "house", "home", "construction"], ["κατοικ", "βιλ", "κατασκευ", "σπιτ"]),
    "extensions": (["extension", "annex"], ["επεκτασ", "προσθηκ"]),
    "structural": (["concrete", "frame", "formwork", "rebar"], ["σκυροδεμ", "φερων", "καλουπ", "οπλισμ"]),
    "full-renovation": (["renovation"], ["ανακαινισ"]),
    "bathroom": (["bathroom"], ["μπανι"]),
    "kitchen": (["kitchen"], ["κουζιν"]),
    "ceilings": (["ceiling"], ["ψευδοροφ", "οροφ"]),
    "partitions": (["partition", "plasterboard", "drywall"], ["χωρισμ", "γυψοσανιδ"]),
    "painting": (["painting", "paint"], ["βαψιμ", "ελαιοχρωματισμ", "χρωματισμ"]),
    "tiling": (["tiling", "tile"], ["πλακ"]),
    "waterproofing": (["waterproofing"], ["στεγανοποιησ", "στεγανωσ"]),
    "remote-owner": (["property care", "inspection", "property"], ["ακινητ", "επιθεωρησ"]),
    "repairs": (["repair", "maintenance"], ["επισκευ", "συντηρησ"]),
    "pool-care": (["pool"], ["πισιν"]),
    "pool-renovation": (["pool"], ["πισιν"]),
    "concrete-repairs": (["concrete", "spalling"], ["σκυροδεμ", "μπετ"]),
    "retaining-walls": (["retaining wall"], ["αντιστηριξ"]),
    "damp-repairs": (["damp", "mould", "water damage"], ["υγρασι", "μουχλ"]),
    "etics": (["insulation", "etics"], ["θερμομονωσ", "etics"]),
    "joinery": (["joinery", "wardrobe", "cabinet"], ["ξυλουργ", "ντουλαπ"]),
    "electrical": (["electrical"], ["ηλεκτρολογ"]),
    "light-steel": (["steel"], ["μεταλλικ", "χαλυβ"]),
}

# ---------------------------------------------------------------- price
VAT_WORDS = {"en": r"\bvat\b", "el": r"φπα"}
UNIT_WORDS = {"en": r"per (?:m²|m2|sq|square|metre|meter|m\b|linear|hour|visit|month|bathroom|kitchen|project|room|point|item|unit)",
              "el": r"ανα (?:μ²|μ2|τ\.?μ|τετραγωνικ|μετρο|τρεχον|ωρα|επισκεψ|μηνα|μπανιο|κουζινα|εργο|δωματιο|σημειο|τεμαχιο)"}
FROM_WORDS = {"en": r"\bfrom\b", "el": r"\bαπο\b"}
PRICE_EVIDENCE_STATUSES = {"approved"}             # rates.json, owner-approved
RESEARCH_EVIDENCE_STATUS = "researched"            # needs citations: [{url, date, value}]

# ---------------------------------------------------------------- uniqueness
MAX_TEMPLATE_SIMILARITY = 0.40        # full description shingles, fixed lines removed
MAX_PROBLEM_SIMILARITY = 0.40         # word Jaccard of the problem sentence
OPENING_WORDS = 5                     # identical first N words of the problem = cloned opening

# ---------------------------------------------------------------- images
MIN_APPROVED_IMAGES = 5
APPROVE_SCORE = 85
RUBRIC_MAX = {"service": 35, "title": 20, "stage": 15, "plausibility": 10, "visual": 10, "licence": 10}
MIN_TITLE_SCORE = 15                  # below = image does not show what the title says
MIN_SERVICE_SCORE = 28                # below = service mismatch (automatic rejection)
ALLOWED_SOURCES = {"own", "pexels", "unsplash", "ai_illustrative"}
# AI illustrative images (D-083): declared source, approved generator, prompt + owner authorisation on record.
AI_SOURCE = "ai_illustrative"
AI_GENERATORS = {"nano-banana-pro", "meta-ai"}   # meta-ai: D-100, while Gemini is blocked on the Workspace account
AI_AUTHORISATION = "D-083"
LICENCE_EVIDENCE = {"pexels": "https://www.pexels.com/license/", "unsplash": "https://unsplash.com/license"}
FORBIDDEN_DOMAINS = ["pinterest", "pinimg", "google", "gstatic", "bazaraki", "facebook", "fbcdn", "instagram", "cdninstagram",
                     "shutterstock", "istockphoto", "gettyimages", "adobe.stock", "123rf", "dreamstime", "alamy", "depositphotos"]
PHASH_NEAR = 10
IMAGE_RECORD_FIELDS = ("image_id", "source_url", "licence", "download_date", "checksum_sha256", "phash", "service_key",
                       "variant_key", "intended_title", "role", "scores")
ROLES = ("cover", "scope", "detail", "material", "finished-result")

# What an image may depict per service (tags used in visual reviews). Anything else = Q-IMG-MATCH.
GENERIC_TAGS = {"finished_villa", "house_exterior", "generic_interior", "tools_flatlay", "house_model", "keys_door",
                "texture_only", "measuring", "industrial_frame", "stock_concept"}
SERVICE_SUBJECTS = {
    "new-build": {"villa_shell_rc", "house_under_construction", "villa_finished"},
    "extensions": {"extension_blockwork", "extension_finished", "extension_under_construction"},
    "structural": {"rebar_fixing", "formwork", "rc_frame", "concrete_pour", "rc_wall"},
    "full-renovation": {"strip_out", "demolition_interior", "bare_rooms", "renovated_interior"},
    "bathroom": {"bathroom_strip_out", "bathroom_rough_in", "bathroom_tiling_in_progress", "bathroom_finished"},
    "kitchen": {"kitchen_strip_out", "kitchen_install", "kitchen_finished"},
    "ceilings": {"ceiling_board_install", "ceiling_frame", "suspended_ceiling_led", "suspended_ceiling_finished"},
    "partitions": {"metal_stud_frame", "plasterboard_cutting", "plasterboard_install", "partition_finished"},
    "painting": {"interior_painting", "exterior_painting", "paint_roller_wall"},
    "tiling": {"tiling_in_progress", "tiled_floor_finished", "tiled_wall_finished", "tile_cutting"},
    "waterproofing": {"cementitious_coating_application", "roof_membrane_application", "balcony_waterproofing",
                      "roof_waterproofed_finished"},
    "remote-owner": {"property_inspection", "property_checklist", "maintenance_visit"},
    "repairs": {"small_repair", "door_window_adjustment", "wall_patching", "sealant_application"},
    "pool-care": {"pool_cleaning", "pool_robot_cleaner", "pool_water_testing", "pool_clean_finished"},
    "pool-renovation": {"pool_empty_before", "pool_resurfacing", "pool_mosaic_tiling", "pool_under_construction",
                        "pool_renovated_finished"},
    "concrete-repairs": {"spalling_exposed_rebar", "concrete_patch_repair", "balcony_edge_spalling", "rebar_treatment"},
    "retaining-walls": {"rc_retaining_wall", "blockwork_retaining_wall", "retaining_wall_construction"},
    "damp-repairs": {"damp_plaster_removal", "damp_treatment_application", "replastering", "damp_wall_before"},
    "etics": {"etics_boards_install", "etics_mesh_render", "etics_finished_facade"},
    "joinery": {"built_in_wardrobe", "tv_wall_unit", "cabinet_install", "joinery_workshop"},
    "electrical": {"electrical_wiring", "distribution_board", "socket_installation", "lighting_installation"},
    "light-steel": {"light_steel_frame", "carport_steel", "rooftop_room_steel"},
}
COVER_FORBIDDEN = {"finished_villa", "house_exterior", "generic_interior", "stock_concept", "texture_only"}
ILLUSTRATIVE_ONLY_TAGS = {"bathroom_finished"}     # allowed only for bathroom renovation, as illustrative
# Owner-chosen covers (D-124): this image may be the cover even if another image scores higher.
OWNER_COVER = {"bathroom": "bathroom_cover_v2.webp"}
