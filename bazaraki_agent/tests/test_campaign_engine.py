"""Campaign engine tests (written before the implementation)."""
import copy
import inspect
import unittest

from bazaraki_agent import campaign_engine as ce
from bazaraki_agent.official import load as load_official

OFFICIAL = load_official()
RATES = {"waterproofing": {"approved_price": 45, "approved_by": "Leo", "approved_date": "2026-10-03", "unit": "EUR per m2"}}


def img(i, source="pexels", url=None, sha=None, ph=None):
    return {"file": f"x/{i}.jpg", "source": source, "source_url": url or f"https://www.pexels.com/photo/p-{i}/",
            "licence": source, "checksum_sha256": sha or f"{i:064x}", "phash": ph or f"{(i * 0x9E3779B97F4A7C15) % (1 << 64):016x}"}


def variant(key="wp-roof", base=0, **over):
    v = {"variant_key": key, "campaign_key": "waterproofing", "rubric": "3026",
         "title_en": "Flat roof and terrace waterproofing with reinforced coating",
         "title_el": "Στεγάνωση ταράτσας με οπλισμένη επίστρωση",
         "primary_scope": "flat-roof-membrane", "scope_tags": ["flat roof", "terrace", "cementitious membrane", "mesh", "uv coat"],
         "customer_problem": "roof leaks into rooms below", "customer_segments": ["homeowners"],
         "description_en": "Waterproofing of flat roofs and terraces with a cementitious membrane, mesh and UV top coat.",
         "description_el": "Στεγάνωση ταρατσών με τσιμεντοειδή μεμβράνη, πλέγμα και τελική στρώση UV.",
         "price_status": "approved", "rates_key": "waterproofing", "images": [img(base + i) for i in range(5)], "publish": False}
    v.update(over)
    return v


def other(key="wp-balcony", base=100, **over):
    o = variant(key, base, title_en="Balcony waterproofing under new tiles to stop leaks below",
                title_el="Στεγάνωση μπαλκονιού κάτω από νέα πλακάκια", primary_scope="balcony-under-tile",
                scope_tags=["balcony", "under tile", "liquid membrane", "drainage edge"], customer_problem="balcony leaks onto ceiling below",
                description_en="Balcony waterproofing under new tiles: removal of old tiles, liquid membrane, falls to the drain and new tiling.",
                description_el="Στεγάνωση μπαλκονιού κάτω από νέα πλακάκια: αφαίρεση πλακιδίων, υγρή μεμβράνη, κλίσεις και νέα πλακάκια.",
                price_status="research_required", rates_key=None)
    o.update(over)
    return o


class VariantRulesTest(unittest.TestCase):
    def errs(self, v):
        return ce.check_variant(v, OFFICIAL, RATES)

    def assertErr(self, frag, errs):
        self.assertTrue(any(frag in e for e in errs), f"{frag!r} not in {errs}")

    def test_good_variant_passes(self):
        self.assertEqual(self.errs(variant()), [])

    def test_five_image_rule(self):
        self.assertErr("5 unique images", self.errs(variant(images=[img(i) for i in range(4)])))

    def test_approved_price_rule(self):
        self.assertErr("price", self.errs(variant(rates_key="missing")))
        r = ce.readiness(variant(price_status="research_required", rates_key=None), RATES)
        self.assertEqual(r, "needs_price")

    def test_prohibited_claims(self):
        self.assertErr("claim", self.errs(variant(description_en="Guaranteed waterproofing with 20 years experience.")))
        self.assertErr("claim", self.errs(variant(description_el="Δωρεάν αυτοψία και εγγύηση.")))

    def test_title_rules(self):
        self.assertErr("title", self.errs(variant(title_en="Waterproofing")))                              # too short
        self.assertErr("title", self.errs(variant(title_en="Roof waterproofing from 45 EUR per m2 in Cyprus now")))  # price
        self.assertErr("title", self.errs(variant(title_en="Roof waterproofing roof coating for flat terraces today")))  # repeat
        self.assertErr("title", self.errs(variant(title_en="Roof waterproofing for houses and villas in Limassol")))  # city clone

    def test_forbidden_image_sources(self):
        for bad in ("https://www.pinterest.com/pin/1/", "https://images.google.com/x", "https://www.bazaraki.com/adv/1/",
                    "https://i.pinimg.com/x.jpg"):
            imgs = [img(i) for i in range(4)] + [img(9, source="pexels", url=bad)]
            self.assertErr("forbidden image source", self.errs(variant(images=imgs)))
        imgs = [img(i) for i in range(4)] + [img(9, source="ai_generated")]
        self.assertErr("image source", self.errs(variant(images=imgs)))

    def test_near_duplicate_images_within_one_ad(self):
        imgs = [img(i) for i in range(4)] + [img(7, ph=img(0)["phash"])]
        self.assertErr("near-duplicate image", self.errs(variant(images=imgs)))


