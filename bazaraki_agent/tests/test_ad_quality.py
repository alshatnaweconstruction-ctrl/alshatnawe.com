"""STEP 13.1: Advanced Ad Standard (Master Prompt v2) tests, written before the implementation."""
import unittest

from bazaraki_agent import ad_quality_validator as q
from bazaraki_agent.official import load as load_official

OFFICIAL = load_official()


def sections():
    return {
        "el": {"problem": "Πλακάκια που ξεκολλούν, ραγίζουν ή έχουν φθαρμένους αρμούς κάνουν το μπάνιο ή τη βεράντα να δείχνουν παραμελημένα και αφήνουν το νερό να περνά.",
               "solution": "Νέο δάπεδο ή τοίχος με πλακάκια, τοποθετημένα σε σωστά προετοιμασμένη επιφάνεια.",
               "scope": ["Προετοιμασία και αλφάδιασμα επιφάνειας", "Κόλλα πλακιδίων", "Τοποθέτηση με συστήματα αλφαδιάσματος",
                         "Αρμόστοκος", "Κοπές γύρω από γωνίες και σωληνώσεις"],
               "customers": "Για ιδιοκτήτες κατοικιών, διαχειριστές ακινήτων και ξενοδοχεία.",
               "coverage": "Εξυπηρετούμε όλη την Κύπρο. Η διαθεσιμότητα της υπηρεσίας επιβεβαιώνεται ανάλογα με την τοποθεσία του ακινήτου και τις απαιτήσεις του έργου.",
               "process": "Στέλνετε φωτογραφίες και διαστάσεις, ακολουθεί αυτοψία και γραπτή προσφορά με το εύρος της εργασίας.",
               "cta": "Γράψτε μας τα τετραγωνικά και το είδος του πλακιδίου για να ετοιμάσουμε την προσφορά."},
        "en": {"problem": "Loose, cracked or badly grouted tiles make a bathroom or terrace look neglected and let water through.",
               "solution": "A new tiled floor or wall laid on a properly prepared, level surface.",
               "scope": ["Surface preparation and levelling", "Tile adhesive", "Laying with levelling clips", "Grouting",
                         "Cuts around corners and pipes"],
               "customers": "For homeowners, property managers and hotels.",
               "coverage": "We serve all of Cyprus. Service availability is confirmed depending on the property location and project requirements.",
               "process": "You send photos and measurements, then a site visit and a written quotation listing the scope follow.",
               "cta": "Message us the area in square metres and the tile type to receive a quotation."}}


PRICE = {"approval_status": "approved", "price": 22, "display_en": "From €22 per m². Prices exclude VAT.",
         "display_el": "Από €22 ανά μ². Οι τιμές δεν περιλαμβάνουν ΦΠΑ."}
FEE_SCOPE = {"en": "laying only; tile adhesive and grout included; tiles supplied by the client",
             "el": "μόνο τοποθέτηση· με κόλλα και αρμόστοκο· τα πλακάκια τα προμηθεύει ο πελάτης"}


def ad(**over):
    a = {"service_key": "tiling", "title_en": "Floor and wall tiling for homes, bathrooms and outdoor terraces",
         "title_el": "Τοποθέτηση πλακιδίων σε δάπεδα, μπάνια, κουζίνες και βεράντες", "price_status": "approved", "price_meta": PRICE,
         "fee_scope": FEE_SCOPE, "sections": sections(), "stock_photos": True}
    a.update(over)
    a["description"] = q.build_description(a)
    return a


def image(i, **over):
    m = {"image_id": f"img{i}", "file": f"x/{i}.jpg", "source": "pexels", "source_url": f"https://www.pexels.com/photo/p-{i}/",
         "licence": "pexels", "licence_verified": "yes", "download_date": "2026-10-03", "checksum_sha256": f"{i:064x}",
         "phash": f"{(i * 0x9E3779B97F4A7C15) % (1 << 64):016x}", "service_key": "tiling", "variant_key": "tiling",
         "intended_title": "Floor and wall tiling for homes, bathrooms and outdoor terraces", "role": "cover" if i == 0 else "scope",
         "depicts": ["tiling_in_progress"], "scores": {"service": 33, "title": 18, "stage": 14, "plausibility": 9, "visual": 10, "licence": 10},
         "watermark": False, "stock": True, "illustrative_only": True, "approved": True}
    m.update(over)
    return m


def five(**over):
    return [image(i, **over) for i in range(5)]


def codes(errs):
    return {e[0] for e in errs}


