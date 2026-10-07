"""STEP 8: advertisement content engine (written before the implementation)."""
import copy
import hashlib
import unittest

from bazaraki_agent.ad_quality_validator import load_gate
from bazaraki_agent import ad_engine as ae
from bazaraki_agent.official import load as load_official
from bazaraki_agent.validate import REPO

OFFICIAL = load_official()

EL = {"intro": "Τοποθέτηση γυψοσανίδας σε οροφές κατοικιών και γραφείων.",
      "includes": ["Μεταλλικός σκελετός", "Γυψοσανίδα και αρμόστοκος", "Κρυφός φωτισμός LED"],
      "notes": ["Η τιμή αφορά τυπική γυψοσανίδα σε μεταλλικό σκελετό."]}
EN = {"intro": "Plasterboard ceilings for homes and offices.",
      "includes": ["Metal frame", "Plasterboard and jointing", "Hidden LED lighting"],
      "notes": ["The price covers standard board on a metal frame."]}
PRICE = {"approval_status": "approved", "price": 20, "display_en": "From €20 per m². Prices exclude VAT.",
         "display_el": "Από €20 ανά μ². Οι τιμές δεν περιλαμβάνουν ΦΠΑ."}


def content(**over):
    c = {"title_en": "Plasterboard suspended ceilings for homes offices and shops",
         "title_el": "Ψευδοροφές γυψοσανίδας για κατοικίες και γραφεία", "el": copy.deepcopy(EL), "en": copy.deepcopy(EN)}
    c.update(over)
    return c


def photos(n=5, status="proposed", source="unsplash"):
    return [{"file": f"downloaded_candidates/svc/{i}.jpg", "service_key": "ceilings", "status": status, "source": source,
             "approved": "yes" if status == "approved" else "no", "checksum_sha256": f"{i:064d}", "phash": f"{i:016x}",
             "source_url": f"https://unsplash.com/photos/{i}"} for i in range(n)]


def build(c=None, price=PRICE, ph=None, key="ceilings"):
    return ae.build_ad(key, c or content(), price, ph if ph is not None else photos())


class TitleTest(unittest.TestCase):
    def errs(self, title):
        return ae.check_ad(build(content(title_en=title)), OFFICIAL)

    def assertErr(self, frag, errs):
        self.assertTrue(any(frag in e for e in errs), f"{frag!r} not in {errs}")

    def test_good_title_passes(self):
        self.assertEqual(ae.check_ad(build(), OFFICIAL), [])

    def test_too_long_and_too_short(self):
        self.assertErr("title length", self.errs("Plasterboard suspended ceilings and partitions for homes offices and shops"))
        self.assertErr("title length", self.errs("Plasterboard ceilings"))

    def test_price_in_title(self):
        self.assertErr("price in title", self.errs("Plasterboard suspended ceilings from 20 EUR per m2 here"))

    def test_stop_words_english_and_greek(self):
        self.assertErr("stop word", self.errs("Plasterboard suspended ceilings best price for homes"))
        self.assertErr("stop word", self.errs("Plasterboard suspended ceilings χαμηλή τιμή for homes"))

    def test_repeated_word_and_city_copy(self):
        self.assertErr("repeated word", self.errs("Plasterboard ceilings and plasterboard walls for homes"))
        self.assertErr("city", self.errs("Plasterboard suspended ceilings for homes in Limassol"))

    def test_disallowed_characters(self):
        self.assertErr("characters", self.errs("Plasterboard suspended ceilings | homes & offices now"))