class UniquenessTest(unittest.TestCase):
    def test_distinct_variants_pass(self):
        self.assertEqual(ce.uniqueness([variant(), other()]), [])

    def test_duplicate_variant_detected(self):
        errs = ce.uniqueness([variant(), variant("wp-roof-2", base=50)])
        self.assertTrue(any("primary_scope" in e for e in errs))
        self.assertTrue(any("title" in e or "description" in e for e in errs))

    def test_adjective_or_word_order_change_detected(self):
        v2 = variant("wp-roof-b", base=50, primary_scope="flat-roof-membrane-2",
                     title_en="Reinforced coating waterproofing for flat terraces and roofs",
                     scope_tags=["flat roof", "terrace", "cementitious membrane", "mesh", "uv coat"])
        self.assertTrue(ce.uniqueness([variant(), v2]))

    def test_image_reuse_across_ads_detected(self):
        o = other(images=[img(0)] + [img(100 + i) for i in range(4)])
        self.assertTrue(any("image reused" in e for e in ce.uniqueness([variant(), o])))

    def test_near_duplicate_image_across_ads_detected(self):
        o = other(images=[img(200, ph=img(1)["phash"], sha="f" * 64)] + [img(100 + i) for i in range(4)])
        self.assertTrue(any("near-duplicate image" in e for e in ce.uniqueness([variant(), o])))

    def test_same_customer_problem_detected(self):
        o = other(customer_problem="roof leaks into rooms below")
        self.assertTrue(any("customer_problem" in e for e in ce.uniqueness([variant(), o])))


class NoPublishTest(unittest.TestCase):
    def test_engine_has_no_publishing_capability(self):
        src = inspect.getsource(ce).lower()
        for word in ("write_feed", "bazaraki.xml", "git push", "urllib.request", "requests.", "def publish"):
            self.assertNotIn(word, src)

    def test_catalog_variants_are_never_publish_true(self):
        cat = ce.load_catalog()
        self.assertTrue(all(v.get("publish") is False for c in cat["campaigns"] for v in c.get("variants", [])))
        self.assertTrue(all(c.get("approval_status") != "approved_to_publish" for c in cat["campaigns"]))


class RealCatalogTest(unittest.TestCase):
    def test_catalog_has_20_campaigns_with_official_categories(self):
        cat = ce.load_catalog()
        self.assertEqual(len(cat["campaigns"]), 20)
        for c in cat["campaigns"]:
            self.assertTrue(OFFICIAL["rubrics"].get(str(c["rubric"]), "").startswith("Services / Property, maintenance"), c["campaign_key"])

    def test_waterproofing_plan_is_unique_after_merges(self):
        cat = ce.load_catalog()
        wp = next(c for c in cat["campaigns"] if c["campaign_key"] == "waterproofing")
        self.assertEqual(len(wp["candidate_variants"]), 10)
        kept = [v for v in wp["variants"]]
        self.assertGreaterEqual(len(kept), 5)
        self.assertEqual(ce.plan_uniqueness(kept), [])


if __name__ == "__main__":
    unittest.main()
