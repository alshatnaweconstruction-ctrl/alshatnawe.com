import hashlib
import tempfile
import unittest
from pathlib import Path

from bazaraki_agent.feed import (FEED, FIELDS, LIVE_FEED, RAW_PREFIX, catalog_to_feed, feed_to_catalog,
                                 load_catalog, published)
from bazaraki_agent.official import load as load_official
from bazaraki_agent.validate import validate

GR_EN = ("Τοποθέτηση γυψοσανίδας σε τοίχους και οροφές για κατοικίες στην Κύπρο.\n\n"
         "Plasterboard walls and ceilings for homes across Cyprus, with a written quotation.")
OTHER = ("Ελαιοχρωματισμός εσωτερικών και εξωτερικών χώρων σε βίλες και διαμερίσματα.\n\n"
         "Interior and exterior painting of villas, including surface preparation and two coats.")


JPEG_MAGIC = b"\xff\xd8\xff\xe0"


def write_photo(root: Path, rel: str, service_key: str, payload: str, source: str = "own") -> dict:
    """Create a minimal JPEG-signature file and its manifest v2 row."""
    data = JPEG_MAGIC + payload.encode()
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_bytes(data)
    return {"file": rel, "service_key": service_key, "source": source, "rights_status": "owned",
            "source_url": "", "licence": "", "project_ref": "ASC-12", "capture_date": "2026-08-27",
            "stage": "after", "relevance_reason": "finished work of this service",
            "checksum_sha256": hashlib.sha256(data).hexdigest(), "width": "", "height": "",
            "consent": "not_needed", "approved": "yes", "approved_by": "Leo", "approved_date": "2026-10-03"}


def listing(n: int = 1, **over):
    base = {
        "service_key": f"svc-{n}", "publish": True,
        "last_update": "2026-10-02 12:00:00", "external_id": f"T-{n}", "status": "active",
        "rubric": "3027", "district": "5713", "title": f"Plasterboard ceilings {n} in Cyprus",
        "description": (GR_EN if n == 1 else OTHER) + f" Ref {n}.", "price": "120.00",
        "chosen_phone": "+35795553931", "whatsapp": "+35795553931",
        "images": [f"{RAW_PREFIX}photos/svc-{n}/0{i}.jpg" for i in range(1, 6)],
        "attrs": {"language": "10,20"}, "geometry": "",
    }
    base.update(over)
    return base