class DescriptionTest(unittest.TestCase):
    def assertErr(self, frag, errs):
        self.assertTrue(any(frag in e for e in errs), f"{frag!r} not in {errs}")

    def test_greek_first_then_english(self):
        ad = build()
        self.assertTrue(ae.GREEK.match(next(ch for ch in ad["description"] if ch.isalpha())))
        self.assertLess(ad["description"].find("Ψευδοροφές"), ad["description"].find("Plasterboard suspended"))

    def test_unsubstantiated_claim_rejected(self):
        c = content(); c["en"]["includes"][0] = "Guaranteed metal frame"; c["el"]["includes"][0] = "Μεταλλικός σκελετός με εγγύηση"
        self.assertErr("claim", ae.check_ad(build(c), OFFICIAL))
        c2 = content(); c2["en"]["intro"] += " 15 years of experience."; c2["el"]["intro"] += " 15 χρόνια εμπειρίας."
        self.assertErr("claim", ae.check_ad(build(c2), OFFICIAL))

    def test_stock_photos_described_as_company_work_rejected(self):
        c = content(); c["en"]["notes"].append("See our completed projects in the photos.")
        c["el"]["notes"].append("Δείτε τα έργα μας στις φωτογραφίες.")
        self.assertErr("stock", ae.check_ad(build(c), OFFICIAL))

    def test_stock_photos_require_illustrative_note(self):
        ad = build()
        self.assertIn(ae.PHOTO_NOTE_EN, ad["description"])
        self.assertIn(ae.PHOTO_NOTE_EL, ad["description"])

    def test_contacts_and_bazaraki_rejected(self):
        c = content(); c["en"]["notes"].append("Call 99123456 or visit www.x.cy on Bazaraki")
        c["el"]["notes"].append("Καλέστε 99123456")
        errs = ae.check_ad(build(c), OFFICIAL)
        self.assertErr("contact", errs); self.assertErr("Bazaraki", errs)

    def test_internal_cost_or_margin_rejected(self):
        c = content(); c["en"]["notes"].append("Our margin is 25 percent."); c["el"]["notes"].append("Το περιθώριο μας είναι 25 τοις εκατό.")
        self.assertErr("internal", ae.check_ad(build(c), OFFICIAL))

    def test_greek_english_mismatch_rejected(self):
        c = content(); c["en"]["includes"].append("Acoustic insulation")          # extra bullet only in EN
        self.assertErr("parity", ae.check_ad(build(c), OFFICIAL))
        c2 = content(); c2["en"]["notes"][0] = "The price covers 2 layers of board."  # number only in EN
        self.assertErr("parity", ae.check_ad(build(c2), OFFICIAL))

    def test_audience_sentence_rendered_and_parity_checked(self):
        c = content(); c["el"]["audience"] = "Κατάλληλο και για ξενοδοχεία."; c["en"]["audience"] = "Also suitable for hotels."
        ad = build(c)
        self.assertIn("Also suitable for hotels.", ad["description"]); self.assertIn("Κατάλληλο και για ξενοδοχεία.", ad["description"])
        self.assertEqual(ae.check_ad(ad, OFFICIAL), [])
        c2 = content(); c2["en"]["audience"] = "Also suitable for hotels."           # only in English
        self.assertTrue(any("parity" in e and "audience" in e for e in ae.check_ad(build(c2), OFFICIAL)))

    def test_price_only_from_price_meta(self):
        ad = build()
        self.assertIn(PRICE["display_en"], ad["description"]); self.assertIn(PRICE["display_el"], ad["description"])
        c = content(); c["en"]["notes"].append("Only €15 per m2."); c["el"]["notes"].append("Μόνο €15 ανά μ2.")
        self.assertErr("price", ae.check_ad(build(c), OFFICIAL))


class DuplicateTest(unittest.TestCase):
    def test_duplicate_draft_rejected(self):
        a, b = build(key="ceilings"), build(key="partitions")
        errs = ae.duplicate_problems([a, b], live_titles={})
        self.assertTrue(any("partitions" in e and "ceilings" in e for e in errs))

    def test_full_description_similarity_rejected(self):
        c2 = content(title_en="Plasterboard partition walls and linings for apartments")
        c2["en"]["includes"] = ["Studs", "Board", "Tape"]; c2["el"]["includes"] = ["Ορθοστάτες", "Σανίδα", "Ταινία"]
        errs = ae.duplicate_problems([build(key="ceilings"), build(c2, key="partitions")], live_titles={})
        self.assertTrue(any("full" in e for e in errs), errs)

    def test_two_ads_for_same_service_rejected(self):
        errs = ae.duplicate_problems([build(), build()], live_titles={})
        self.assertTrue(any("same service" in e for e in errs))

    def test_similar_live_title_of_other_service_flagged(self):
        live = {"6378437": "Plasterboard suspended ceilings for homes and offices and shops"}
        errs = ae.duplicate_problems([build()], live_titles=live, own_live_ids={"ceilings": []})
        self.assertTrue(any("6378437" in e for e in errs))
        ok = ae.duplicate_problems([build()], live_titles=live, own_live_ids={"ceilings": ["6378437"]})
        self.assertFalse(any("6378437" in e and "reject" in e for e in ok))


