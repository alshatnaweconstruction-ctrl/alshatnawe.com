"""STEP 12: end-to-end sandbox tests (written before the implementation).
Full path: dashboard queue -> apply in sandbox -> ad engine -> XML preview -> production validator.
Nothing outside the sandbox folder may change."""
import hashlib
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from bazaraki_agent import sandbox as sbx
from bazaraki_agent.validate import REPO

WS = REPO.parent
PROTECTED = [REPO / "bazaraki_agent/catalog.json", REPO / "bazaraki_agent/data/rates.json", REPO / "photos/manifest.csv",
             REPO / "bazaraki.xml", REPO / "bazaraki_agent/data/published_ids.json",
             WS / "master_plan/photo_system/photo_manifest_v3.csv", WS / "master_plan/catalog_system/catalog_proposed.json",
             WS / "master_plan/registry/services_registry.json", WS / "master_plan/xml_preview/proposed_bazaraki.xml",
             WS / "master_plan/dashboard/data/dashboard.db"]


def md5s():
    return [hashlib.md5(p.read_bytes()).hexdigest() if p.is_file() else None for p in PROTECTED]


class Base(unittest.TestCase):
    def setUp(self):
        self.before = md5s()
        self.tmp = tempfile.TemporaryDirectory()
        self.sb = sbx.Sandbox.create(Path(self.tmp.name) / "run")

    def tearDown(self):
        self.assertEqual(self.before, md5s(), "a production file changed during the sandbox test")
        self.tmp.cleanup()

    def approve(self, service, n=5, status="proposed"):
        files = self.sb.files(service, status)[:n]
        self.sb.queue_via_dashboard("photo", files, "approve")
        return files, self.sb.apply_queue(by="Leo (sandbox)", date="2026-10-03")


class FullPathTest(Base):
    def test_five_approvals_make_tiling_ready_and_valid_xml(self):
        files, applied = self.approve("tiling")
        self.assertEqual(len(applied["applied"]), 5)
        self.sb.mark_quality_passed("tiling")
        r = self.sb.run_pipeline()
        self.assertEqual(r["ad_status"]["tiling"], "ready_to_publish")
        root = ET.fromstring(r["xml"])
        items = root.findall("list-item")
        self.assertEqual([i.findtext("external_id") for i in items], ["AS-TILING"])
        self.assertEqual(len(items[0].find("images")), 5)
        self.assertEqual(r["validate_errors"], [], r["validate_errors"])     # production validator on the staged copy
        self.assertEqual(r["diff"]["added"], ["AS-TILING"])
        self.assertEqual(len(r["diff"]["removed"]), 386)
        self.assertTrue(r["live_xml_unchanged"])
        self.assertEqual(r["audit_events"].get("queue_add"), 5)
        self.assertEqual(r["audit_events"].get("queue_applied_sandbox"), 5)
        self.assertTrue(any(self.sb.backup_dir.glob("dashboard-*.db")))


class RefusedCasesTest(Base):
    def test_five_approvals_without_quality_gate_stay_out_of_xml(self):
        self.approve("tiling")
        r = self.sb.run_pipeline()
        self.assertNotEqual(r["ad_status"]["tiling"], "ready_to_publish")
        self.assertEqual(ET.fromstring(r["xml"]).findall("list-item"), [])

    def test_four_photos_do_not_make_ready(self):
        self.approve("tiling", n=4)
        r = self.sb.run_pipeline()
        self.assertNotEqual(r["ad_status"]["tiling"], "ready_to_publish")
        self.assertEqual(ET.fromstring(r["xml"]).findall("list-item"), [])

    def test_on_hold_and_candidate_photos_never_enter_xml(self):
        self.approve("tiling")
        r = self.sb.run_pipeline()
        excluded = self.sb.files("tiling", "on_hold") + self.sb.files("tiling", "candidate")
        self.assertTrue(excluded)
        for f in excluded:
            self.assertNotIn(Path(f).name, r["xml"])

    def test_unverified_licence_is_not_approved(self):
        f = self.sb.files("tiling", "proposed")[0]
        self.sb.set_photo(f, licence_verified="no")
        self.sb.queue_via_dashboard("photo", [f], "approve")
        res = self.sb.apply_queue(by="Leo (sandbox)", date="2026-10-03")
        self.assertEqual(res["applied"], [])
        self.assertTrue(any("licence" in e for e in res["refused"][f]))

    def test_service_without_approved_price_not_in_xml(self):
        self.approve("pool-renovation")
        r = self.sb.run_pipeline()
        self.assertTrue(any("price" in x for x in r["excluded"]["pool-renovation"]))
        self.assertNotIn("AS-POOL-RENOVATION", r["xml"])

    def test_compliance_blocked_service_not_in_xml(self):
        self.approve("electrical")
        r = self.sb.run_pipeline()
        self.assertTrue(any("compliance" in x for x in r["excluded"]["electrical"]))
        self.assertNotIn("AS-ELECTRICAL", r["xml"])

    def test_live_external_id_cannot_disappear(self):
        self.sb.set_ledger([{"external_id": "AS-OLD-LIVE", "status": "live"}])
        r = self.sb.run_pipeline()
        self.assertTrue(any("AS-OLD-LIVE" in e for e in r["ledger_errors"]))


class RollbackTest(Base):
    def test_backup_change_restore_is_exact(self):
        snap = self.sb.snapshot("before")
        self.approve("tiling")
        self.sb.run_pipeline()
        self.assertNotEqual(self.sb.state_md5(), snap["md5"])
        self.sb.restore("before")
        self.assertEqual(self.sb.state_md5(), snap["md5"])


class SecurityTest(unittest.TestCase):
    def test_dashboard_routes_have_no_publish_apply_or_url_change(self):
        paths = sbx.dashboard_routes()
        self.assertFalse([p for p in paths if any(w in p.lower() for w in ("publish", "apply", "push", "xml-url", "migrate"))], paths)

    def test_sandbox_refuses_paths_outside_its_folder(self):
        with tempfile.TemporaryDirectory() as d:
            sb = sbx.Sandbox.create(Path(d) / "x")
            with self.assertRaises(ValueError):
                sb.assert_inside(REPO / "bazaraki.xml")


if __name__ == "__main__":
    unittest.main()