class TextRulesTest(unittest.TestCase):
    def check(self, a, imgs=None, others=None):
        return codes(q.validate_ad(a, imgs if imgs is not None else five(), others or [], OFFICIAL))

    def test_compliant_bilingual_ad_with_five_matching_images_passes(self):
        self.assertEqual(q.validate_ad(ad(), five(), [], OFFICIAL), [])

    def test_company_name_rejected_in_greek_and_english(self):
        for lang, txt in (("en", "Al Shatnawe Construction carries out the work."), ("el", "Η VERTEKS εκτελεί τις εργασίες.")):
            s = sections(); s[lang]["solution"] += " " + txt
            self.assertIn("Q-COMPANY", self.check(ad(sections=s)))

    def test_legal_entity_registration_and_address_rejected(self):
        for txt in ("Registered as HE 495105.", "VERTEKS S.A. CONSTRUCTION LTD", "Office at Agapinoros 8-6, Paphos."):
            s = sections(); s["en"]["solution"] += " " + txt
            self.assertIn("Q-COMPANY", self.check(ad(sections=s)))

    def test_banned_phrases_rejected(self):
        for txt in ("We offer premium solutions.", "Tailored services with cutting-edge methods.", "Affordable prices."):
            s = sections(); s["en"]["solution"] = txt
            self.assertIn("Q-BANNED", self.check(ad(sections=s)))
        s = sections(); s["el"]["solution"] = "Προσφέρουμε κορυφαίες λύσεις."
        self.assertIn("Q-BANNED", self.check(ad(sections=s)))

    def test_unsupported_claims_rejected(self):
        for txt in ("20 years of experience.", "Over 100 projects completed.", "Full warranty on all work.", "Fully insured team."):
            s = sections(); s["en"]["solution"] += " " + txt
            self.assertIn("Q-CLAIM", self.check(ad(sections=s)))

    def test_missing_pastor_sections_rejected(self):
        for sec in ("problem", "scope", "process", "cta"):
            s = sections(); s["el"][sec] = [] if sec == "scope" else ""
            self.assertIn("Q-PASTOR", self.check(ad(sections=s)))

    def test_template_description_flagged(self):
        other = ad(service_key="painting", title_en="Interior and exterior wall painting for houses and apartments")
        self.assertIn("Q-TEMPLATE", self.check(ad(), others=[other]))

    def test_greek_english_mismatch_flagged(self):
        s = sections(); s["en"]["scope"].append("Waterproofing membrane")
        self.assertIn("Q-PARITY", self.check(ad(sections=s)))
        s2 = sections(); s2["en"]["process"] += " Works start within 3 days."
        self.assertIn("Q-PARITY", self.check(ad(sections=s2)))

    def test_price_without_evidence_blocked(self):
        a = ad(price_status="research_required", price_meta=PRICE)
        self.assertIn("Q-PRICE-EVIDENCE", self.check(a))

    def test_vat_ambiguity_flagged(self):
        pm = dict(PRICE, display_en="From €22 per m².", display_el="Από €22 ανά μ².")
        self.assertIn("Q-VAT", self.check(ad(price_meta=pm)))

    def test_title_length_and_words(self):
        self.assertIn("Q-TITLE", self.check(ad(title_en="Floor and wall tiling in Cyprus homes")))      # < 55
        self.assertIn("Q-TITLE", self.check(ad(title_en="Floor and wall tiling for homes, best price in Cyprus today")))

    def test_contacts_and_social_links_rejected(self):
        s = sections(); s["en"]["cta"] = "Call 99123456 or find us on facebook.com/x"
        self.assertIn("Q-CONTACT", self.check(ad(sections=s)))


