"""STEP 13.1: report writers for ad_quality_validator.run(). Writes ONLY master_plan/quality/."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter

from bazaraki_agent import ad_quality_policy as P
from bazaraki_agent.ad_quality_validator import GATE, IMAGE_CODES, QUALITY, single_image_problems

FIRST_BATCH = ("repairs", "ceilings", "bathroom")
PHOTO_PRIORITY = ("waterproofing", "bathroom", "etics")       # owner order (D-058); other services follow by gap size
CODE_TEXT = {
    "Q-COMPANY": "company name / legal entity / HE number / office line in the description",
    "Q-PASTOR": "no problem, process or customer-type section",
    "Q-TEMPLATE": "shared template lines (same closing line in every ad)",
    "Q-TITLE": "title outside 55-70 characters (mostly the Greek titles)",
    "Q-PRICE-SCOPE": "'from' price without a stated scope",
    "Q-CLAIM": "claim without evidence",
    "Q-IMG-COUNT": "fewer than 5 approved exact-match images",
    "Q-IMG-SCORE": "images below 85/100",
    "Q-IMG-TITLE": "images that do not show what the title says",
    "Q-IMG-MATCH": "images of the wrong subject or generic images",
    "Q-IMG-COVER": "cover image not the strongest literal match",
    "Q-IMG-WATERMARK": "logo / watermark on an image",
    "Q-IMG-NEAR": "near-duplicate images (same scene)",
    "Q-IMG-RECORD": "incomplete image record",
}


def _w(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def summarise(res) -> dict:
    reg, out = res["registry"], {}
    draft_by = {d["service_key"]: d for d in res["drafts"]}
    for key, v in res["legacy"].items():
        svc = reg.get(key, {})
        imgs = v["images"]
        good = [i for i in imgs if i.get("scores") and not single_image_problems(i, {"service_key": key, "title_en": draft_by.get(key, {}).get("title_en", "")})]
        price = svc.get("pricing", {}).get("price_status")
        derr = res["draft_errors"].get(key, [])
        out[key] = {
            "legacy_status": v["status_before"],
            "legacy_codes": sorted({c for c, _ in v["errors"]}),
            "needs_rewrite": any(not c.startswith("Q-IMG") for c, _ in v["errors"]),
            "draft_text_clean": not [e for e in derr if e[0] not in IMAGE_CODES and e[0] != "Q-IMG-STOCK"],
            "images_proposed": len(imgs),
            "images_pass_rubric": len(good),
            "images_owner_approved": sum(1 for i in imgs if i.get("approved")),
            "missing_images": max(0, P.MIN_APPROVED_IMAGES - len(good)),
            "price_status": price,
            "compliance_required": bool(svc.get("hospitality", {}).get("compliance_required")),
            "blocked_by_evidence": price != "approved" or bool(svc.get("hospitality", {}).get("compliance_required")),
            "passed": False if v["errors"] else True,
        }
    return out


def _gate_json(summary) -> str:
    return json.dumps({"_meta": {"step": "13.1", "date": "2026-10-03",
                                 "rule": "an ad may be ready_to_review / ready_to_publish / XML-eligible only if passed is true",
                                 "source": "python -m bazaraki_agent.ad_quality_validator"},
                       "services": {k: {"passed": s["passed"], "draft_text_clean": s["draft_text_clean"],
                                        "images_pass_rubric": s["images_pass_rubric"],
                                        "images_owner_approved": s["images_owner_approved"],
                                        "blocked_by_evidence": s["blocked_by_evidence"]} for k, s in summary.items()}},
                      ensure_ascii=False, indent=1)


def _photo_csv(rows) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def _priority(summary):
    def key(k):
        s = summary[k]
        return (s["blocked_by_evidence"], s["missing_images"], k not in FIRST_BATCH, k)
    return sorted(summary, key=key)


def _draft_md(d, errs) -> str:
    text = [e for e in errs if e[0] not in IMAGE_CODES and e[0] != "Q-IMG-STOCK"]
    img = sorted({c for c, _ in errs if c in IMAGE_CODES})
    lines = [f"# {d['service_key']}: remediated draft (REVIEW ONLY)", "",
             "Not used by ad_engine, feed or XML. The original in master_plan/ads/drafts/ is unchanged.", "",
             f"- Title EN ({len(d['title_en'])}): {d['title_en']}", f"- Title EL ({len(d['title_el'])}): {d['title_el']}",
             f"- Text checks: {'PASS' if not text else 'FAIL'}" + ("" if not text else " " + "; ".join(m for _, m in text)),
             f"- Image checks: {', '.join(img) if img else 'PASS'}", "", "## Description", "", "```", d["description"], "```", ""]
    return "\n".join(lines)


def _report(res, summary) -> str:
    n = len(summary)
    rew = sum(1 for s in summary.values() if s["needs_rewrite"])
    pho = sum(1 for s in summary.values() if s["missing_images"] > 0)
    evi = sum(1 for s in summary.values() if s["blocked_by_evidence"])
    ok = sum(1 for s in summary.values() if s["passed"])
    clean = sum(1 for s in summary.values() if s["draft_text_clean"])
    fails = Counter(c for s in summary.values() for c in s["legacy_codes"])
    pc = Counter(p["decision"] for p in res["photos"])
    proposed = [p for p in res["photos"] if p["manifest_status"] == "proposed"]
    ppass = sum(1 for p in proposed if p["decision"].startswith("passes"))
    L = ["# AD REMEDIATION REPORT (STEP 13.1)", "",
         "Generated by `python -m bazaraki_agent.ad_quality_validator` on 2026-10-03. Read-only audit: no production file,",
         "manifest, XML or live ad was changed, and no photo was approved.",
         f"Audited layout: {', '.join(sorted({v.get('layout', 'legacy') for v in res['legacy'].values()}))}. "
         "The audit of the original drafts (before regeneration) is kept in AD_REMEDIATION_REPORT_pre_regeneration.md.", "",
         "## Summary", "",
         "| Item | Count |", "|---|---:|",
         f"| Ads audited (master_plan/ads/ads_proposed.json) | {n} |",
         f"| Ads needing a text rewrite | {rew} |",
         f"| Ads needing photo replacement (fewer than 5 photos pass the rubric) | {pho} |",
         f"| Ads blocked by missing evidence (price research or compliance documents) | {evi} |",
         f"| Ads already passing the Advanced Ad Standard | {ok} |",
         f"| Remediated drafts with clean text (review only) | {clean} / {n} |",
         f"| Proposed photos scored | {len(proposed)} |",
         f"| Proposed photos passing the rubric (>= 85, exact match, unique) | {ppass} |",
         f"| Proposed photos rejected for match / quality | {len(proposed) - ppass} |",
         f"| Owner-approved photos | 0 |", "",
         "Every ad also fails Q-IMG-COUNT until the owner approves 5 photos per ad; a rubric pass is not an approval.", "",
         "## Most common failures (current drafts)", "", "| Code | Ads | Meaning |", "|---|---:|---|"]
    for c, k in fails.most_common():
        L.append(f"| {c} | {k} | {CODE_TEXT.get(c, '')} |")
    L += ["", "## First 10 services to remediate", "",
          "Order: evidence available first (approved price, no compliance hold), then fewest missing photos, first batch first on ties.", "",
          "| # | Service | Price | Photos passing | Missing | Draft text | Next action |", "|---:|---|---|---:|---:|---|---|"]
    for i, k in enumerate(_priority(summary)[:10], 1):
        s = summary[k]
        act = "owner approves 5 photos" if s["missing_images"] == 0 else f"find {s['missing_images']} exact-match photo(s)"
        if s["blocked_by_evidence"]:
            act = "evidence first (price / documents); " + act
        L.append(f"| {i} | {k} | {s['price_status']} | {s['images_pass_rubric']}/5 | {s['missing_images']} | "
                 f"{'clean' if s['draft_text_clean'] else 'issues'} | {act} |")
    L += ["", "## All services", "", "| Service | Legacy status | Gate status | Codes | Photos passing | Evidence blocker |", "|---|---|---|---|---:|---|"]
    for k in _priority(summary):
        s = summary[k]
        blk = "compliance docs" if s["compliance_required"] else ("price research" if s["blocked_by_evidence"] else "-")
        gate = "draft" if s["legacy_status"].startswith("ready") else s["legacy_status"]
        L.append(f"| {k} | {s['legacy_status']} | {gate} | {' '.join(s['legacy_codes'])} | {s['images_pass_rubric']}/5 | {blk} |")
    L += ["", "## Photo audit (photo_quality_audit.csv)", "", "| Decision | Photos |", "|---|---:|"]
    for d, k in pc.most_common():
        L.append(f"| {d} | {k} |")
    L += ["", "Candidate and on_hold photos were not visually scored (owner decision D-058); they stay untouched as a reserve.",
          "", "## What changed and what did not", "",
          "- New: policy, validator, reports, tests, review-only drafts, quality_gate.json, photo_scores.json, photo_quality_audit.csv.",
          "- Gate: ad_engine and xml_preview read quality_gate.json; no ad can be ready_to_review, ready_to_publish or XML-eligible without passed=true.",
          "- Unchanged: catalog.json, rates.json, manifest.csv, photo_manifest_v3.csv, bazaraki.xml, feed.py, validate.py, content_blocks.json, master_plan/ads/.",
          "- The legacy drafts in master_plan/ads/ were not regenerated; their stored status (14 ready_to_review) predates the gate.", ""]
    return "\n".join(L)


def _gap_report(summary, res, replace) -> str:
    def order(k):
        return (PHOTO_PRIORITY.index(k) if k in PHOTO_PRIORITY else 9, -summary[k]["missing_images"], k)
    L = ["# IMAGE GAP REPORT", "", "Source: STEP 13.1 audit (photo_scores.json + photo_quality_audit.csv), 2026-10-03.",
         "Approved = owner-approved; nothing is approved yet, so every service needs 5 approvals. 'Passing' = rubric pass, awaiting the owner.", "",
         "| Priority | Service | Approved | Passing rubric | Missing (to reach 5 passing) | Required roles still missing | Research status | Blocker |",
         "|---:|---|---:|---:|---:|---|---|---|"]
    i = 0
    for k in sorted(summary, key=order):
        s = summary[k]
        i += 1
        have = {r["role"] for r in res["photos"] if r["service_key"] == k and r["decision"].startswith("passes")}
        need = [r for r in ("cover", "scope", "detail", "finished-result") if r not in have]
        blk = ["compliance docs"] if s["compliance_required"] else (["price research"] if s["blocked_by_evidence"] else [])
        blk = ", ".join(blk + (["missing photos"] if s["missing_images"] else []) + ["owner photo approval"])
        status = "plan written, search not started" if s["missing_images"] else "no search needed"
        L.append(f"| {i} | {k} | {s['images_owner_approved']} | {s['images_pass_rubric']} | {s['missing_images']} | "
                 f"{', '.join(need) or '-'} | {status} | {blk} |")
    L += ["", "Requirement per service: see IMAGE_RESEARCH_PLAN.md.", "",
          "Not listed (no registry service, or postponed until the owner confirms them): mechanical ventilation, external building",
          "cleaning, plumbing, AC, heating, cleaning, gardening, security systems, sewage.", ""]
    return "\n".join(L)


def write_all(res) -> dict:
    summary = summarise(res)
    sc = json.loads((QUALITY / "photo_scores.json").read_text(encoding="utf-8"))
    _w(GATE, _gate_json(summary))
    _w(QUALITY / "photo_quality_audit.csv", _photo_csv(res["photos"]))
    for d in res["drafts"]:
        _w(QUALITY / "remediated_drafts" / f"{d['service_key']}.md", _draft_md(d, res["draft_errors"][d["service_key"]]))
    _w(QUALITY / "AD_REMEDIATION_REPORT.md", _report(res, summary))
    _w(QUALITY / "IMAGE_GAP_REPORT.md", _gap_report(summary, res, sc.get("replacement_requirements", {})))
    _w(QUALITY / "audit_summary.json", json.dumps(summary, ensure_ascii=False, indent=1))
    return summary
