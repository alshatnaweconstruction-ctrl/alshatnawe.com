import datetime as dt
import tempfile
import unittest
from pathlib import Path

from bazaraki_agent import rejection_advisor as R


def inv(*ads):
    return {"captured_at": dt.datetime(2026, 10, 7, 12, 0),
            "ads": [dict(zip(("id", "state", "category", "title", "price", "created", "views", "phone_clicks", "images", "city"),
                             a)) for a in ads]}


CATALOG = [{"service_key": "ceilings", "publish": True}, {"service_key": "painting", "publish": False},
           {"service_key": "new-build", "publish": False}, {"service_key": "structural", "publish": False}]


class AdviceTest(unittest.TestCase):
    def test_declined_duplicate_of_an_active_service_is_kept_as_history(self):
        rows = R.advise(inv((1, "A", "Plasterboard", "Suspended ceilings with LED coves", "€20", "2026-10", 0, 0, 5, "Paphos"),
                            (2, "D", "Plasterboard", "Gypsum ceiling installation in paphos", "€1", "2026-10", 0, 0, 1, "Paphos")),
                        CATALOG)
        self.assertEqual([(r["id"], r["action"]) for r in rows], [(2, "KEEP_ACTIVE")])
        self.assertIn("#1", rows[0]["why"])

    def test_missing_service_goes_through_the_catalog_pipeline(self):
        rows = R.advise(inv((3, "D", "Painters", "Interior and exterior painting", "€1", "2026-10", 0, 0, 1, "Paphos")), CATALOG)
        self.assertEqual(rows[0]["action"], "FROM_CATALOG")
        self.assertIn("painting", rows[0]["why"])

    def test_service_family_mapping_is_used_for_grouped_services(self):
        rows = R.advise(inv((4, "D", "Builders", "Full project contractor", "€1", "2026-03", 0, 0, 1, "Paphos")), CATALOG)
        self.assertEqual(rows[0]["action"], "FROM_CATALOG")
        self.assertIn("new-build", rows[0]["why"])

    def test_unknown_or_uncatalogued_service_is_left_to_the_owner(self):
        rows = R.advise(inv((5, "D", "Builders", "Transform your property with precision.", "€1", "2026-03", 0, 0, 1, "Paphos"),
                            (6, "D", "Electricians", "Electrical rewiring of villas", "€1", "2026-03", 0, 0, 1, "Paphos")), CATALOG)
        self.assertEqual({r["action"] for r in rows}, {"OWNER_DECIDES"})

    def test_advice_never_proposes_rewording_or_reposting(self):
        rows = R.advise(inv((2, "D", "Plasterboard", "Gypsum ceiling installation in paphos", "€1", "2026-10", 0, 0, 1, "Paphos")),
                        CATALOG)
        self.assertTrue(all(r["action"] in R.ACTIONS for r in rows))
        for word in ("reword", "repost", "resubmit", "new title", "retry"):
            self.assertNotIn(word, " ".join(r["why"] for r in rows).lower())

    def test_report_lists_every_declined_ad(self):
        i = inv((1, "A", "Painters", "Painting", "€9", "2026-10", 0, 0, 5, "Paphos"),
                (2, "D", "Painters", "House painting | interior", "€1", "2026-10", 0, 0, 1, "Paphos"))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            R.write_report(R.advise(i, CATALOG), i, p)
            text = p.read_text(encoding="utf-8")
        self.assertIn("| 2 | House painting / interior |", text)
        self.assertIn("| KEEP_ACTIVE | 1 |", text)


if __name__ == "__main__":
    unittest.main()
