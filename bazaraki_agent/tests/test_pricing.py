"""STEP 7: pricing approval engine + catalog_proposed.json (written before the implementation)."""
import copy
import hashlib
import unittest

from bazaraki_agent import pricing
from bazaraki_agent.registry import load_registry
from bazaraki_agent.validate import REPO, validate

RATES = {"svc-a": {"unit": "EUR per m2", "basis": "from", "approved_price": 20, "approved_by": "Leo", "approved_date": "2026-10-03",
                   "confidence": "Medium", "vat_included": False,
                   "sources": [{"source": "x.cy", "url": "https://x.cy", "figure": "EUR 18-22"}]}}


def svc(key="svc-a", status="approved", rubric="3027", **over):
    s = {"service_key": key, "names": {"ar": "أ", "el": "Υ", "en": "Plasterboard ceilings in Cyprus"}, "group": "finishing",
         "bazaraki_category": {"rubric_id": rubric, "candidates": [rubric] if rubric else ["3024", "314"],
                               "confidence": "high" if rubric else "needs_owner_decision"},
         "locations": {"xml_district_id": "5713"}, "ad_status": "prepare_now",
         "pricing": {"unit": "EUR per m2", "price_status": status, "rates_key": key if status == "approved" else None,
                     "approved_price": 20 if status == "approved" else None, "vat": "excluded"}}
    s.update(over)
    return s


class PriceViewTest(unittest.TestCase):
    def test_approved_price_comes_from_rates(self):
        v = pricing.price_view(svc(), RATES)
        self.assertEqual((v["price"], v["approval_status"], v["vat"], v["unit"]), (20, "approved", "excluded", "EUR per m2"))
        self.assertEqual(v["approved_by"], "Leo")
        self.assertEqual(v["confidence"], "Medium")
        self.assertTrue(v["sources"])
        self.assertIn("VAT", v["display_en"])
        self.assertIn("ΦΠΑ", v["display_el"])

    def test_no_rate_means_research_required_and_no_price(self):
        v = pricing.price_view(svc("svc-b", status="research_required"), RATES)
        self.assertEqual((v["price"], v["approval_status"]), (None, "research_required"))
        self.assertEqual(v["display_en"], "")

    def test_registry_price_mismatch_is_an_error(self):
        s = svc(); s["pricing"]["approved_price"] = 25
        with self.assertRaises(ValueError):
            pricing.price_view(s, RATES)

    def test_rate_without_approval_is_not_used(self):
        r = copy.deepcopy(RATES); r["svc-a"]["approved_by"] = ""
        s = svc(); s["pricing"]["price_status"] = "research_required"; s["pricing"]["rates_key"] = None
        self.assertEqual(pricing.price_view(s, r)["price"], None)


class ProposedCatalogTest(unittest.TestCase):
    def setUp(self):
        self.catalog = [{"service_key": "svc-a", "publish": False, "external_id": "AS-SVC-A", "rubric": "3027", "district": "5713",
                         "title": "Plasterboard ceilings in Cyprus", "price": "0.00", "coverage": "All districts of Cyprus"}]

    def test_existing_entry_gets_rates_price_and_stays_draft(self):
        out, skipped = pricing.build_catalog_proposed({"services": [svc()]}, RATES, self.catalog)
        e = out[0]
        self.assertEqual((e["price"], e["publish"], e["external_id"]), ("20.00", False, "AS-SVC-A"))
        self.assertEqual(e["price_meta"]["approval_status"], "approved")
        self.assertIn("availability", e["coverage"].lower())

    def test_new_service_without_price_is_draft_with_zero_price(self):
        out, _ = pricing.build_catalog_proposed({"services": [svc(), svc("svc-b", status="research_required", rubric="3024")]},
                                                RATES, self.catalog)
        b = next(e for e in out if e["service_key"] == "svc-b")
        self.assertEqual((b["price"], b["publish"], b["price_meta"]["approval_status"]), ("0.00", False, "research_required"))
        self.assertEqual(b["external_id"], "AS-SVC-B")

    def test_never_publishes(self):
        cat = copy.deepcopy(self.catalog); cat[0]["publish"] = True
        out, _ = pricing.build_catalog_proposed({"services": [svc()]}, RATES, cat)
        self.assertTrue(all(e["publish"] is False for e in out))

    def test_service_with_undecided_category_is_skipped(self):
        out, skipped = pricing.build_catalog_proposed({"services": [svc(), svc("svc-c", status="research_required", rubric=None)]},
                                                      RATES, self.catalog)
        self.assertNotIn("svc-c", [e["service_key"] for e in out])
        self.assertIn("svc-c", skipped)

    def test_input_catalog_not_mutated(self):
        before = copy.deepcopy(self.catalog)
        pricing.build_catalog_proposed({"services": [svc()]}, RATES, self.catalog)
        self.assertEqual(self.catalog, before)


class RateApprovalProposalTest(unittest.TestCase):
    def test_needs_owner_date_and_positive_price(self):
        for kw in ({"price": 30, "by": "", "date": "2026-10-03"}, {"price": 30, "by": "Leo", "date": "3/10"},
                   {"price": 0, "by": "Leo", "date": "2026-10-03"}):
            with self.assertRaises(ValueError):
                pricing.propose_rate_approval({}, "svc-x", unit="EUR per m", **kw)

    def test_returns_new_dict_without_touching_input(self):
        rates = copy.deepcopy(RATES)
        new = pricing.propose_rate_approval(rates, "svc-x", price=30, unit="EUR per m", by="Leo", date="2026-10-04")
        self.assertNotIn("svc-x", rates)
        self.assertEqual((new["svc-x"]["approved_price"], new["svc-x"]["approved_by"]), (30, "Leo"))
        self.assertEqual(new["svc-a"], RATES["svc-a"])


class RealDataTest(unittest.TestCase):
    def test_real_catalog_proposed_validates_and_leaves_catalog_untouched(self):
        cat_path = REPO / "bazaraki_agent/catalog.json"
        md5 = hashlib.md5(cat_path.read_bytes()).hexdigest()
        out, skipped = pricing.build_catalog_proposed(load_registry(), pricing.load_rates(), pricing.load_catalog())
        errors, _ = validate(out)
        self.assertEqual(errors, [])
        self.assertEqual(hashlib.md5(cat_path.read_bytes()).hexdigest(), md5)
        self.assertEqual(len(out) + len(skipped), 22)
        self.assertTrue(all(e["publish"] is False for e in out))


if __name__ == "__main__":
    unittest.main()
