#!/usr/bin/env python3
"""Turn the OCR + page headers + validated candidate rows into research/data/*.json.

Sources of input:
  artifacts/headers.json            parsed Vogue-Archive citation headers (one per page)
  artifacts/pages/<issue>/*.txt     the OCR text of every page
  artifacts/candidates/*.json       advertiser / people / topic rows proposed by the
                                    extraction agents, afterwards checked verbatim
                                    against the OCR (see code/validate_candidates.py)

Output (committed, and the only thing code/build_db.py reads):
  research/data/pages.json
  research/data/entries.json
  research/data/advertisers.json
  research/data/people.json
  research/data/topics.json

The five generated files are rebuilt deterministically from the accumulated
candidates, so a new issue adds rows without touching old ones. Curate by editing
artifacts/candidates/*.json (or the two hand-maintained files sources.json /
issues.json); re-running this script overwrites the generated files.
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "research", "data")
PAGES = os.path.join(ROOT, "artifacts", "pages")
HEADERS = os.path.join(ROOT, "artifacts", "headers.json")
CANDS = os.path.join(ROOT, "artifacts", "candidates")
ISSUES_JSON = os.path.join(DATA, "issues.json")

ISSUES = [it["date_iso"] for it in json.load(open(ISSUES_JSON, encoding="utf-8"))]
ISSUE_META = {it["date_iso"]: it for it in json.load(open(ISSUES_JSON, encoding="utf-8"))}
ROMAN = re.compile(r"^[ivxl]+$")


def page_section(label: str) -> str:
    lab = label.strip().rstrip(".").strip()
    first = lab.split(",")[0].strip()
    if first.upper().startswith("C"):
        return "cover"
    if first.upper().startswith("S"):
        return "society supplement"
    if ROMAN.match(first.lower()):
        return "advertisements"
    return "editorial"


def clean_name(raw: str):
    """Drop possessives / place-possessives that are not people."""
    if re.search(r"'s\b", raw) or "conservatory" in raw.lower():
        return None
    name = raw.strip().rstrip(",").strip()
    if not name:
        return None
    return name


FLOWERS = {"Madame Caroline Testout", "American Beauties", "green carnation"}
RECLASSIFY = {"India Rugs": ("object", None), "humps": (None, None),
              "Aristocracy": (None, "drop")}


def main() -> None:
    headers = { (r["issue"], r["page"]): r for r in json.load(open(HEADERS, encoding="utf-8")) }

    pages, entries = [], []
    pid = 0
    for issue in ISSUES:
        issue_no = ISSUE_META[issue]["issue_no"]
        for path in sorted(glob.glob(os.path.join(PAGES, issue, "page-*.txt"))):
            n = int(os.path.basename(path)[5:8])
            text = open(path, encoding="utf-8").read()
            h = headers.get((issue, n), {"matched": False})
            pid += 1
            label = h.get("printed_pages", "") if h.get("matched") else ""
            pages.append({
                "id": pid, "issue": issue, "issue_no": issue_no, "ocr_page": n,
                "printed_label": label, "section": page_section(label) if label else "continuation",
                "header_kind": h.get("kind", "") if h.get("matched") else "",
                "header_title": h.get("title", "") if h.get("matched") else "",
                "header_author": (h.get("author") or "") if h.get("matched") else "",
                "header_company": h.get("company", "") if h.get("matched") else "",
                "matched": bool(h.get("matched")), "chars": len(text),
                "note": "" if h.get("matched") else "continuation page: no citation header in the scan",
            })
            if h.get("matched"):
                entries.append({
                    "page_id": pid, "issue": issue, "ocr_page": n,
                    "kind": h["kind"], "title_raw": h["title"], "author_raw": h.get("author") or "",
                    "company_raw": h.get("company", ""), "printed_pages_raw": h["printed_pages"],
                    "citation_raw": h["citation"].strip(), "note": "",
                })

    # ---- advertisers / people / topics: validate then curate ----
    def norm(s):
        return re.sub(r"\s+", " ", s).strip().lower()

    page_text = {}
    for issue in ISSUES:
        for p in glob.glob(os.path.join(PAGES, issue, "page-*.txt")):
            n = int(os.path.basename(p)[5:8])
            page_text[(issue, n)] = norm(open(p, encoding="utf-8").read())

    advertisers, people, topics = [], [], []
    for f in sorted(glob.glob(os.path.join(CANDS, "*.json"))):
        issue = json.load(open(f, encoding="utf-8"))["issue"]
        d = json.load(open(f, encoding="utf-8"))
        for r in d.get("advertisers", []):
            if norm(r["name_raw"]) not in page_text[(issue, r["page"])]:
                continue
            advertisers.append({
                "issue": issue, "ocr_page": r["page"], "name_raw": r["name_raw"].strip(),
                "category_raw": r.get("category", ""), "address_raw": r.get("address_raw", ""),
                "city_raw": r.get("city", ""), "note": "",
            })
        for r in d.get("people", []):
            if norm(r["name_raw"]) not in page_text[(issue, r["page"])]:
                continue
            name = clean_name(r["name_raw"])
            if not name:
                continue
            people.append({
                "issue": issue, "ocr_page": r["page"], "name_raw": name,
                "role_raw": r.get("role_raw", ""), "note": "",
            })
        for r in d.get("topics", []):
            if norm(r["term_raw"]) not in page_text[(issue, r["page"])]:
                continue
            term, kind = r["term_raw"].strip(), r.get("kind", "")
            if term in RECLASSIFY:
                new_kind, drop = RECLASSIFY[term]
                if drop:
                    continue
                kind = new_kind or kind
            if term in FLOWERS:
                kind = "flower"
            topics.append({
                "issue": issue, "ocr_page": r["page"], "term_raw": term,
                "kind": kind, "note": "",
            })

    os.makedirs(DATA, exist_ok=True)
    for name, rows in [("pages", pages), ("entries", entries), ("advertisers", advertisers),
                       ("people", people), ("topics", topics)]:
        with open(os.path.join(DATA, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)
        print(f"{name:14} {len(rows):>4} rows")


if __name__ == "__main__":
    main()
