"""Phase A hardening tests (written before the implementation)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from bazaraki_agent.feed import RAW_PREFIX, atomic_write_text, catalog_to_feed, write_feed
from bazaraki_agent.official import load as load_official
from bazaraki_agent.plan import diff_feeds
from bazaraki_agent.tests.test_feed_validate import listing, write_photo
from bazaraki_agent.validate import load_denylist, validate


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.manifest, self.rates = {}, {}
        for n in (1, 2):
            for i in range(1, 6):
                rel = f"photos/svc-{n}/0{i}.jpg"
                self.manifest[rel] = write_photo(self.root, rel, f"svc-{n}", f"photo {n}-{i}")
            self.rates[f"svc-{n}"] = {"approved_price": 120.0, "approved_by": "Leo", "approved_date": "2026-10-02"}
        self.official = load_official()

    def tearDown(self):
        self.tmp.cleanup()

    def run_validate(self, listings, ledger=None, denylist=None):
        return validate(listings, self.root, self.rates, self.manifest, self.official,
                        ledger=ledger if ledger is not None else [], denylist=denylist or {})

    def errors(self, **over):
        return self.run_validate([listing(1, **over)])[0]

    def assertError(self, fragment, errors):
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")


class AtomicWriteTest(unittest.TestCase):
    def test_atomic_write_replaces_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "out.xml"
            p.write_text("old", encoding="utf-8")
            atomic_write_text(p, "new")
            self.assertEqual(p.read_text(encoding="utf-8"), "new")
            self.assertEqual(sorted(x.name for x in Path(d).iterdir()), ["out.xml"])

    def test_write_feed_refuses_malformed_xml_and_keeps_old_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "feed.xml"
            p.write_text("<root></root>\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_feed("<root><broken></root>", p)
            self.assertEqual(p.read_text(encoding="utf-8"), "<root></root>\n")

    def test_write_feed_writes_valid_xml(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "feed.xml"
            xml = catalog_to_feed([listing(1)])
            write_feed(xml, p)
            self.assertEqual(p.read_text(encoding="utf-8"), xml)


class TitleRulesTest(Base):
    def test_doubled_words_blocked(self):
        self.assertError("doubled word", self.errors(title="Plasterboard ceilings in Paphos Paphos"))
        self.assertError("doubled word", self.errors(title="Tiling tiling floors in Cyprus"))
        self.assertEqual(self.errors(title="Plasterboard ceilings in Paphos, Cyprus"), [])

    def test_price_in_title_blocked(self):
        for t in ["Tiling from 20 EUR per m2 Cyprus", "Painting 8 euro Cyprus homes", "Πλακάκια 20 ευρώ Πάφος"]:
            self.assertError("price in title", self.errors(title=t))
        self.assertEqual(self.errors(title="Tiling for 2 bedroom apartments in Cyprus"), [])


class StatusTest(Base):
    def test_active_b2b_not_allowed_for_services(self):
        self.assertError("status 'active_b2b'", self.errors(status="active_b2b"))


class ImageTypeTest(Base):
    def test_extension_must_be_jpg_or_png(self):
        rel = "photos/svc-1/01.webp"
        self.manifest[rel] = write_photo(self.root, rel, "svc-1", "webp")
        imgs = [f"{RAW_PREFIX}{rel}"] + listing(1)["images"][1:]
        self.assertError("JPG or PNG", self.errors(images=imgs))

    def test_file_signature_must_match(self):
        rel = "photos/svc-1/01.jpg"
        (self.root / rel).write_bytes(b"GIF89a fake")
        self.manifest[rel]["checksum_sha256"] = hashlib.sha256(b"GIF89a fake").hexdigest()
        self.assertError("not a real JPG/PNG file", self.errors())


class DenylistTest(Base):
    def test_denylisted_image_is_blocked(self):
        data = (self.root / "photos/svc-1/03.jpg").read_bytes()
        deny = {hashlib.sha256(data).hexdigest(): "pinterest origin"}
        errs = self.run_validate([listing(1)], denylist=deny)[0]
        self.assertError("deny-list (pinterest origin)", errs)

    def test_load_denylist_parses_lines(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "denylist.txt"
            p.write_text("# comment\n" + "a" * 64 + "  ai_render  some/path.png\n\n", encoding="utf-8")
            self.assertEqual(load_denylist(p), {"a" * 64: "ai_render"})


class ManifestV2Test(Base):
    def test_unverified_rights_cannot_go_live(self):
        self.manifest["photos/svc-1/02.jpg"]["rights_status"] = "unverified"
        self.assertError("rights_status 'unverified'", self.errors())

    def test_source_and_rights_must_agree(self):
        self.manifest["photos/svc-1/02.jpg"]["rights_status"] = "licensed"
        self.assertError("does not match source", self.errors())

    def test_required_v2_fields(self):
        row = self.manifest["photos/svc-1/02.jpg"]
        row["relevance_reason"] = ""
        row["capture_date"] = "yesterday"
        errs = self.errors()
        self.assertError("relevance_reason", errs)
        self.assertError("capture_date", errs)

    def test_checksum_must_match_file(self):
        self.manifest["photos/svc-1/02.jpg"]["checksum_sha256"] = "0" * 64
        self.assertError("checksum does not match", self.errors())

    def test_approval_needs_who_and_when(self):
        self.manifest["photos/svc-1/02.jpg"]["approved_by"] = ""
        self.assertError("approved_by", self.errors())

    def test_on_hold_photo_is_an_error_even_in_a_draft(self):
        self.manifest["photos/svc-1/02.jpg"]["approved"] = "on_hold"
        self.assertError("on hold", self.errors(publish=False))

    def test_copy_of_on_hold_photo_is_blocked_by_checksum(self):
        held = dict(self.manifest["photos/svc-1/02.jpg"], file="../photos-inbox/x.jpeg", approved="on_hold")
        self.manifest["../photos-inbox/x.jpeg"] = held
        self.assertError("on hold", self.errors())


class LedgerTest(Base):
    def test_published_id_cannot_disappear(self):
        ledger = [{"external_id": "T-9", "service_key": "svc-9", "status": "live"}]
        errs = self.run_validate([listing(1)], ledger=ledger)[0]
        self.assertError("T-9", errs)
        self.assertError("was published", errs)

    def test_published_id_may_be_archived_or_removed_explicitly(self):
        ledger = [{"external_id": "T-1", "service_key": "svc-1", "status": "live"}]
        self.assertEqual(self.run_validate([listing(1, status="remove", images=[], price="0")], ledger=ledger)[0], [])

    def test_published_id_cannot_become_draft(self):
        ledger = [{"external_id": "T-1", "service_key": "svc-1", "status": "live"}]
        errs = self.run_validate([listing(1, publish=False)], ledger=ledger)[0]
        self.assertError("was published", errs)

    def test_service_key_of_published_id_is_immutable(self):
        ledger = [{"external_id": "T-1", "service_key": "old-key", "status": "live"}]
        errs = self.run_validate([listing(1)], ledger=ledger)[0]
        self.assertError("service_key changed", errs)


class PlanTest(unittest.TestCase):
    def test_diff_reports_added_changed_removed(self):
        live = catalog_to_feed([listing(1), listing(2)])
        new = catalog_to_feed([listing(1, title="Plasterboard ceilings new title Cyprus"), listing(3)])
        d = diff_feeds(live, new)
        self.assertEqual(d["added"], ["T-3"])
        self.assertEqual(d["changed"], ["T-1"])
        self.assertEqual(d["removed"], ["T-2"])
        self.assertEqual(d["unchanged"], [])

    def test_diff_of_identical_feeds_is_empty(self):
        live = catalog_to_feed([listing(1)])
        d = diff_feeds(live, live)
        self.assertEqual((d["added"], d["changed"], d["removed"]), ([], [], []))


class RepoFilesTest(unittest.TestCase):
    REPO = Path(__file__).resolve().parents[2]

    def test_gitignore_excludes_build_and_cache(self):
        text = (self.REPO / ".gitignore").read_text(encoding="utf-8")
        for entry in ("build/", "__pycache__/"):
            self.assertIn(entry, text)

    def test_version_and_changelog_exist(self):
        v = (self.REPO / "bazaraki_agent" / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(v, r"^\d+\.\d+\.\d+$")
        self.assertIn(v, (self.REPO / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_ledger_and_manifest_files_valid(self):
        ledger = json.loads((self.REPO / "bazaraki_agent" / "data" / "published_ids.json").read_text(encoding="utf-8"))
        self.assertIsInstance(ledger, list)
        header = (self.REPO / "photos" / "manifest.csv").read_text(encoding="utf-8").splitlines()[0]
        for col in ("rights_status", "capture_date", "relevance_reason", "checksum_sha256", "approved_by"):
            self.assertIn(col, header)


if __name__ == "__main__":
    unittest.main()
