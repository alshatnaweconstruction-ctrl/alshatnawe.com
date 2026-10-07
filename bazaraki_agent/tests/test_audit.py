import tempfile
import unittest
from pathlib import Path

from bazaraki_agent.audit import run

FEED = """<?xml version="1.0" encoding="utf-8"?>
<root>
  <list-item>
    <external_id>T-1</external_id><status>active</status><rubric>1</rubric><district>2</district>
    <title>Plasterboard in Paphos</title>
    <description>Al Shatnawe Construction, 26 years experience. Send an enquiry.</description>
    <price>0.00</price><negotiable_price>1</negotiable_price><chosen_phone>+1</chosen_phone>
    <images><list-item>https://alshatnawe.com/bazaraki/a/01.jpg</list-item></images>
  </list-item>
  <list-item>
    <external_id>T-2</external_id><status>active</status><rubric>1</rubric><district>2</district>
    <title>Ceilings</title><description>Short.</description>
    <price>25</price><chosen_phone>+1</chosen_phone>
    <images>
      <list-item>https://alshatnawe.com/bazaraki/a/01.jpg</list-item>
      <list-item>https://alshatnawe.com/bazaraki/b/missing.jpg</list-item>
    </images>
  </list-item>
</root>
"""


class AuditTest(unittest.TestCase):
    def test_run_detects_reuse_zero_price_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "public/bazaraki/a").mkdir(parents=True)
            (d / "public/bazaraki/a/01.jpg").write_bytes(b"same-bytes")
            feed = d / "feed.xml"
            feed.write_text(FEED, encoding="utf-8")
            s = run(feed, d / "public", d / "out")

            self.assertEqual(s["listings"], 2)
            self.assertEqual(s["priced_zero"], 1)
            self.assertEqual(s["images_missing"], 1)
            self.assertEqual(s["reused_image_files"], 1)
            self.assertEqual(s["covers_reused"], 2)
            self.assertEqual(s["descriptions_with_brand"], 1)
            self.assertTrue((d / "out/listing_inventory.csv").is_file())
            self.assertIn("T-1#01 T-2#01", (d / "out/image_reuse.csv").read_text())


if __name__ == "__main__":
    unittest.main()
