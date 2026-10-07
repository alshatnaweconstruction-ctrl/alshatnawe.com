"""STEP 12: end-to-end sandbox. Copies every input into a sandbox folder and runs the full path:

    dashboard approval queue -> apply approvals (sandbox copy only) -> ad engine -> XML preview
    -> production validator (validate.py) on a staged copy of the approved photos.

Every write goes inside the sandbox folder (`assert_inside`). Production files, the live XML,
the real dashboard DB and the XML URL are never touched. No network, no publishing.

    python -m bazaraki_agent.sandbox e2e [--service tiling]      # full scenario + report
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

from bazaraki_agent import ad_engine, xml_preview
from bazaraki_agent.feed import LIVE_FEED, RAW_PREFIX, write_feed
from bazaraki_agent.validate import REPO, load_denylist, validate

WS = REPO.parent
MP = WS / "master_plan"
PHOTO_ROOT = MP / "photo_system"
DASH = MP / "dashboard"
for p in (PHOTO_ROOT, DASH):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import photo_pipeline as pp  # noqa: E402

INPUTS = {  # sandbox name: real source (copied once, read-only)
    "catalog_proposed.json": MP / "catalog_system/catalog_proposed.json",
    "photo_manifest_v3.csv": PHOTO_ROOT / "photo_manifest_v3.csv",
    "rates.json": REPO / "bazaraki_agent/data/rates.json",
    "services_registry.json": MP / "registry/services_registry.json",
    "content_blocks.json": MP / "ads/content_blocks.json",
    "live_bazaraki.xml": LIVE_FEED,
    "published_ids.json": REPO / "bazaraki_agent/data/published_ids.json",
    "live_ads_meta.csv": MP / "phase_b/live_ads_snapshot_2026-10-03_meta.csv",
}
STATE_DIRS = ("inputs", "output", "stage")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def dashboard_routes() -> list[str]:
    from app import create_app
    with __import__("tempfile").TemporaryDirectory() as d:
        a = create_app(db_path=Path(d) / "x.db", backup_dir=Path(d) / "b")
        return sorted({getattr(r, "path", "") for r in a.routes})


class Sandbox:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.inputs, self.output, self.stage = self.root / "inputs", self.root / "output", self.root / "stage"
        self.db, self.backup_dir, self.snaps = self.root / "dashboard.db", self.root / "backups", self.root / "snapshots"

    # ---------------------------------------------------------------- setup
    @classmethod
    def create(cls, root: Path) -> "Sandbox":
        sb = cls(root)
        sb.root.mkdir(parents=True, exist_ok=True)
        for d in (sb.inputs, sb.output, sb.stage):
            d.mkdir(exist_ok=True)
        for name, src in INPUTS.items():
            shutil.copyfile(src, sb.inputs / name)
        sb.live_md5 = _md5(LIVE_FEED)
        (sb.root / "live_md5.txt").write_text(sb.live_md5, encoding="utf-8")
        from store import Store
        Store(sb.db, sb.backup_dir)            # sandbox dashboard DB (schema only)
        return sb

    def assert_inside(self, path: Path) -> Path:
        p = Path(path).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError(f"sandbox write outside {self.root}: {p}")
        return p

    def _j(self, name):
        return json.loads((self.inputs / name).read_text(encoding="utf-8"))

    def mark_quality_passed(self, service: str) -> None:
        """Sandbox only: simulate a remediated ad that passed the STEP 13.1 quality gate."""
        f = self.assert_inside(self.inputs / "quality_gate.json")
        g = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {"services": {}}
        g["services"][service] = {"passed": True, "simulated": True}
        f.write_text(json.dumps(g, indent=1), encoding="utf-8")

    def quality_gate(self) -> dict:
        f = self.inputs / "quality_gate.json"
        return json.loads(f.read_text(encoding="utf-8"))["services"] if f.is_file() else {}

    def photos(self):
        return pp.read_manifest(self.inputs / "photo_manifest_v3.csv")

    def _save_photos(self, rows):
        pp.write_manifest(rows, self.assert_inside(self.inputs / "photo_manifest_v3.csv"))

    def files(self, service, status):
        return [r["file"] for r in self.photos() if r["service_key"] == service and r["status"] == status
                ] if status != "proposed" else [r["file"] for r in sorted(
                    (r for r in self.photos() if r["service_key"] == service and r["status"] == "proposed"), key=lambda r: int(r["rank"] or 99))]

    def set_photo(self, file, **fields):
        rows = self.photos()
        for r in rows:
            if r["file"] == file:
                r.update(fields)
        self._save_photos(rows)

    def set_ledger(self, entries):
        self.assert_inside(self.inputs / "published_ids.json").write_text(json.dumps(entries), encoding="utf-8")

    # ---------------------------------------------------------------- dashboard -> queue -> apply
    def queue_via_dashboard(self, item_type, items, action):
        from fastapi.testclient import TestClient
        from app import create_app
        client = TestClient(create_app(db_path=self.db, backup_dir=self.backup_dir))
        for it in items:
            r = client.post("/action", data={"item_type": item_type, "item_id": it, "action": action, "confirm": "yes", "note": "sandbox"},
                            follow_redirects=False)
            if r.status_code != 303:
                raise RuntimeError(f"dashboard refused {it}: {r.status_code} {r.text}")

    def apply_queue(self, by: str, date: str) -> dict:
        """Apply pending photo approvals to the SANDBOX photo manifest only (the real dashboard has no apply)."""
        from store import Store
        st = Store(self.db, self.backup_dir)
        rows = self.photos()
        idx = {r["file"]: r for r in rows}
        applied, refused = [], {}
        for q in reversed(st.queue("pending")):
            if q["item_type"] != "photo":
                continue
            r = idx.get(q["item_id"])
            status = "refused_sandbox"
            if r is None:
                refused[q["item_id"]] = ["not in the sandbox manifest"]
            elif q["action"] == "approve":
                try:
                    pp.approve(r, PHOTO_ROOT, by=by, date=date)
                    applied.append(q["item_id"]); status = "applied_sandbox"
                except ValueError as e:
                    refused[q["item_id"]] = [str(e)]
            elif q["action"] in ("reject", "on_hold"):
                r["status"] = "rejected" if q["action"] == "reject" else "on_hold"
                applied.append(q["item_id"]); status = "applied_sandbox"
            st.backup()
            with st.conn() as c:
                c.execute("update approval_queue set status=?, status_ts=? where id=?", (status, time.strftime("%Y-%m-%d %H:%M:%S"), q["id"]))
                st.audit(c, "queue_applied_sandbox" if status == "applied_sandbox" else "queue_refused_sandbox",
                         {"id": q["id"], "item_id": q["item_id"], "refused": refused.get(q["item_id"])})
        self._save_photos(rows)
        return {"applied": applied, "refused": refused}

    # ---------------------------------------------------------------- pipeline
    def run_pipeline(self) -> dict:
        reg = self._j("services_registry.json")
        services = {s["service_key"]: s for s in reg["services"]}
        proposed = self._j("catalog_proposed.json")
        photos = self.photos()
        with open(self.inputs / "live_ads_meta.csv", encoding="utf-8") as f:
            live_titles = {r["id"]: r["title"] for r in csv.DictReader(f)}
        ads_res = ad_engine.run(write=False, data={"registry": reg, "proposed": proposed, "content": self._j("content_blocks.json"),
                                                   "photos": photos, "live_titles": live_titles,
                                                   "quality_gate": self.quality_gate()})
        ads = {a["service_key"]: a for a in ads_res["ads"]}
        live_xml = (self.inputs / "live_bazaraki.xml").read_text(encoding="utf-8")
        ledger = self._j("published_ids.json")
        prev = xml_preview.build_preview(proposed, ads, photos, services, ledger, live_xml)
        write_feed(prev["xml"], self.assert_inside(self.output / "proposed_bazaraki.xml"))
        (self.assert_inside(self.output / "diff.json")).write_text(json.dumps(prev["diff"], indent=1), encoding="utf-8")
        verrs = self._stage_and_validate(prev["included"], photos, ledger)
        c = sqlite3.connect(self.db)
        try:
            ev = dict(c.execute("select event, count(*) from audit_log group by event").fetchall())
        finally:
            c.close()
        return {"ad_status": {k: a["status"] for k, a in ads.items()}, "xml": prev["xml"], "diff": prev["diff"],
                "excluded": prev["excluded"], "ledger_errors": prev["errors"], "validate_errors": verrs,
                "live_xml_unchanged": _md5(LIVE_FEED) == (self.root / "live_md5.txt").read_text(encoding="utf-8"),
                "audit_events": ev, "included": [i["external_id"] for i in prev["included"]]}

    def _stage_and_validate(self, included, photos, ledger) -> list[str]:
        """Simulate the photo migration inside the sandbox and run the PRODUCTION validator on the result."""
        if not included:
            return []
        manifest, listings = {}, []
        for row in included:
            key = row["service_key"]
            for p in xml_preview._approved(photos, key):
                rel = f"photos/{key}/{Path(p['file']).name}"
                dst = self.assert_inside(self.stage / rel)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PHOTO_ROOT / p["file"], dst)
                manifest[rel] = {"file": rel, "service_key": key, "source": "stock" if pp.is_stock(p) else "own",
                                 "rights_status": "licensed" if pp.is_stock(p) else p["rights_status"], "source_url": p["source_url"],
                                 "licence": p["licence"], "project_ref": p["project_ref"], "capture_date": p["download_date"] or "2026-10-03",
                                 "stage": p["stage"], "relevance_reason": p["relevance_reason"], "checksum_sha256": p["checksum_sha256"],
                                 "width": p["width"], "height": p["height"], "consent": "", "approved": "yes",
                                 "approved_by": p["approved_by"], "approved_date": p["approved_date"]}
            listings.append(dict(row, publish=True))
        errors, _ = validate(listings, root=self.stage, rates=self._j("rates.json"), manifest=manifest, ledger=ledger,
                             denylist=load_denylist())
        return errors

    # ---------------------------------------------------------------- backup / rollback
    def state_md5(self) -> str:
        h = hashlib.md5()
        for d in (*[self.root / x for x in STATE_DIRS], ):
            for p in sorted(d.rglob("*")):
                if p.is_file():
                    h.update(str(p.relative_to(self.root)).encode()); h.update(p.read_bytes())
        h.update(self._db_dump().encode("utf-8"))
        return h.hexdigest()

    def _db_dump(self) -> str:
        c = sqlite3.connect(self.db)
        try:
            return "\n".join(c.iterdump())
        finally:
            c.close()

    def snapshot(self, name: str) -> dict:
        dst = self.assert_inside(self.snaps / name)
        if dst.exists():
            shutil.rmtree(dst)
        for d in STATE_DIRS:
            shutil.copytree(self.root / d, dst / d)
        shutil.copyfile(self.db, dst / "dashboard.db")
        return {"name": name, "md5": self.state_md5()}

    def restore(self, name: str) -> None:
        src = self.snaps / name
        for d in STATE_DIRS:
            shutil.rmtree(self.assert_inside(self.root / d))
            shutil.copytree(src / d, self.root / d)
        shutil.copyfile(src / "dashboard.db", self.assert_inside(self.db))


# ---------------------------------------------------------------- CLI scenario
def e2e(service: str = "tiling", root: Path | None = None) -> dict:
    root = root or (MP / "sandbox" / f"run-{time.strftime('%Y%m%d-%H%M%S')}")
    prot = {p: _md5(p) for p in [REPO / "bazaraki_agent/catalog.json", REPO / "bazaraki_agent/data/rates.json",
                                 REPO / "photos/manifest.csv", LIVE_FEED, PHOTO_ROOT / "photo_manifest_v3.csv"]}
    sb = Sandbox.create(root)
    snap = sb.snapshot("initial")
    files = sb.files(service, "proposed")[:5]
    sb.queue_via_dashboard("photo", files, "approve")
    applied = sb.apply_queue(by="Leo (sandbox)", date=time.strftime("%Y-%m-%d"))
    sb.mark_quality_passed(service)              # simulated STEP 13.1 pass; real ads need the real gate
    res = sb.run_pipeline()
    changed = sb.state_md5() != snap["md5"]
    sb.restore("initial")
    restored = sb.state_md5() == snap["md5"]
    res2 = sb.run_pipeline()                    # after rollback: back to 0 eligible
    sb.restore("initial")
    prod_ok = all(_md5(p) == m for p, m in prot.items())
    report = {"root": str(root), "service": service, "queued": files, "applied": applied, "ad_status": res["ad_status"][service],
              "included": res["included"], "validate_errors": res["validate_errors"], "diff_added": res["diff"]["added"],
              "diff_removed": len(res["diff"]["removed"]), "live_xml_unchanged": res["live_xml_unchanged"],
              "rollback_changed_then_restored": changed and restored, "after_rollback_included": res2["included"],
              "production_unchanged": prod_ok, "audit_events": res["audit_events"]}
    (Path(root) / "E2E_RESULT.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["e2e"]); ap.add_argument("--service", default="tiling")
    a = ap.parse_args(argv)
    r = e2e(a.service)
    for k, v in r.items():
        print(f"{k:32} {v}")
    ok = (r["ad_status"] == "ready_to_publish" and not r["validate_errors"] and r["live_xml_unchanged"]
          and r["rollback_changed_then_restored"] and not r["after_rollback_included"] and r["production_unchanged"])
    print("E2E RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
