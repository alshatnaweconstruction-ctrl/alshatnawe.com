"""STEP 10: XML build, validation, preview and diff (written before the implementation)."""
import copy
import hashlib
import unittest
import xml.etree.ElementTree as ET

from bazaraki_agent import xml_preview as xp
from bazaraki_agent.validate import REPO


def entry(key="tiling", **over):
    e = {"service_key": key, "publish": False, "last_update": "2026-10-03 12:00:00", "external_id": f"AS-{key.upper()}",
         "status": "active", "rubric": "3031", "district": "5713", "title": "", "description": "", "price": "22.00",
         "negotiable_price": "1", "exchange": "0", "phone_hide": "0", "chosen_phone": "+35795553931", "whatsapp": "+35795553931",
         "disallow_chat": "0", "images": [], "attrs": {"language": "10,20"}, "geometry": "",
         "price_meta": {"approval_status": "approved", "price": 22}}
    e.update(over)
    return e


def ad(key="tiling", status="ready_to_publish", **over):
    a = {"service_key": key, "status": status, "quality_passed": True, "title_en": "Floor and wall tiling for homes, bathrooms and terraces",
         "description": "Τοποθέτηση πλακιδίων & αρμόστοκος <ok>\n\nENGLISH\n\nTiling \"quoted\" it's fine", "problems": []}
    a.update(over)
    return a


def photos(key="tiling", n=5, status="approved"):
    return [{"service_key": key, "file": f"downloaded_candidates/{key}/p{i}.jpg", "status": status,
             "approved": "yes" if status == "approved" else "no", "checksum_sha256": f"{i:064d}", "source": "pexels"} for i in range(n)]


def svc(key="tiling", compliance=False):
    return {"service_key": key, "ad_status": "prepare_now", "pricing": {"price_status": "approved"},
            "hospitality": {"compliance_required": compliance}}


def run(entries, ads, ph, services=None, ledger=None, live_xml="<root></root>"):
    services = services or {e["service_key"]: svc(e["service_key"]) for e in entries}
    return xp.build_preview(entries, {a["service_key"]: a for a in ads}, ph, services, ledger or [], live_xml)


class EligibilityTest(unittest.TestCase):
    def test_eligible_entry_goes_into_valid_xml(self):
        r = run([entry()], [ad()], photos())
        self.assertEqual([e["service_key"] for e in r["included"]], ["tiling"])
        root = ET.fromstring(r["xml"])
        item = root.find("list-item")
        self.assertEqual(item.findtext("external_id"), "AS-TILING")
        self.assertEqual(item.find("attrs").findtext("language"), "10,20")
        self.assertEqual(len(item.find("images")), 5)
        self.assertIn("&amp;", r["xml"]); self.assertIn("&quot;", r["xml"]); self.assertIn("&apos;", r["xml"])

    def test_quality_gate_not_passed_blocks_xml(self):
        for q in (False, None):
            r = run([entry()], [ad(quality_passed=q)], photos())
            self.assertEqual(r["included"], [])

    def test_empty_preview_is_valid_xml(self):
        r = run([entry()], [ad(status="draft")], photos())
        self.assertEqual(r["included"], [])
        self.assertEqual(ET.fromstring(r["xml"]).tag, "root")

    def test_draft_is_excluded(self):
        r = run([entry()], [ad(status="ready_to_review")], photos())
        self.assertIn("tiling", r["excluded"]); self.assertTrue(any("status" in x for x in r["excluded"]["tiling"]))

    def test_candidate_or_on_hold_images_never_used(self):
        ph = photos(n=5) + photos(n=3, status="proposed") + [dict(photos(n=1, status="on_hold")[0], checksum_sha256="f" * 64)]
        r = run([entry()], [ad()], ph)
        imgs = r["included"][0]["images"]
        self.assertEqual(len(imgs), 5)
        self.assertTrue(all("p" in u for u in imgs))
        r2 = run([entry()], [ad()], photos(n=5, status="proposed"))
        self.assertEqual(r2["included"], [])

    def test_fewer_than_five_approved_excluded(self):
        r = run([entry()], [ad()], photos(n=4))
        self.assertTrue(any("approved photos" in x for x in r["excluded"]["tiling"]))

    def test_no_approved_price_excluded(self):
        r = run([entry(price="0.00", price_meta={"approval_status": "research_required", "price": None})], [ad()], photos())
        self.assertTrue(any("price" in x for x in r["excluded"]["tiling"]))

    def test_compliance_required_excluded(self):
        r = run([entry("electrical", rubric="311")], [ad("electrical")], photos("electrical"),
                services={"electrical": svc("electrical", compliance=True)})
        self.assertTrue(any("compliance" in x for x in r["excluded"]["electrical"]))

    def test_problems_exclude(self):
        r = run([entry()], [ad(problems=["x"])], photos())
        self.assertIn("tiling", r["excluded"])