class ImageRulesTest(unittest.TestCase):
    def check(self, imgs, a=None):
        return codes(q.validate_ad(a or ad(), imgs, [], OFFICIAL))

    def test_fewer_than_five_approved_blocked(self):
        imgs = five(); imgs[4]["approved"] = False
        self.assertIn("Q-IMG-COUNT", self.check(imgs))

    def test_generic_villa_photo_for_waterproofing_rejected(self):
        wa = ad(service_key="waterproofing", title_en="Flat roof waterproofing with reinforced cementitious coating system")
        imgs = [image(i, service_key="waterproofing", depicts=["roof_membrane_application"]) for i in range(4)]
        imgs.append(image(9, service_key="waterproofing", depicts=["finished_villa"]))
        self.assertIn("Q-IMG-MATCH", self.check(imgs, wa))

    def test_bathroom_image_for_electrical_rejected(self):
        el = ad(service_key="electrical", title_en="Electrical installation and repair works for homes and shops")
        imgs = [image(i, service_key="electrical", depicts=["electrical_wiring"]) for i in range(4)]
        imgs.append(image(9, service_key="electrical", depicts=["bathroom_finished"]))
        self.assertIn("Q-IMG-MATCH", self.check(imgs, el))

    def test_reused_photo_rejected(self):
        imgs = five(); imgs[1]["used_by_other_ad"] = "painting"
        self.assertIn("Q-IMG-REUSED", self.check(imgs))

    def test_near_duplicate_image_rejected(self):
        imgs = five(); imgs[4]["phash"] = imgs[0]["phash"]; imgs[4]["checksum_sha256"] = "f" * 64
        self.assertIn("Q-IMG-NEAR", self.check(imgs))

    def test_forbidden_sources_rejected(self):
        for url in ("https://www.pinterest.com/pin/1/", "https://www.bazaraki.com/adv/1/", "https://images.google.com/x"):
            imgs = five(); imgs[2]["source_url"] = url
            self.assertIn("Q-IMG-SOURCE", self.check(imgs))

    def test_missing_licence_evidence_rejected(self):
        imgs = five(); imgs[3]["licence_verified"] = "no"
        self.assertIn("Q-IMG-LICENCE", self.check(imgs))

    def test_watermarked_image_rejected(self):
        imgs = five(); imgs[2]["watermark"] = True
        self.assertIn("Q-IMG-WATERMARK", self.check(imgs))

    def test_image_title_mismatch_rejected(self):
        imgs = five(); imgs[0]["scores"] = dict(imgs[0]["scores"], title=8)
        self.assertIn("Q-IMG-TITLE", self.check(imgs))

    def test_score_below_85_rejected_and_rubric_total(self):
        self.assertEqual(q.image_score(image(0)), 94)
        imgs = five(); imgs[1]["scores"] = dict(imgs[1]["scores"], service=24, stage=8)
        self.assertIn("Q-IMG-SCORE", self.check(imgs))

    def test_stock_disclosure_required(self):
        s = sections()
        a = ad(sections=s, stock_photos=True)
        a["description"] = a["description"].replace(q.PHOTO_NOTE["en"], "")
        self.assertIn("Q-IMG-STOCK", self.check(five(), a))


def ai_image(i, **over):
    m = image(i, source="ai_illustrative", source_url=f"ai://nano-banana-pro/tiling_{i}", licence="ai_illustrative",
              licence_verified="n/a", ai_generated=True, generator="nano-banana-pro", prompt_ref=f"AI_IMAGE_PLAN #{i + 1}",
              owner_authorisation="D-083", visible_watermark=False)
    m.update(over)
    return m


class AiIllustrativeTest(unittest.TestCase):
    """D-083: AI images allowed as illustrative service visuals only, with disclosure; never as our work."""

    def check(self, imgs, a=None):
        return codes(q.validate_ad(a or ad(ai_images=True), imgs, [], OFFICIAL))

    def test_declared_ai_images_with_disclosure_pass_any_role_including_cover(self):
        self.assertEqual(set(), self.check([ai_image(i) for i in range(5)]))

    def test_mixed_ai_and_stock_pass(self):
        self.assertEqual(set(), self.check([ai_image(0)] + [image(i) for i in range(1, 5)]))

    def test_ai_disclosure_required_in_both_languages(self):
        for lang in ("el", "en"):
            a = ad(ai_images=True)
            a["description"] = a["description"].replace(q.AI_NOTE[lang], "")
            self.assertIn("Q-IMG-AI", self.check([ai_image(i) for i in range(5)], a))

    def test_ai_images_presented_as_our_work_rejected(self):
        s = sections(); s["en"]["cta"] = s["en"]["cta"] + " See photos of our work."
        self.assertIn("Q-IMG-STOCK", self.check([ai_image(i) for i in range(5)], ad(ai_images=True, stock_photos=False, sections=s)))

    def test_weaker_cover_needs_owner_choice(self):
        """D-124: a cover scoring below another image fails unless the owner chose it (OWNER_COVER)."""
        from unittest import mock
        imgs = [ai_image(i) for i in range(5)]
        imgs[1]["scores"] = dict(imgs[1]["scores"], plausibility=10)   # image 1 now outscores the cover
        self.assertIn("Q-IMG-COVER", self.check(imgs))
        with mock.patch.dict(q.P.OWNER_COVER, {"tiling": "img0"}):
            self.assertEqual(set(), self.check(imgs))
        self.assertEqual(q.P.OWNER_COVER.get("bathroom"), "bathroom_cover_v2.webp")

    def test_meta_ai_accepted_as_generator(self):
        """D-100: Meta AI used while Gemini is blocked on the Workspace account."""
        self.assertEqual(set(), self.check([ai_image(i, generator="meta-ai") for i in range(5)]))

    def test_undeclared_ai_image_rejected(self):
        imgs = five(); imgs[2]["ai_generated"] = True
        self.assertIn("Q-IMG-SOURCE", self.check(imgs, ad()))

    def test_ai_provenance_required(self):
        for field, bad in (("generator", "midjourney"), ("prompt_ref", ""), ("owner_authorisation", "")):
            imgs = [ai_image(i) for i in range(5)]; imgs[1][field] = bad
            self.assertIn("Q-IMG-AI", self.check(imgs))

    def test_ai_visible_watermark_rejected(self):
        imgs = [ai_image(i) for i in range(5)]; imgs[3]["visible_watermark"] = True
        self.assertIn("Q-IMG-WATERMARK", self.check(imgs))

    def test_ai_image_still_needs_score_85(self):
        imgs = [ai_image(i) for i in range(5)]; imgs[1]["scores"] = dict(imgs[1]["scores"], stage=4, visual=3)
        self.assertIn("Q-IMG-SCORE", self.check(imgs))

    def test_ai_note_added_by_builder_only_when_ai_images(self):
        d = ad(ai_images=True)["description"]
        self.assertIn(q.AI_NOTE["el"], d); self.assertIn(q.AI_NOTE["en"], d)
        self.assertNotIn(q.AI_NOTE["en"], ad()["description"])


