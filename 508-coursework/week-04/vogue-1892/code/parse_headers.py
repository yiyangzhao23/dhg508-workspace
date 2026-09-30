#!/usr/bin/env python3
"""Parse the Vogue Archive citation header on each OCR'd page.

Each page image in these scans carries a machine-generated header added by the
digitising archive, e.g.

    Advertisement: The Century Co. (Century Company) Vogue1. 1 (Dec 17, 1892): iii.;
    'Le Bon Oncle D'amérique' Janvier, Thomas. Vogue1. 1 (Dec 17, 1892): 4, 5, 6, 7.;
    Society In Novels Vogue1. 1 (Dec 17, 1892): 15.;

It names the item, its author (for articles), the issue and the printed page.
We only keep what is literally in the OCR text, so every parsed row is grounded.

Output: artifacts/headers.json  (list of dicts)
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = os.path.join(ROOT, "artifacts", "pages")
OUT = os.path.join(ROOT, "artifacts", "headers.json")

CITE = re.compile(
    r"Vogue1\.\s*(?P<no>\d+)\s*\((?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\)\s*:\s*(?P<pages>[^;]+);?"
)
MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def split_title_author(prefix: str):
    prefix = prefix.strip().rstrip(".").strip()
    if prefix.lower().startswith("advertisement"):
        rest = prefix.split(":", 1)[1].strip() if ":" in prefix else ""
        # e.g. "The Century Co. (Century Company)" -> name + parenthetical company
        m = re.match(r"^(?P<name>[^(]+?)\s*(?:\((?P<company>[^)]*)\))?$", rest)
        name = (m.group("name").strip() if m else rest) or ""
        company = (m.group("company").strip() if m and m.group("company") else "")
        return "advertisement", name, company, None
    # trailing author "Lastname, Firstname." or "Cavazza, E."
    m = re.match(r"^(?P<title>.*?)\s+(?P<author>[A-Z][A-Za-z'\-]+,\s*(?:[A-Z]\.?\s*)*[A-Za-z.\-]*)$", prefix)
    if m and " " in m.group("title"):
        return "article", m.group("title").strip(), "", m.group("author").strip()
    return "item", prefix, "", None


def main() -> None:
    rows = []
    for issue in ["1892-12-17", "1892-12-24", "1892-12-31"]:
        for path in sorted(glob.glob(os.path.join(PAGES, issue, "page-*.txt"))):
            n = int(os.path.basename(path)[5:8])
            text = open(path, encoding="utf-8").read()
            m = CITE.search(text)
            if not m:
                rows.append({"issue": issue, "page": n, "matched": False})
                continue
            prefix = text[:m.start()]
            # citation header is usually the first line; keep only the final line of the prefix
            prefix = prefix.strip().splitlines()[-1] if prefix.strip() else ""
            kind, title, company, author = split_title_author(prefix)
            mon, day, year = m.group("mon"), int(m.group("day")), int(m.group("year"))
            rows.append({
                "issue": issue, "page": n, "matched": True, "kind": kind,
                "title": title, "company": company, "author": author,
                "issue_no": int(m.group("no")),
                "date_iso": f"{year:04d}-{MONTHS[mon]:02d}-{day:02d}",
                "printed_pages": m.group("pages").strip(),
                "citation": prefix + " " + m.group(0),
            })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    matched = sum(1 for r in rows if r["matched"])
    print(f"{matched}/{len(rows)} pages matched a citation header -> {OUT}")


if __name__ == "__main__":
    main()
