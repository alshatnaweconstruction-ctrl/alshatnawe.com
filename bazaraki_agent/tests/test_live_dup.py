"""Q-LIVE-DUP (D-086): offline duplicate-prevention analyzer. Written before the implementation."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from bazaraki_agent import live_dup as L

NOW = dt.datetime(2026, 10, 6, 15, 0)
SNAPSHOT = Path(__file__).resolve().parents[3] / "master_plan" / "release_gates" / "evidence" / "live_inventory_2026-10-06.psv"


def row(i, state, cat, title, price="€75", city="Paphos"):
    return {"id": i, "state": state, "category": cat, "title": title, "price": price, "city": city}


def inventory(*ads, captured=NOW - dt.timedelta(hours=1)):
    return {"captured_at": captured, "ads": list(ads)}


ACTIVE_PARTITION = row(6200619, "A", "Plasterboard", "Plasterboard partition walls in Paphos")
ACTIVE_POOL = row(6758110, "A", "Pools maintenance", "Pool main drain inspection and debris removal", "€1")


def proposal(**over):
    p = {"service_key": "partitions", "title_en": "Plasterboard partition walls in Paphos",
         "title_el": "Χωρίσματα από γυψοσανίδα στην Πάφο", "rubric": "3027", "district": "5713", "price": 75,
         "images": [{"checksum_sha256": "a" * 64, "phash": "ff00ff00ff00ff00"}, {"checksum_sha256": "b" * 64, "phash": "00ff00ff00ff00ff"}]}
    p.update(over)
    return p


def codes(findings):
    return {f["code"] for f in findings}


class DuplicateDetectionTest(unittest.TestCase):
    def check(self, p, inv=None):
        return L.check_proposal(p, inv or inventory(ACTIVE_PARTITION, ACTIVE_POOL))

    def test_exact_duplicate_blocked(self):
        f = self.check(proposal())
        self.assertIn("Q-LIVE-DUP", codes(f))
        self.assertIn(6200619, {x.get("active_id") for x in f})

    def test_changed_title_still_blocked(self):
        self.assertIn("Q-LIVE-DUP", codes(self.check(proposal(title_en="Licensed drywall room dividers for homes and offices"))))

    def test_changed_location_still_blocked(self):
        self.assertIn("Q-LIVE-DUP", codes(self.check(proposal(title_en="Plasterboard partition walls in Tala - 309", district="5724"))))

    def test_changed_price_still_blocked(self):
        self.assertIn("Q-LIVE-DUP", codes(self.check(proposal(price=1400))))

    def test_changed_category_still_blocked(self):
        self.assertIn("Q-LIVE-DUP", codes(self.check(proposal(rubric="2167"))))

    def test_punctuation_changes_still_blocked(self):
        self.assertIn("Q-LIVE-DUP", codes(self.check(proposal(title_en="Plasterboard, partition-walls!! (Paphos)"))))

    def test_same_images_in_different_order_blocked(self):
        imgs = proposal()["images"]
        inv_ad = dict(row(1, "A", "Painters", "House painting interior and exterior", "€1"), images=imgs)
        p = proposal(service_key="tiling", title_en="Floor and wall tiling for homes", images=list(reversed(imgs)))
        self.assertIn("Q-LIVE-DUP-IMG", codes(self.check(p, inventory(inv_ad))))

    def test_pool_sub_services_count_as_the_same_service(self):
        p = proposal(service_key="pool-care", title_en="Skimmer basket cleaning and lid replacement", rubric="2167")
        self.assertIn("Q-LIVE-DUP", codes(self.check(p)))

    def test_genuinely_different_service_passes(self):
        p = proposal(service_key="ceilings", title_en="Suspended plasterboard ceilings with metal frame for homes",
                     title_el="Ψευδοροφές γυψοσανίδας με μεταλλικό σκελετό")
        self.assertNotIn("Q-LIVE-DUP", codes(self.check(p)))

    def test_related_service_is_a_warning_not_a_block(self):
        inv = inventory(row(6379539, "A", "Tiler", "Large format tile & marble / precision laying cyprus", "€1"))
        p = proposal(service_key="bathroom", title_en="Bathroom renovation with strip out, new tiles and shower", title_el="Ανακαίνιση μπάνιου")
        f = self.check(p, inv)
        self.assertNotIn("Q-LIVE-DUP", codes(f)); self.assertIn("W-LIVE-RELATED", codes(f))

    def test_title_that_reads_as_another_service_is_flagged(self):
        p = proposal(service_key="repairs", title_en="Plasterboard partition walls in Paphos")
        self.assertIn("W-LIVE-TITLE", codes(self.check(p)))

    def test_declined_history_is_a_warning_not_a_block(self):
        inv = inventory(ACTIVE_PARTITION, row(6673711, "D", "Pools maintenance", "Drywall suspended ceiling installation in paphos", "€1.400"))
        f = self.check(proposal(service_key="ceilings", title_en="Suspended plasterboard ceilings with metal frame for homes",
                                title_el="Ψευδοροφές γυψοσανίδας με μεταλλικό σκελετό"), inv)
        self.assertIn("W-LIVE-DECLINED", codes(f)); self.assertNotIn("Q-LIVE-DUP", codes(f))


class FailClosedTest(unittest.TestCase):
    def test_missing_inventory_blocks_everything(self):
        rep = L.check([proposal(service_key="ceilings", title_en="Suspended ceilings for homes")], Path("does/not/exist.psv"), now=NOW)
        self.assertFalse(rep["inventory_ok"])
        self.assertTrue(all("Q-LIVE-DUP-INV" in codes(r["findings"]) for r in rep["results"]))
        self.assertFalse(any(r["allowed"] for r in rep["results"]))

    def test_stale_inventory_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "inv.psv"
            p.write_text("# captured_at: 2026-10-01T10:00\n1|A|Builders|Site preparation|€1|2026-03|1|0|1|Paphos\n", encoding="utf-8")
            with self.assertRaises(L.InventoryError):
                L.load_inventory(p, now=NOW)

    def test_empty_inventory_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "inv.psv"
            p.write_text("# captured_at: 2026-10-06T14:00\n", encoding="utf-8")
            with self.assertRaises(L.InventoryError):
                L.load_inventory(p, now=NOW)


class ExceptionTest(unittest.TestCase):
    def test_owner_exception_allows_with_record(self):
        exc = [{"service_key": "partitions", "active_id": 6200619, "approved_by": "owner", "date": "2026-10-06", "reason": "replace old ad"}]
        f = L.check_proposal(proposal(), inventory(ACTIVE_PARTITION), exceptions=exc)
        self.assertNotIn("Q-LIVE-DUP", codes(f)); self.assertIn("X-OWNER-EXCEPTION", codes(f))

    def test_incomplete_exception_ignored(self):
        exc = [{"service_key": "partitions", "active_id": 6200619, "approved_by": "", "date": "2026-10-06", "reason": ""}]
        self.assertIn("Q-LIVE-DUP", codes(L.check_proposal(proposal(), inventory(ACTIVE_PARTITION), exceptions=exc)))


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.inv = inventory(
            row(6689165, "A", "Renovation", "Certified plasterboard partition tala - 307"),
            row(6379873, "A", "Electricians", "Electrical rewiring cyprus / safe power & smart home", "€1"),
            row(6685265, "A", "Pools maintenance", "Kitchen renovation and fitting service in paphos", "€3.500"),
            row(6379695, "A", "Painters", "House painting cyprus / long-lasting exterior and interior", "€1"),
            row(6688004, "D", "Carpenters", "Licensed plasterboard partition tala - 309"),
            row(6687961, "D", "Carpenters", "Top plasterboard partition tala - 312"))
        self.reg = {r["ad_id"]: r for r in L.registry(self.inv)}

    def test_only_active_ads_in_registry(self):
        self.assertEqual(set(self.reg), {6689165, 6379873, 6685265, 6379695})

    def test_high_risk_claims_flagged(self):
        self.assertEqual(self.reg[6689165]["risk"], "high")
        self.assertIn("certified", self.reg[6689165]["main_claim"])

    def test_licence_gated_service_flagged(self):
        self.assertEqual(self.reg[6379873]["risk"], "high")

    def test_wrong_category_flagged(self):
        self.assertTrue(self.reg[6685265]["wrong_category"])
        self.assertFalse(self.reg[6379695]["wrong_category"])

    def test_active_service_with_multiple_declined_duplicates(self):
        self.assertEqual(self.reg[6689165]["declined_twins"], 2)


class RealSnapshotTest(unittest.TestCase):
    """The captured 2026-10-06 inventory (read-only)."""

    def setUp(self):
        self.inv = L.load_inventory(SNAPSHOT, now=NOW)

    def test_counts(self):
        st = [a["state"] for a in self.inv["ads"]]
        self.assertEqual((len(st), st.count("A"), st.count("D")), (144, 17, 127))

    def test_ceilings_not_blocked_but_warned(self):
        f = L.check_proposal(proposal(service_key="ceilings", title_en="Suspended plasterboard ceilings with metal frame for homes",
                                      title_el="Ψευδοροφές γυψοσανίδας με μεταλλικό σκελετό"), self.inv)
        self.assertNotIn("Q-LIVE-DUP", codes(f)); self.assertIn("W-LIVE-DECLINED", codes(f))

    def test_partitions_blocked_by_live_ads(self):
        f = L.check_proposal(proposal(), self.inv)
        self.assertTrue({6689165, 6200619} <= {x.get("active_id") for x in f if x["code"] == "Q-LIVE-DUP"})


class OfflineOnlyTest(unittest.TestCase):
    def test_module_has_no_network_or_write_endpoints(self):
        src = Path(L.__file__).read_text(encoding="utf-8")
        for bad in ("import urllib", "import requests", "import http", "socket", "to_remove", "/edit/", "deactivate("):
            self.assertNotIn(bad, src)


if __name__ == "__main__":
    unittest.main()