class FeedTest(unittest.TestCase):
    def test_catalog_round_trips_through_feed(self):
        # Independent of whether build/ exists: every published catalog field must
        # survive catalog -> XML -> catalog unchanged (internal fields excluded).
        live = published(load_catalog()) + [listing(1), listing(2)]
        xml = catalog_to_feed(live)
        expected = [{k: v for k, v in l.items() if k in FIELDS} for l in live]
        self.assertEqual(feed_to_catalog(xml), expected)

    def test_build_never_targets_the_live_feed(self):
        self.assertNotEqual(FEED.resolve(), LIVE_FEED.resolve())
        self.assertEqual(FEED.parent.name, "build")

    def test_only_published_and_no_internal_fields(self):
        xml = catalog_to_feed(published([listing(1), listing(2, publish=False)]))
        self.assertIn("<external_id>T-1</external_id>", xml)
        self.assertNotIn("T-2", xml)
        for internal in ("service_key", "publish"):
            self.assertNotIn(f"<{internal}", xml)

    def test_escapes_follow_official_spec(self):
        xml = catalog_to_feed([listing(description="Walls & ceilings -> \"done\" it's")])
        self.assertIn("Walls &amp; ceilings -&gt; &quot;done&quot; it&apos;s", xml)
        self.assertEqual(feed_to_catalog(xml)[0]["description"], "Walls & ceilings -> \"done\" it's")


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.manifest = {}
        self.rates = {}
        for n in (1, 2):
            for i in range(1, 6):
                rel = f"photos/svc-{n}/0{i}.jpg"
                self.manifest[rel] = write_photo(self.root, rel, f"svc-{n}", f"photo {n}-{i}")
            self.rates[f"svc-{n}"] = {"approved_price": 120.0, "approved_by": "Leo", "approved_date": "2026-10-02"}
        self.official = load_official()

    def tearDown(self):
        self.tmp.cleanup()

    def run_validate(self, listings):
        return validate(listings, self.root, self.rates, self.manifest, self.official,
                        ledger=[], denylist={})

    def errors(self, **over):
        return self.run_validate([listing(1, **over)])[0]

    def assertError(self, fragment, errors):
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")

    def test_clean_listing_passes(self):
        self.assertEqual(self.run_validate([listing(1), listing(2)]), ([], []))

    # official Bazaraki rules
    def test_official_ids(self):
        self.assertError("not an official Bazaraki category", self.errors(rubric="2168"))
        self.assertError("not an official Bazaraki location", self.errors(district="269"))
        self.assertEqual(self.errors(rubric="3024"), [])

    def test_official_statuses(self):
        self.assertError("status 'inactive'", self.errors(status="inactive"))
        self.assertEqual(self.errors(status="remove", images=[], price="0"), [])

    def test_title_stop_words_and_characters(self):
        for title in ["Urgent plasterboard repairs", "Γυψοσανίδα τιμή Πάφος", "Best price ceilings"]:
            self.assertTrue(any("stop word" in e or "unsubstantiated" in e for e in self.errors(title=title)), title)
        for title in ["Plasterboard – ceilings", "Tiling 20m² floors", "Kitchens & bathrooms"]:
            self.assertError("characters Bazaraki does not allow", self.errors(title=title))
        self.assertError("71 chars", self.errors(title="x" * 71))
        self.assertEqual(self.errors(title="Plasterboard ceilings, partitions - Cyprus"), [])

    # one ad per service
    def test_one_ad_per_service(self):
        errors, _ = self.run_validate([listing(1), listing(2, service_key="svc-1")])
        self.assertError("used by more than one ad", errors)

    def test_near_duplicate_descriptions(self):
        errors, _ = self.run_validate([listing(1), listing(2, description=listing(1)["description"])])
        self.assertError("near-duplicate", errors)

    def test_duplicate_ids_and_titles(self):
        errors, _ = self.run_validate([listing(1), listing(2, external_id="T-1", title=listing(1)["title"])])
        self.assertError("duplicate external_id", errors)
        self.assertError("duplicate title", errors)

    # language and claims
    def test_language_rules(self):
        self.assertError("Arabic", self.errors(description=GR_EN + " خدمات"))
        self.assertError("Greek and English", self.errors(description="Plasterboard only in English."))
        self.assertError("language must be '10,20'", self.errors(attrs={"language": "20"}))

    def test_claims_are_blocked(self):
        for text in ["Best plasterboard", "Η ΚΑΛΥΤΕΡΗ ΔΟΥΛΕΙΑ", "δωρεάν εκτίμηση", "10 year warranty",
                     "15+ years of work", "available 24/7", "licensed and insured"]:
            self.assertError("unsubstantiated", self.errors(description=GR_EN + " " + text))

    def test_comparative_better_is_allowed(self):
        self.assertEqual(self.errors(description=GR_EN + " χρειάζονται καλύτερη ηχομόνωση"), [])

    def test_contact_and_brand_rules(self):
        self.assertTrue(self.errors(description=GR_EN + " call +357 99 123456"))
        self.assertEqual(self.errors(description=GR_EN + " call +357 95 553 931"), [])
        self.assertError("link or email", self.errors(description=GR_EN + " www.example.com"))
        self.assertError("mentions Bazaraki", self.errors(description=GR_EN + " Message us on Bazaraki"))
        self.assertTrue(self.errors(whatsapp="+35799000000"))

    # price
    def test_price_must_be_approved(self):
        self.rates.pop("svc-1")
        self.assertError("price not approved", self.errors())
        self.rates["svc-1"] = {"approved_price": 150.0, "approved_by": "Leo"}
        self.assertError("differs from approved price", self.errors())
        self.assertError("above 0.00", self.errors(price="0.00"))

    def test_draft_problems_are_warnings(self):
        self.rates.pop("svc-1")
        errors, warnings = self.run_validate([listing(1, publish=False, images=[])])
        self.assertEqual(errors, [])
        self.assertTrue(any("draft needs" in w and "photos" in w for w in warnings))
        self.assertTrue(any("draft needs" in w and "price not approved" in w for w in warnings))

    # photos
    def test_photo_rules(self):
        self.assertError("photos < 5", self.errors(images=listing(1)["images"][:4]))
        self.assertError("not hosted in this repo",
                         self.errors(images=["https://pinterest.com/x.jpg"] + listing(1)["images"][1:]))
        rel = "photos/svc-1/01.jpg"
        self.manifest[rel]["source"] = "pinterest"
        self.assertError("source 'pinterest'", self.errors())
        self.manifest[rel].update(source="stock", licence="", source_url="")
        self.assertError("needs licence", self.errors())
        # D-084 / D-111: an AI illustrative image may be the cover; Meta AI is an accepted AI source (D-100)
        for src in ("ai_nano_banana_pro", "ai_meta_ai"):
            self.manifest[rel].update(source=src, rights_status="generated", licence="")
            errs = " | ".join(self.errors())
            self.assertNotIn("cover (first) photo must be a real photo", errs)
            self.assertNotIn(f"source '{src}'", errs)
            self.assertNotIn("does not match source", errs)
        self.manifest[rel].update(source="ai_meta_ai", rights_status="owned")
        self.assertError("does not match source 'ai_meta_ai'", self.errors())
        self.manifest[rel].update(rights_status="generated")
        for i in (2, 3):
            self.manifest[f"photos/svc-1/0{i}.jpg"]["source"] = "ai_nano_banana_pro"
        self.assertError("3 AI photos > 2", self.errors())       # both AI sources count toward the cap

    def test_all_ai_ads_allowed_for_owner_listed_services(self):
        # D-124: bathroom, repairs, remote-owner may use 5 AI photos; other services keep the cap of 2
        for i in range(1, 6):
            self.manifest[f"photos/svc-1/0{i}.jpg"].update(source="ai_meta_ai", rights_status="generated",
                                                           licence="", service_key="bathroom")
        self.assertNotIn("AI photos >", " | ".join(self.errors(service_key="bathroom")))
        for i in range(1, 6):
            self.manifest[f"photos/svc-1/0{i}.jpg"]["service_key"] = "ceilings"
        self.assertError("5 AI photos > 2", self.errors(service_key="ceilings"))

    def test_photo_must_be_recorded_and_approved(self):
        del self.manifest["photos/svc-1/02.jpg"]
        self.assertError("not recorded in photos/manifest.csv", self.errors())
        self.manifest["photos/svc-1/02.jpg"] = {"file": "photos/svc-1/02.jpg", "service_key": "svc-1",
                                                "source": "own", "approved": "no"}
        self.assertError("not approved by the owner", self.errors())

    def test_same_photo_file_in_two_ads(self):
        same = (self.root / "photos/svc-1/01.jpg").read_bytes()
        (self.root / "photos/svc-2/01.jpg").write_bytes(same)  # same bytes as svc-1/01
        self.manifest["photos/svc-2/01.jpg"]["checksum_sha256"] = hashlib.sha256(same).hexdigest()
        errors, _ = self.run_validate([listing(1), listing(2)])
        self.assertError("already used by T-1", errors)


class OfficialListTest(unittest.TestCase):
    def test_parses_known_values(self):
        d = load_official()
        self.assertEqual(d["rubrics"]["2167"], "Services / Property, maintenance / Pools maintenance")
        self.assertEqual(d["rubrics"]["2169"], "Services / Property, maintenance / Gardeners")
        self.assertEqual(d["districts"]["5713"], "Paphos - Kato Paphos")
        self.assertNotIn("2168", d["rubrics"])
        self.assertIn("τιμή", d["stopwords"])


if __name__ == "__main__":
    unittest.main()
