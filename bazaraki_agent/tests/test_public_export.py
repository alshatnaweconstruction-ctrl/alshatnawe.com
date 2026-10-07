import unittest

from bazaraki_agent import public_export as X
from bazaraki_agent.feed import RAW_PREFIX

RATES = {"tiling": {"unit": "EUR per m2", "approved_price": 22, "approved_by": "Leo",
                    "internal_evidence": "Labour selling EUR 99 (signed, ZZZ-00), cost EUR 77",
                    "sources": [{"source": "Market survey", "url": "https://example.org/tiles"},
                                {"source": "Client working set (internal, Documents\\Quotations)", "url": ""}]},
         "_meta": "owner-approved rates"}
MANIFEST = {"photos/tiling/a.jpg": {"file": "photos/tiling/a.jpg", "service_key": "tiling", "source": "stock", "licence": "pexels",
                                    "source_url": "https://www.pexels.com/photo/1/", "project_ref": "VSC-99",
                                    "relevance_reason": "from C:\\Users\\x\\Organized_Files", "checksum_sha256": "ab", "width": "2400", "height": "1600"},
            "photos/tiling/b.jpg": {"file": "photos/tiling/b.jpg", "service_key": "tiling", "source": "own", "licence": "own",
                                    "source_url": "own://VSC-99 visit/x.jpg", "checksum_sha256": "cd", "width": "1600", "height": "1200"},
            "photos/tiling/c.jpg": {"file": "photos/tiling/c.jpg", "service_key": "tiling", "source": "ai_meta_ai", "licence": "ai_illustrative",
                                    "source_url": "ai://meta-ai/c", "checksum_sha256": "ef", "width": "2048", "height": "1152"}}
FEED = "".join(f"<list-item>{RAW_PREFIX}photos/tiling/{n}.jpg</list-item>" for n in "abc")


class PublicExportTest(unittest.TestCase):
    def test_internal_rate_fields_and_internal_sources_are_dropped(self):
        r = X.public_rates(RATES)
        self.assertNotIn("internal_evidence", r["tiling"])
        self.assertEqual([s["url"] for s in r["tiling"]["sources"]], ["https://example.org/tiles"])
        self.assertEqual(r["tiling"]["approved_price"], 22)
        self.assertEqual(r["_meta"], "owner-approved rates")

    def test_public_manifest_keeps_only_public_columns(self):
        rows = X.public_manifest(MANIFEST, X.feed_photos(FEED))
        self.assertEqual([r["file"] for r in rows], [f"photos/tiling/{n}.jpg" for n in "abc"])
        self.assertTrue(all(set(r) == set(X.PHOTO_FIELDS) for r in rows))
        a, b, c = rows
        self.assertEqual(a["source_url"], "https://www.pexels.com/photo/1/")
        self.assertEqual((b["source_type"], b["licence"], b["source_url"]), ("own photo", "owned", ""))
        self.assertEqual((c["source_type"], c["source_url"]), ("AI illustration (Meta AI)", ""))

    def test_rendered_output_has_no_leaks(self):
        files = X.render(RATES, X.public_manifest(MANIFEST, X.feed_photos(FEED)))
        for name, text in files.items():
            self.assertEqual(X.leaks(text, ["Clientname"]), [], name)

    def test_leak_scanner_catches_project_codes_paths_and_private_terms(self):
        self.assertTrue(X.leaks("see ASC-99"))
        self.assertTrue(X.leaks("C:\\Users\\someone\\x.jpg"))
        self.assertTrue(X.leaks("own://VSC-99/x"))
        self.assertTrue(X.leaks("internal_evidence: ..."))
        self.assertEqual(X.leaks("Clientname roof", ["clientname"]), ["private term #1"])
        self.assertEqual(X.leaks("Plasterboard ceilings, Paphos"), [])

    def test_photo_used_by_the_feed_must_be_recorded(self):
        with self.assertRaises(ValueError):
            X.public_manifest({}, ["photos/tiling/a.jpg"])


if __name__ == "__main__":
    unittest.main()
