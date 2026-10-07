"""STEP 5: service registry validation (master_plan/registry/services_registry.json)."""
import copy
import unittest

from bazaraki_agent.registry import (claims_for_generation, district_of, load_registry, validate_registry)


def entry(key="svc-a", **over):
    e = {
        "service_key": key,
        "names": {"ar": "خدمة", "el": "Υπηρεσία", "en": "Service"},
        "group": "finishing",
        "bazaraki_category": {"rubric_id": "3027", "candidates": ["3027"], "confidence": "high"},
        "locations": {"xml_district_id": "5713", "coverage_claim_status": "needs_owner_decision",
                      "evidence_districts": ["Paphos"]},
        "target_customers": ["homeowners"],
        "property_types": ["house"],
        "pricing": {"unit": "EUR per m2", "price_status": "approved", "rates_key": key,
                    "approved_price": 20, "vat": "excluded"},
        "images": {"min_required": 5, "approved_count": 0, "on_hold_count": 0, "status": "missing"},
        "evidence_level": "none",
        "claims_allowed": ["Service provided by Al Shatnawe Construction"],
        "claims_prohibited": ["26 years"],
        "ad_status": "prepare_now",
        "publish_priority": "medium",
        "duplicate_risk_group": "3027",
        "live_ads": {"relationship": "none", "ids": []},
        "owner_decisions_required": [],
        "data_sources": [],
        "last_verified": "2026-10-03",
    }
    e.update(over)
    return e


RATES = {"svc-a": {"approved_price": 20, "approved_by": "Leo", "approved_date": "2026-10-03"},
         "svc-b": {"approved_price": 30, "approved_by": "Leo", "approved_date": "2026-10-03"}}


def run(services, rates=RATES, manifest=None, expected_count=None):
    reg = {"schema_version": "1.0", "global_claims_prohibited": ["guarantee", "licensed", r"\b\d+\+? years\b"],
           "services": services}
    return validate_registry(reg, rates=rates, manifest=manifest or {}, expected_count=expected_count)


class RegistryTest(unittest.TestCase):
    def assertError(self, frag, errors):
        self.assertTrue(any(frag in e for e in errors), f"{frag!r} not in {errors}")

    def test_clean_registry_passes(self):
        self.assertEqual(run([entry("svc-a"), entry("svc-b", pricing=dict(entry()["pricing"], rates_key="svc-b",
                                                                        approved_price=30))]), [])

    def test_service_keys_unique(self):
        self.assertError("duplicate service_key", run([entry("svc-a"), entry("svc-a")]))

    def test_expected_service_count(self):
        self.assertError("expected 22 services", run([entry()], expected_count=22))

    def test_category_must_be_official(self):
        bad = entry(bazaraki_category={"rubric_id": "2168", "candidates": ["2168"], "confidence": "high"})
        self.assertError("not an official", run([bad]))

    def test_uncertain_category_needs_owner_decision_and_official_candidates(self):
        e = entry(bazaraki_category={"rubric_id": None, "candidates": ["3024", "314"],
                                     "confidence": "needs_owner_decision"})
        self.assertEqual(run([e]), [])
        e2 = entry(bazaraki_category={"rubric_id": None, "candidates": ["3024"], "confidence": "high"})
        self.assertError("rubric_id missing", run([e2]))

    def test_location_must_be_official(self):
        self.assertError("not an official location", run([entry(locations={"xml_district_id": "269",
                                                                             "coverage_claim_status": "x",
                                                                             "evidence_districts": []})]))

    def test_district_of_known_ids(self):
        self.assertEqual(district_of("5713"), "Paphos")
        self.assertEqual(district_of("5792"), "Limassol")

    def test_approved_price_must_match_rates(self):
        e = entry(pricing=dict(entry()["pricing"], approved_price=25))
        self.assertError("differs from rates.json", run([e]))

    def test_approved_price_needs_rates_key(self):
        e = entry(pricing=dict(entry()["pricing"], rates_key="missing"))
        self.assertError("no approved rate", run([e]))

    def test_research_required_price_has_no_rates_key(self):
        e = entry(pricing={"unit": "project", "price_status": "research_required", "rates_key": None,
                           "approved_price": None, "vat": "excluded"})
        self.assertEqual(run([e]), [])

    def test_publish_needs_five_approved_photos(self):
        e = entry(ad_status="approved_to_publish", images={"min_required": 5, "approved_count": 5,
                                                          "on_hold_count": 0, "status": "ready"})
        errs = run([e], manifest={})
        self.assertError("approved photos", errs)
        man = {f"photos/svc-a/{i}.jpg": {"service_key": "svc-a", "approved": "yes"} for i in range(5)}
        self.assertEqual(run([e], manifest=man), [])

    def test_publish_needs_approved_price(self):
        e = entry(ad_status="approved_to_publish",
                  pricing={"unit": "x", "price_status": "research_required", "rates_key": None,
                           "approved_price": None, "vat": "excluded"},
                  images={"min_required": 5, "approved_count": 5, "on_hold_count": 0, "status": "ready"})
        man = {f"photos/svc-a/{i}.jpg": {"service_key": "svc-a", "approved": "yes"} for i in range(5)}
        self.assertError("price not approved", run([e], manifest=man))

    def test_on_hold_count_matches_manifest(self):
        man = {"x.jpg": {"service_key": "svc-a", "approved": "on_hold"}}
        self.assertError("on_hold_count", run([entry()], manifest=man))

    def test_allowed_claim_may_not_contain_prohibited_term(self):
        e = entry(claims_allowed=["Fully licensed team"])
        self.assertError("prohibited", run([e]))
        e2 = entry(claims_allowed=["Over 26 years of experience"])
        self.assertError("prohibited", run([e2]))

    def test_claims_for_generation_blocks_prohibited(self):
        reg = {"global_claims_prohibited": ["guarantee"], "services": [entry()]}
        self.assertEqual(claims_for_generation(reg, "svc-a"), ["Service provided by Al Shatnawe Construction"])
        bad = copy.deepcopy(reg)
        bad["services"][0]["claims_allowed"].append("5 year guarantee")
        with self.assertRaises(ValueError):
            claims_for_generation(bad, "svc-a")

    def test_live_ad_ids_not_shared_between_services(self):
        a = entry("svc-a", live_ads={"relationship": "update", "ids": ["6378437"]})
        b = entry("svc-b", live_ads={"relationship": "merge", "ids": ["6378437"]},
                  pricing=dict(entry()["pricing"], rates_key="svc-b", approved_price=30))
        self.assertError("live ad 6378437", run([a, b]))

    def test_enum_values_checked(self):
        self.assertError("ad_status", run([entry(ad_status="live")]))
        self.assertError("evidence_level", run([entry(evidence_level="lots")]))


class RealRegistryTest(unittest.TestCase):
    def test_real_registry_is_valid(self):
        reg = load_registry()
        self.assertEqual(validate_registry(reg, expected_count=22), [])


if __name__ == "__main__":
    unittest.main()
