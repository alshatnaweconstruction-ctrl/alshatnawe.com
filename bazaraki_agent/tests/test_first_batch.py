"""STEP 13: first publishing batch preparation (written before the implementation)."""
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from bazaraki_agent import first_batch as fb
from bazaraki_agent.validate import REPO

WS = REPO.parent
PROTECTED = [REPO / "bazaraki_agent/catalog.json", REPO / "bazaraki_agent/data/rates.json", REPO / "photos/manifest.csv",
             REPO / "bazaraki.xml", WS / "master_plan/photo_system/photo_manifest_v3.csv",
             WS / "master_plan/catalog_system/catalog_proposed.json", WS / "master_plan/xml_preview/proposed_bazaraki.xml",
             WS / "master_plan/dashboard/data/dashboard.db"]


def md5s():
    return [hashlib.md5(p.read_bytes()).hexdigest() for p in PROTECTED]


def queue_db(path, rows):
    c = sqlite3.connect(path)
    c.execute("create table approval_queue (id integer primary key, ts text, item_type text, item_id text, action text, note text, status text, status_ts text)")
    c.executemany("insert into approval_queue(ts,item_type,item_id,action,note,status,status_ts) values ('t','photo',?,?,'',?,'t')", rows)
    c.commit(); c.close()


class FirstBatchTest(unittest.TestCase):
    def setUp(self):
        self.before = md5s()
        self.tmp = tempfile.TemporaryDirectory(); self.out = Path(self.tmp.name) / "first_batch"

    def tearDown(self):
        self.assertEqual(self.before, md5s(), "a production file changed")
        self.tmp.cleanup()

    def test_three_packages_with_full_content(self):
        r = fb.build(out=self.out)
        self.assertEqual(sorted(r["services"]), ["bathroom", "ceilings", "repairs"])
        for k in ("bathroom", "ceilings", "repairs"):
            t = (self.out / k / "PUBLISH_PACKAGE.md").read_text(encoding="utf-8")
            p = r["services"][k]
            for needle in (p["title_en"], p["title_el"], "10,20", "Prices exclude VAT", "Οι τιμές δεν περιλαμβάνουν ΦΠΑ",
                           p["rubric"], p["district"], "ENGLISH"):
                self.assertIn(needle, t, (k, needle))
            self.assertEqual(len(p["photos"]), 5)
            for ph in p["photos"]:
                if ph["type"] == "ai_illustrative":          # D-083/D-110: AI illustrative images carry ai:// provenance
                    self.assertTrue(ph["source_url"].startswith("ai://")); self.assertEqual(ph["licence"], "ai_illustrative")
                else:
                    self.assertTrue(ph["source_url"].startswith("https://"))
                    self.assertIn(ph["type"], ("stock", "own"))
                    self.assertIn(ph["licence"], ("unsplash", "pexels", "own"))
                self.assertTrue(ph["relevance_reason"])
        self.assertTrue((self.out / "FIRST_BATCH_READINESS.md").is_file())

    def test_nothing_is_publishable_from_this_tool_even_with_owner_approvals(self):
        # D-110 / D-124: the owner approved 5 photos for ceilings, bathroom and repairs on 2026-10-07
        r = fb.build(out=self.out)
        for k, p in r["services"].items():
            self.assertEqual(p["status"], "ready_to_review")          # never publishable from this tool
            self.assertEqual(p["approved_photos"], 5, k)
            self.assertTrue(any("final review" in m.lower() for m in p["missing"]), p["missing"])
            self.assertEqual(p["compliance_problems"], [])
            self.assertEqual(p["duplicate_problems"], [])

    def test_queued_approvals_are_counted_but_not_treated_as_approved(self):
        r0 = fb.build(out=self.out)
        p0 = r0["services"]["repairs"]
        files = [ph["file"] for ph in p0["photos"]]
        db = Path(self.tmp.name) / "q.db"
        queue_db(db, [(f, "approve", "pending") for f in files])
        r = fb.build(out=self.out, queue_db=db)
        p = r["services"]["repairs"]
        self.assertEqual(p["queued_approvals"], len(files) - p0["approved_photos"])   # only photos not yet approved
        self.assertEqual(p["approved_photos"], p0["approved_photos"])               # a pending queue approves nothing
        self.assertNotEqual(p["status"], "ready_to_publish")

    def test_readiness_report_has_order_and_blockers(self):
        fb.build(out=self.out)
        t = (self.out / "FIRST_BATCH_READINESS.md").read_text(encoding="utf-8")
        for needle in ("bathroom", "ceilings", "repairs", "386", "Proposed publishing order", "blocks publishing"):
            self.assertIn(needle, t)

    def test_writes_only_inside_out_dir(self):
        fb.build(out=self.out)
        files = [p for p in self.out.rglob("*") if p.is_file()]
        self.assertEqual(len(files), 4)                     # 3 packages + readiness report
        with self.assertRaises(ValueError):
            fb.build(out=REPO / "bazaraki_agent")             # refuses a production folder


if __name__ == "__main__":
    unittest.main()