class ManifestRowTest(unittest.TestCase):
    """D-110: manifest rows keep a stable score_key (the external rename broke the join by file name) and carry AI provenance."""

    def row(self, **over):
        r = {"file": "downloaded_candidates/ceilings/ceiling_work_0009.jpg", "source": "unsplash", "source_url": "https://unsplash.com/photos/x",
             "licence": "unsplash", "licence_verified": "yes", "rights_status": "licensed", "download_date": "2026-10-03",
             "checksum_sha256": "a" * 64, "phash": "ff00ff00ff00ff00", "service_key": "ceilings", "width": "2400", "height": "1600",
             "status": "approved", "approved": "yes", "logos_or_trademarks": "", "score_key": "unsplash_89RsOg-hWyM.jpg"}
        r.update(over)
        return r

    SCORES = {"unsplash_89RsOg-hWyM.jpg": {"scores": {"service": 33}, "depicts": ["suspended_ceiling_led"], "role": "finished-result", "note": ""}}

    def test_scores_found_by_score_key_after_rename(self):
        img = q._image_from_row(self.row(), self.SCORES, "T")
        self.assertEqual(img["role"], "finished-result"); self.assertEqual(img["image_id"], "unsplash_89RsOg-hWyM.jpg")

    def test_falls_back_to_file_name_without_score_key(self):
        img = q._image_from_row(self.row(score_key="", file="x/unsplash_89RsOg-hWyM.jpg"), self.SCORES, "T")
        self.assertEqual(img["role"], "finished-result")

    def test_ai_row_carries_provenance(self):
        img = q._image_from_row(self.row(source="ai_illustrative", generator="meta-ai", prompt_ref="AI_IMAGE_PLAN #1 v2",
                                         owner_authorisation="D-083", visible_watermark="no"), self.SCORES, "T")
        self.assertTrue(img["ai_generated"]); self.assertEqual(img["generator"], "meta-ai")
        self.assertEqual(img["owner_authorisation"], "D-083"); self.assertFalse(img["visible_watermark"])

    def test_stock_row_is_not_ai(self):
        self.assertFalse(q._image_from_row(self.row(), self.SCORES, "T").get("ai_generated"))


class GateTest(unittest.TestCase):
    def test_gate_caps_ready_status_when_quality_fails(self):
        self.assertEqual(q.gate_status("ready_to_review", [("Q-TITLE", "x")]), "draft")
        self.assertEqual(q.gate_status("ready_to_publish", [("Q-IMG-COUNT", "x")]), "draft")
        self.assertEqual(q.gate_status("ready_to_review", []), "ready_to_review")
        self.assertFalse(q.passed({}, "tiling"))
        self.assertTrue(q.passed({"tiling": {"passed": True}}, "tiling"))


class LegacyAuditTest(unittest.TestCase):
    def test_legacy_description_with_company_line_fails(self):
        legacy = "Τίτλος\n\nκείμενο\n\nAl Shatnawe Construction – VERTEKS S.A. CONSTRUCTION LTD (HE 495105), γραφείο στην Πάφο.\n\nENGLISH\n\nText"
        self.assertIn("Q-COMPANY", {c for c, _ in q.audit_text(legacy)})


if __name__ == "__main__":
    unittest.main()
