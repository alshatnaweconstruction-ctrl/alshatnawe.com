"""D-062 / D-068: consistency checks for master_plan/services/MASTER_SERVICE_CATALOG.json."""
import json
import unittest

from bazaraki_agent.validate import REPO

CAT = REPO.parent / "master_plan" / "services" / "MASTER_SERVICE_CATALOG.json"
REG = REPO.parent / "master_plan" / "registry" / "services_registry.json"
TYPES = {"B2C_TURNKEY", "B2B_SUBCONTRACT", "B2B_SPECIALIST", "CONSULTING", "MAINTENANCE", "SUPPLY_ONLY", "NOT_SUITABLE_FOR_BAZARAKI"}
BLOCKING = {"licensed_electrician_EMS", "fire_system_certification", "lift_installer_licence", "gas_certification",
            "medical_gas_certification", "f_gas_certification", "registered_architect_ETEK", "registered_engineer_ETEK",
            "private_security_licence_check", "sewerage_works_authorisation"}
SEVEN = {"plumbing", "air-conditioning", "heating", "cleaning", "gardening", "security-systems", "sewage"}


@unittest.skipUnless(CAT.is_file(), "catalog not built")
class ServiceCatalogTest(unittest.TestCase):
    def setUp(self):
        self.cat = json.loads(CAT.read_text(encoding="utf-8"))
        self.reg = {s["service_key"] for s in json.loads(REG.read_text(encoding="utf-8"))["services"]}
        self.core = self.cat["services"]
        self.ext = self.cat["services_extended"]
        self.all = self.core + self.ext

    def test_core_is_the_22_registry_services(self):
        self.assertEqual({s["service_key"] for s in self.core}, self.reg)
        self.assertTrue(all(s["offered"] == "yes" for s in self.core))

    def test_extended_services_are_offered_and_unique(self):
        keys = [s["service_key"] for s in self.all]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(s["offered"] == "yes" for s in self.ext))
        self.assertTrue(SEVEN <= {s["service_key"] for s in self.ext})

    def test_internal_process_is_never_offered(self):
        for c in self.cat["candidates"]:
            self.assertEqual(c["offered"], "no", c["wbs_code"])
            self.assertEqual(c["phase"], "not_assigned")
            self.assertIn(c["status"], {"internal_process", "excluded_owner_decision"})
            self.assertNotIn("campaign_key", c)
        codes = {c["wbs_code"] for c in self.cat["candidates"] if c["status"] == "internal_process"}
        self.assertIn("1.3.1", codes)      # procurement planning
        self.assertIn("1.2.6", codes)      # clash detection / BIM coordination

    def test_structural_design_stays_excluded(self):
        self.assertIn("1.2.3", {c["wbs_code"] for c in self.cat["candidates"] if c["status"] == "excluded_owner_decision"})

    def test_classifications_are_valid(self):
        for s in self.all:
            self.assertIn(s["contract_type"], TYPES)
            self.assertIn(s["price_status"], {"approved", "provisional_approved", "research_required", "enquiry_only"})
            self.assertIn(s["phase"], {1, 2, 3, 4, 5})
            self.assertTrue(s["wbs_codes_l3"], s["service_key"])

    def test_licence_dependent_services_never_reach_phase_one_or_two(self):
        for s in self.all:
            if set(s.get("licence_or_certification_required", [])) & BLOCKING:
                self.assertEqual(s["phase"], 3, s["service_key"])

    def test_phase_one_rule(self):
        for s in self.all:
            if s["phase"] != 1:
                continue
            self.assertIn(s["price_status"], {"approved", "provisional_approved", "enquiry_only"}, s["service_key"])
            self.assertNotIn(s.get("live_ad_relationship", {}).get("relationship"), {"update", "archive"}, s["service_key"])
            self.assertFalse(set(s.get("licence_or_certification_required", [])) & BLOCKING)

    def test_b2b_only_services_are_not_for_bazaraki(self):
        for s in self.ext:
            if s["b2b_only"]:
                self.assertFalse(s["bazaraki_suitable"], s["service_key"])
                self.assertIn(s["phase"], {3, 4}, s["service_key"])

    def test_contractor_gated_services_never_reach_phase_one(self):
        gated = [s for s in self.all if s.get("contractor_gated")]
        self.assertTrue({"new-build", "extensions", "structural", "demolition"} <= {s["service_key"] for s in gated})
        for s in gated:
            self.assertNotEqual(s["phase"], 1, s["service_key"])

    def test_provisional_prices_are_marked(self):
        prov = {s["service_key"] for s in self.all if s["price_status"] == "provisional_approved"}
        self.assertEqual(prov, {"doors-windows", "cleaning"})

    def test_electrical_is_compliance_gated(self):
        el = next(s for s in self.core if s["service_key"] == "electrical")
        self.assertEqual(el["phase"], 3)
        self.assertEqual(el["phase_status"], "compliance_review_required")

    def test_no_city_or_adjective_variants(self):
        bad = {"paphos", "limassol", "larnaca", "nicosia", "tala", "premium", "luxury", "best", "professional", "cheap"}
        for s in self.core:
            for v in s["variants"]:
                self.assertFalse(set(v["name"].lower().split()) & bad, v)
            keys = [v["variant_key"] for v in s["variants"]]
            self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
