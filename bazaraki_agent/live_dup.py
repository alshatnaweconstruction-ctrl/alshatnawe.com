"""Q-LIVE-DUP: offline duplicate-prevention analyzer (owner decision D-086).

Bazaraki declined all 127 declined ads of the account with one reason: "Duplicate ad. The same ad
is already active in your account or a different account." This module compares proposed ads with
the account's LIVE inventory and blocks any proposal for a service that is already active, even
when the title wording, town, price, category, punctuation or image order was changed.

Read-only and offline by design:
- it never contacts Bazaraki; the inventory is a snapshot file captured read-only (GET of the
  "My ads" list) and saved under master_plan/release_gates/evidence/;
- it fails closed: no snapshot, an unreadable or empty one, or one older than MAX_AGE_HOURS
  blocks every proposal;
- it never edits, deletes, deactivates, reactivates or publishes anything; it writes a dry-run
  report and a service registry only.

    python -m bazaraki_agent.live_dup                    # dry run on master_plan/ads/ads_proposed.json
    python -m bazaraki_agent.live_dup --inventory <psv>  # another snapshot
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

from bazaraki_agent.official import load as load_official
from bazaraki_agent.validate import fold

WS = Path(__file__).resolve().parents[2]
EVIDENCE = WS / "master_plan" / "release_gates" / "evidence"
PROPOSED = WS / "master_plan" / "ads" / "ads_proposed.json"
EXCEPTIONS = WS / "master_plan" / "release_gates" / "live_dup_exceptions.json"
REPORT = WS / "master_plan" / "release_gates" / "LIVE_DUP_DRYRUN.md"
REGISTRY = WS / "master_plan" / "services" / "LIVE_SERVICE_REGISTRY.csv"

MAX_AGE_HOURS = 24
TITLE_JACCARD = 0.5
PHASH_NEAR = 10
FIELDS = ("id", "state", "category", "title", "price", "created", "views", "phone_clicks", "images", "city")


class InventoryError(Exception):
    """The live inventory is missing, unreadable, empty or stale: publishing must stop."""


# ---------------------------------------------------------------- service families
# Ordered: the first matching family wins for one text. Patterns run on folded, lower-case text.
# Pool sub-services are one family each for care and for renovation: the moderator declined
# skimmer / drain / leak / coping ads while another pool-care ad was active.
FAMILY_RULES = [
    ("pool-renovation", r"(?=.*\b(?:pool|πισιν))(?=.*\b(?:resurfac|replaster|plaster|render|construct|tiling|tile|mosaic|waterproof|renovat|ανακαινισ))"),
    ("pool-care", r"\bpool|skimmer|main drain|πισιν"),
    ("ceilings", r"ceiling|ψευδοροφ|οροφ"),
    ("partitions", r"plasterboard|drywall|partition|γυψοσανιδ|χωρισμ"),
    ("electrical", r"electric|rewir|ηλεκτρολογ"),
    ("plumbing", r"plumb|hot water|υδραυλ"),
    ("insulation", r"insulat|etics|θερμομονωσ"),
    ("cleaning", r"cleaning|καθαρισ"),
    ("tiling", r"\btil(?:e|es|ing)\b|marble|porcelain|mosaic|πλακ"),
    ("bathroom", r"bathroom|wet room|μπανι"),
    ("kitchen", r"kitchen|κουζιν"),
    ("flooring", r"flooring|laminate|epoxy|πατωμ"),
    ("waterproofing", r"waterproof|roof sealing|terrace sealing|στεγανο"),
    ("extensions", r"extension|addition|annex|επεκτασ|προσθηκ"),
    ("concrete-repairs", r"(?:structural|concrete|crack|foundation|pillar)\b.*\b(?:repair|restor)|(?:repair|restor)\w*\b.*\b(?:concrete|pillar|crack)|επισκευ\w* σκυροδεμ"),
    ("retaining-walls", r"retaining|αντιστηριξ"),
    ("boundary-walls", r"garden wall|boundary|fence|perimeter wall|περιφραξ"),
    ("landscaping", r"landscap|κηποτεχν"),
    ("paving", r"paving|driveway"),
    ("stone-cladding", r"stone cladding|feature wall"),
    ("stone-walling", r"stone wall|masonry|πετρ"),
    ("plastering", r"\bplaster(?:ing)?\b|graffiato|skimming|render|facade|σοβα"),
    ("painting", r"paint|decorat|βαψ|χρωματισ"),
    ("windows-doors", r"window|door|aluminium|κουφωμ"),
    ("maintenance", r"maintenance|property owners|overseas owners|property care|συντηρησ"),
    ("groundworks", r"groundwork|site prep|εκσκαφ"),
    ("renovation", r"renovat|ανακαινισ"),
    ("general-building", r"construct|contractor|block ?work|concrete works|general works|builder|κατασκευ"),
]
SERVICE_FAMILY = {"new-build": "general-building", "structural": "general-building", "light-steel": "general-building",
                  "full-renovation": "renovation", "remote-owner": "maintenance", "etics": "insulation",
                  "damp-repairs": "waterproofing", "repairs": "maintenance",
                  "joinery": "windows-doors", "doors-windows": "windows-doors"}
# Different services that a moderator may still read as the same item: warning for manual review, not a block.
RELATED = {frozenset(p) for p in (("bathroom", "tiling"), ("kitchen", "tiling"), ("retaining-walls", "boundary-walls"),
                                  ("partitions", "ceilings"), ("pool-care", "pool-renovation"), ("renovation", "general-building"),
                                  ("waterproofing", "insulation"), ("plastering", "painting"))}
LICENCE_GATED = {"electrical", "plumbing"}
# Categories (Bazaraki rubric names) that fit each family. Anything else = wrong category.
FAMILY_CATEGORIES = {
    "pool-care": {"Pools maintenance"}, "pool-renovation": {"Pools maintenance", "Renovation"},
    "ceilings": {"Plasterboard", "Renovation", "Builders"}, "partitions": {"Plasterboard", "Renovation", "Builders"},
    "electrical": {"Electricians"}, "plumbing": {"Plumbers"}, "insulation": {"Insulation", "Builders", "Renovation"},
    "cleaning": {"Cleaning"}, "tiling": {"Tiler", "Renovation"}, "bathroom": {"Renovation", "Tiler", "Builders"},
    "kitchen": {"Renovation", "Carpenters", "Builders"}, "flooring": {"Tiler", "Carpenters", "Renovation"},
    "waterproofing": {"Insulation", "Renovation", "Builders"}, "extensions": {"Builders", "Renovation"},
    "concrete-repairs": {"Builders", "Renovation"}, "boundary-walls": {"Builders"}, "retaining-walls": {"Builders"}, "landscaping": {"Gardeners"},
    "paving": {"Builders", "Gardeners"}, "stone-cladding": {"Builders", "Renovation", "Tiler"},
    "stone-walling": {"Builders", "Renovation"}, "plastering": {"Painters", "Renovation", "Builders"},
    "painting": {"Painters"}, "windows-doors": {"Carpenters", "Builders", "Renovation"},
    "maintenance": {"Handymen", "Renovation", "Other services"}, "groundworks": {"Builders"},
    "renovation": {"Renovation", "Builders"}, "general-building": {"Builders"},
}
HIGH_CLAIMS = ["licensed", "certified", "insured", "luxury", "guarantee", "guaranteed", "best", "top", "no.? ?1", "number one"]
MEDIUM_CLAIMS = ["premium", "expert", "specialist", "professional", "trusted", "reliable", "experienced", "skilled",
                 "quality", "master", "dedicated", "efficient", "fast", "local", "affordable", "cheap"]
FILLER = {"in", "and", "for", "the", "of", "with", "to", "a", "or", "on", "your", "from", "at", "by", "cyprus", "service",
          "services", "works", "work", "homes", "home", "villas", "properties", "property"}


def _t(text) -> str:
    return fold(str(text or "")).lower()


def family_of(text: str) -> str | None:
    t = _t(text)
    for fam, pat in FAMILY_RULES:
        if re.search(pat, t):
            return fam
    return None


def _title_families(p: dict) -> set[str]:
    return {f for f in (family_of(p.get(k)) for k in ("title_en", "title_el")) if f}


def proposal_families(p: dict) -> set[str]:
    """The catalog service_key decides the family, so rewording the title cannot bypass the check.
    Only a proposal without a known service_key falls back to its titles."""
    key = p.get("service_key")
    fam = SERVICE_FAMILY.get(key, key if key in FAMILY_CATEGORIES else None) if key else None
    return {fam} if fam else _title_families(p)


@lru_cache(maxsize=1)
def _places() -> frozenset[str]:
    out = set()
    for name in load_official()["districts"].values():
        for part in re.split(r"[/,()]", _t(name)):
            part = part.strip()
            if part:
                out.add(part)
    return frozenset(out)


def title_tokens(title: str) -> set[str]:
    t = re.sub(r"[^a-zͰ-Ͽ ]+", " ", _t(title))
    places = _places()
    claims = {c for c in HIGH_CLAIMS + MEDIUM_CLAIMS if " " not in c and "?" not in c}
    return {w for w in t.split() if len(w) > 2 and w not in FILLER and w not in places and w not in claims}


def _jac(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def _ham(a, b) -> int:
    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except (TypeError, ValueError):
        return 99


def claims_in(title: str) -> list[str]:
    t = _t(title)
    return [c for c in HIGH_CLAIMS + MEDIUM_CLAIMS if re.search(rf"\b{c}\b", t)]


# ---------------------------------------------------------------- inventory
def load_inventory(path: Path, now: dt.datetime | None = None, max_age_hours: int = MAX_AGE_HOURS) -> dict:
    """Parse a read-only snapshot (pipe-separated, '# captured_at: ISO' header). Fails closed."""
    path = Path(path)
    if not path.is_file():
        raise InventoryError(f"live inventory not found: {path}")
    captured, ads = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            m = re.match(r"#\s*captured_at:\s*(\S+)", line)
            if m:
                captured = dt.datetime.fromisoformat(m.group(1))
            continue
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) != len(FIELDS):
            raise InventoryError(f"unreadable inventory line: {line[:60]}")
        ad = dict(zip(FIELDS, parts))
        ad["id"] = int(ad["id"])
        ads.append(ad)
    if captured is None:
        raise InventoryError("inventory has no captured_at timestamp")
    if not ads:
        raise InventoryError("inventory is empty")
    age = ((now or dt.datetime.now()) - captured).total_seconds() / 3600
    if age > max_age_hours:
        raise InventoryError(f"inventory is {age:.0f} h old (max {max_age_hours} h): capture a fresh read-only snapshot")
    return {"captured_at": captured, "ads": ads}


def _active(inv):
    return [a for a in inv["ads"] if a["state"] == "A"]


def _img_keys(images):
    if not isinstance(images, list):          # the snapshot carries only an image count
        return []
    return [(i.get("checksum_sha256"), i.get("phash")) for i in images if isinstance(i, dict)]


def _valid_exception(e: dict) -> bool:
    return all(str(e.get(k) or "").strip() for k in ("service_key", "active_id", "approved_by", "date", "reason"))


# ---------------------------------------------------------------- checks
def check_proposal(p: dict, inv: dict, exceptions=()) -> list[dict]:
    fams, toks = proposal_families(p), title_tokens(p.get("title_en", ""))
    excepted = {int(e["active_id"]) for e in exceptions if _valid_exception(e) and e["service_key"] == p.get("service_key")}
    out = []
    off_title = _title_families(p) - fams
    if off_title:
        out.append({"code": "W-LIVE-TITLE", "msg": f"title reads as {sorted(off_title)}, service_key is {sorted(fams)}: review wording"})
    for a in inv["ads"]:
        fam_a = family_of(a["title"])
        same_family = fam_a is not None and fam_a in fams
        similar = _jac(toks, title_tokens(a["title"])) >= TITLE_JACCARD
        if a["state"] != "A":
            if same_family or similar:
                out.append({"code": "W-LIVE-DECLINED", "declined_id": a["id"],
                            "msg": f"same service was declined before as a duplicate: #{a['id']} {a['title']!r}"})
            continue
        if not (same_family or similar) and fam_a and any(frozenset((fam_a, f)) in RELATED for f in fams):
            out.append({"code": "W-LIVE-RELATED", "active_id": a["id"],
                        "msg": f"related service already active: #{a['id']} {a['title']!r} ({fam_a}): keep text and photos clearly different"})
        if same_family or similar:
            why = f"family {fam_a}" if same_family else f"title similarity {_jac(toks, title_tokens(a['title'])):.2f}"
            if a["id"] in excepted:
                out.append({"code": "X-OWNER-EXCEPTION", "active_id": a["id"], "msg": f"owner-approved exception vs #{a['id']} ({why})"})
            else:
                out.append({"code": "Q-LIVE-DUP", "active_id": a["id"], "msg": f"already active: #{a['id']} {a['title']!r} ({why})"})
        mine, theirs = _img_keys(p.get("images")), _img_keys(a.get("images"))
        for sha, ph in mine:
            if any((sha and sha == s2) or (ph and ph2 and _ham(ph, ph2) <= PHASH_NEAR) for s2, ph2 in theirs):
                out.append({"code": "Q-LIVE-DUP-IMG", "active_id": a["id"], "msg": f"image already used by active ad #{a['id']}"})
                break
    return out


def check(proposals, inventory_path: Path, exceptions=(), now: dt.datetime | None = None) -> dict:
    """Dry run for many proposals. Any inventory problem blocks every proposal (fail closed)."""
    try:
        inv, err = load_inventory(inventory_path, now=now), None
    except InventoryError as e:
        inv, err = None, str(e)
    results = []
    for p in proposals:
        if err:
            f = [{"code": "Q-LIVE-DUP-INV", "msg": err}]
        else:
            f = check_proposal(p, inv, exceptions)
        blocked = any(x["code"].startswith("Q-") for x in f)
        results.append({"service_key": p.get("service_key"), "title_en": p.get("title_en"), "findings": f, "allowed": not blocked})
    return {"inventory_ok": err is None, "inventory_error": err, "inventory": inv, "results": results}


# ---------------------------------------------------------------- registry of live services
def registry(inv: dict) -> list[dict]:
    declined = [a for a in inv["ads"] if a["state"] != "A"]
    rows = []
    for a in _active(inv):
        fam = family_of(a["title"])
        cl = claims_in(a["title"])
        wrong = bool(fam) and a["category"] not in FAMILY_CATEGORIES.get(fam, set())
        high = any(c in HIGH_CLAIMS for c in cl) or fam in LICENCE_GATED
        risk = "high" if high else ("medium" if wrong or cl else "low")
        twins = sum(1 for d in declined if (fam and family_of(d["title"]) == fam)
                    or _jac(title_tokens(a["title"]), title_tokens(d["title"])) >= TITLE_JACCARD)
        rows.append({"service_id": f"LIVE-{fam or 'other'}", "ad_id": a["id"], "family": fam or "other", "category": a["category"],
                     "location": a.get("city", ""), "title": a["title"], "main_claim": ", ".join(cl), "price": a.get("price", ""),
                     "risk": risk, "wrong_category": wrong, "licence_gated": fam in LICENCE_GATED,
                     "image_fingerprint": "n/a (not in snapshot)",
                     "text_fingerprint": hashlib.sha1(" ".join(sorted(title_tokens(a["title"]))).encode()).hexdigest()[:12],
                     "status": "active", "last_verified": inv["captured_at"].isoformat(timespec="minutes"),
                     "owner_approval": "no", "declined_twins": twins,
                     "active_twins": ", ".join(str(b["id"]) for b in _active(inv) if b is not a and fam and family_of(b["title"]) == fam),
                     "views": a.get("views", ""), "phone_clicks": a.get("phone_clicks", "")})
    return rows


# ---------------------------------------------------------------- reports
def _latest_snapshot() -> Path:
    snaps = sorted(EVIDENCE.glob("live_inventory_*.psv"))
    return snaps[-1] if snaps else EVIDENCE / "live_inventory_MISSING.psv"


def write_reports(rep: dict, report: Path = REPORT, registry_csv: Path = REGISTRY) -> None:
    L = ["# Q-LIVE-DUP dry run (offline, read-only)", "",
         "Nothing was published, edited, deactivated or deleted. This is a report only.", ""]
    if not rep["inventory_ok"]:
        L += [f"**Inventory problem, every proposal blocked (fail closed):** {rep['inventory_error']}", ""]
    else:
        inv = rep["inventory"]
        act = _active(inv)
        L += [f"Inventory snapshot: captured {inv['captured_at']:%Y-%m-%d %H:%M}; {len(inv['ads'])} ads, {len(act)} active.", ""]
        reg = registry(inv)
        with open(registry_csv, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.DictWriter(fh, list(reg[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(reg)
        L += ["## Live service registry (active ads)", "",
              "| Ad | Family | Category | Title | Claim | Risk | Wrong cat. | Declined twins | Active twin |",
              "|---|---|---|---|---|---|---|---:|---|"]
        L += [f"| {r['ad_id']} | {r['family']} | {r['category']} | {r['title'][:55]} | {r['main_claim']} | {r['risk']} | "
              f"{'yes' if r['wrong_category'] else ''} | {r['declined_twins']} | {r['active_twins']} |" for r in reg]
        L += [""]
    L += ["## Proposals", "", "| Service | Title | Result | Findings |", "|---|---|---|---|"]
    for r in rep["results"]:
        f = "; ".join(x["msg"] for x in r["findings"] if not x["code"].startswith("W-")) or "none"
        ws = [x["code"] for x in r["findings"] if x["code"].startswith("W-")]
        wtxt = ", ".join(f"{c} ×{ws.count(c)}" for c in sorted(set(ws)))
        L.append(f"| {r['service_key']} | {(r['title_en'] or '')[:55]} | {'allowed' if r['allowed'] else '**BLOCKED**'} | "
                 f"{f[:300]}{f' (warnings: {wtxt})' if ws else ''} |")
    report.write_bytes(("\n".join(L) + "\n").encode("utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inventory", type=Path, default=None)
    ap.add_argument("--proposed", type=Path, default=PROPOSED)
    ap.add_argument("--exceptions", type=Path, default=EXCEPTIONS)
    a = ap.parse_args(argv)
    proposals = json.loads(a.proposed.read_text(encoding="utf-8")) if a.proposed.is_file() else []
    exc = json.loads(a.exceptions.read_text(encoding="utf-8")) if a.exceptions.is_file() else []
    rep = check(proposals, a.inventory or _latest_snapshot(), exc)
    write_reports(rep)
    blocked = sum(1 for r in rep["results"] if not r["allowed"])
    print(f"inventory_ok={rep['inventory_ok']} proposals={len(rep['results'])} blocked={blocked} -> {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