class LedgerAndDiffTest(unittest.TestCase):
    def test_live_external_id_cannot_disappear(self):
        led = [{"external_id": "AS-OLD", "status": "live"}]
        r = run([entry()], [ad(status="draft")], photos(), ledger=led)
        self.assertTrue(any("AS-OLD" in e for e in r["errors"]))

    def test_explicit_archive_keeps_ledger_id(self):
        led = [{"external_id": "AS-OLD", "status": "live"}]
        old = entry("old", external_id="AS-OLD", status="archive")
        r = run([entry(), old], [ad(status="draft"), ad("old", status="draft")], photos(), ledger=led,
                services={"tiling": svc(), "old": svc("old")})
        self.assertFalse(any("AS-OLD" in e for e in r["errors"]))
        self.assertIn("AS-OLD", r["xml"])

    def test_diff_against_live_lists_deletions(self):
        live = '<root><list-item><external_id>LEO-1</external_id><title>Old</title></list-item></root>'
        r = run([entry()], [ad()], photos(), live_xml=live)
        self.assertEqual(r["diff"]["removed"], ["LEO-1"])
        self.assertEqual(r["diff"]["added"], ["AS-TILING"])


class RealDataTest(unittest.TestCase):
    def test_real_preview_writes_only_preview_folder(self):
        prot = [REPO / "bazaraki_agent/catalog.json", REPO / "bazaraki_agent/data/rates.json", REPO / "photos/manifest.csv",
                REPO / "bazaraki.xml"]
        before = [hashlib.md5(p.read_bytes()).hexdigest() for p in prot]
        r = xp.run(write=False)
        self.assertEqual(r["included"], [])                  # no photos approved yet -> nothing eligible
        self.assertEqual(ET.fromstring(r["xml"]).tag, "root")
        self.assertEqual(len(r["diff"]["removed"]), 386)
        self.assertEqual(before, [hashlib.md5(p.read_bytes()).hexdigest() for p in prot])


if __name__ == "__main__":
    unittest.main()


class AdditiveMergeTest(unittest.TestCase):
    """D-072: the first publish is additive only (+new, -0): existing feed items are carried over unchanged."""
    LIVE = ("<root><list-item><external_id>LEO-SV-001</external_id><status>active</status><title>Old one</title></list-item>"
            "<list-item><external_id>LEO-PB-002</external_id><status>active</status><title>Old two &amp; more</title></list-item></root>")

    def new_xml(self):
        return run([entry()], [ad()], photos())["xml"]

    def test_additive_merge_keeps_every_old_item_and_adds_the_new_one(self):
        from bazaraki_agent.xml_preview import additive_merge
        m = additive_merge(self.LIVE, self.new_xml())
        root = ET.fromstring(m["xml"])
        ids = [i.findtext("external_id") for i in root.findall("list-item")]
        self.assertEqual(ids, ["LEO-SV-001", "LEO-PB-002", "AS-TILING"])
        self.assertEqual(m["added"], ["AS-TILING"])
        self.assertEqual(m["removed"], [])
        self.assertEqual(m["kept"], 2)
        old = {i.findtext("external_id"): i.findtext("title") for i in root.findall("list-item")}
        self.assertEqual(old["LEO-PB-002"], "Old two & more")          # content unchanged

    def test_additive_merge_never_removes_even_if_new_feed_is_empty(self):
        from bazaraki_agent.xml_preview import additive_merge
        m = additive_merge(self.LIVE, "<root></root>")
        self.assertEqual(m["removed"], [])
        self.assertEqual(len(ET.fromstring(m["xml"]).findall("list-item")), 2)

    def test_additive_merge_refuses_to_overwrite_an_existing_id(self):
        from bazaraki_agent.xml_preview import additive_merge
        clash = "<root><list-item><external_id>LEO-SV-001</external_id><status>active</status><title>New</title></list-item></root>"
        with self.assertRaises(ValueError):
            additive_merge(self.LIVE, clash)