class StatusTest(unittest.TestCase):
    def test_fewer_than_five_approved_never_ready_to_publish(self):
        svc = {"ad_status": "prepare_now", "pricing": {"price_status": "approved"}}
        ad = build(ph=photos(5, "proposed"))
        self.assertEqual(ae.ad_status(ad, svc, []), "ready_to_review")
        ad4 = build(ph=photos(4, "approved") + photos(1, "proposed"))
        self.assertNotEqual(ae.ad_status(ad4, svc, []), "ready_to_publish")
        ad5 = build(ph=photos(5, "approved"))
        self.assertEqual(ae.ad_status(ad5, svc, []), "ready_to_publish")

    def test_research_required_stays_draft_and_errors_block(self):
        svc = {"ad_status": "research_required", "pricing": {"price_status": "research_required"}}
        self.assertEqual(ae.ad_status(build(price={"approval_status": "research_required"}), svc, []), "draft")
        svc2 = {"ad_status": "prepare_now", "pricing": {"price_status": "approved"}}
        self.assertEqual(ae.ad_status(build(), svc2, ["some error"]), "blocked")
        self.assertEqual(ae.ad_status(build(ph=photos(3)), svc2, []), "draft")


class HospitalityVariantTest(unittest.TestCase):
    def hosp(self, **over):
        h = {"title_en": "Plasterboard ceilings for hotel lobbies and corridors here",
             "title_el": "Ψευδοροφές γυψοσανίδας για ξενοδοχεία", "el": copy.deepcopy(EL), "en": copy.deepcopy(EN)}
        h.update(over)
        return h

    def test_variant_is_a_separate_draft(self):
        v = ae.build_variant("ceilings", content(), self.hosp(), PRICE, photos(), {"compliance_required": False})
        self.assertEqual(v["status"], "hospitality_variant_draft")
        self.assertTrue(v["variant_of"] == "ceilings" and v["publish"] is False)
        self.assertEqual(v["problems"], [])

    def test_variant_title_must_differ_from_main(self):
        v = ae.build_variant("ceilings", content(), self.hosp(title_en=content()["title_en"]), PRICE, photos(), {})
        self.assertTrue(any("same title as the main ad" in p for p in v["problems"]))

    def test_compliance_required_blocks_variant(self):
        v = ae.build_variant("electrical", content(), self.hosp(), PRICE, photos(), {"compliance_required": True})
        self.assertEqual(v["status"], "blocked_compliance")
        self.assertEqual(v["description"], "")


class RealDataTest(unittest.TestCase):
    def test_engine_runs_on_real_data_and_touches_no_protected_file(self):
        prot = [REPO / "bazaraki_agent/catalog.json", REPO / "bazaraki_agent/data/rates.json", REPO / "photos/manifest.csv",
                REPO / "bazaraki.xml"]
        before = [hashlib.md5(p.read_bytes()).hexdigest() for p in prot]
        result = ae.run(write=False)
        self.assertEqual(len(result["ads"]), 22)
        for ad in result["ads"]:
            if ad["status"] in ("ready_to_review", "ready_to_publish"):
                self.assertEqual(ad["problems"], [], ad["service_key"])
        st = {a["service_key"]: a["status"] for a in result["ads"]}
        gate = load_gate()
        for k, s in st.items():                          # STEP 13.1: no ready status without a passed quality gate
            if not (gate.get(k) or {}).get("passed"):
                self.assertNotIn(s, ("ready_to_review", "ready_to_publish"), k)
        self.assertEqual(st["electrical"], "draft")      # D-038: offered, but no approved price yet
        self.assertEqual(st["light-steel"], "draft")
        el = next(a for a in result["ads"] if a["service_key"] == "electrical")
        self.assertNotRegex(el["description"].lower(), r"licen[cs]|αδει|certif")   # D-025
        self.assertEqual(before, [hashlib.md5(p.read_bytes()).hexdigest() for p in prot])
        vs = result["variants"]
        self.assertEqual(len([v for v in vs if v["status"] == "hospitality_variant_draft"]), 12)
        self.assertTrue(all(v["publish"] is False and v["problems"] == [] for v in vs if v["status"] == "hospitality_variant_draft"))
        mains = {a["title_en"] for a in result["ads"]}
        self.assertFalse(any(v["title_en"] in mains for v in vs if v["title_en"]))


if __name__ == "__main__":
    unittest.main()
