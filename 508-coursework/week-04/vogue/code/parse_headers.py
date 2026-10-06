#!/usr/bin/env python3
"""Parse the Vogue Archive citation header on each OCR'd page.

The archive has printed its citation header in more than one style across the
scans this archive now holds:

  1892-1893   'Le Bon Oncle D'amérique' Janvier, Thomas. Vogue1. 1 (Dec 17, 1892): 4, 5, 6, 7.;
  1900 (Jul)  Clippings LUND, ADELAIDE. "Clippings." Vogue, Jul 05, 1900. 458, http://…;
  1900 (Aug)  A Midsummer Night's Dream TAYLOR, E. (1900, Aug 23). A midsummer night's
              dream. Vogue, 16, 118-118, 119, 122. Retrieved from http://…;

Each header names the item, sometimes its author, and the issue and printed page.
We only keep what is literally in the OCR text, so every parsed row is grounded.

The issue list is read from research/data/issues.json, so adding an issue there is
all that is needed to have its pages parsed.

Output: artifacts/headers.json  (list of dicts)
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = os.path.join(ROOT, "artifacts", "pages")
ISSUES = os.path.join(ROOT, "research", "data", "issues.json")
OUT = os.path.join(ROOT, "artifacts", "headers.json")

MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

# 1892-1893: 'Title' Author. Vogue1. N (Mon D, YYYY): pages.;
CITE_1892 = re.compile(
    r"Vogue1\.\s*(?P<no>\d+)\s*\((?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\)\s*:\s*(?P<pages>[^;]+);?"
)
# 1900 Aug (also the 1916 style): Title. (YYYY, Mon D). Title. Vogue[, vol], pages. Retrieved ...
CITE_MODERN = re.compile(
    r"\((?P<year>\d{4}),\s*(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\)\.\s*(?P<mid>.*?)"
    r"Vogue,?\s*(?P<vol>\d+)?[,\s]+(?P<pages>[^.]+)\.\s*Retrieved from"
)
# 1900 Jul: display line "Title." Vogue, Mon DD, YYYY. pages, http…
CITE_1900 = re.compile(
    r"Vogue,\s*(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\.\s*(?P<pages>[^,;]+),"
)

AUTHOR = re.compile(r"(?P<author>[A-Z][A-Za-z'\-]+,\s*(?:[A-Z]\.?\s*)*[A-Za-z.\-]*)\s*$")


def last_line(prefix: str) -> str:
    prefix = prefix.strip()
    return prefix.splitlines()[-1] if prefix else ""


def split_title_author_1892(prefix: str):
    prefix = prefix.strip().rstrip(".").strip()
    if prefix.lower().startswith("advertisement"):
        rest = prefix.split(":", 1)[1].strip() if ":" in prefix else ""
        m = re.match(r"^(?P<name>[^(]+?)\s*(?:\((?P<company>[^)]*)\))?$", rest)
        name = (m.group("name").strip() if m else rest) or ""
        company = (m.group("company").strip() if m and m.group("company") else "")
        return "advertisement", name, company, None
    m = re.match(r"^(?P<title>.*?)\s+(?P<author>[A-Z][A-Za-z'\-]+,\s*(?:[A-Z]\.?\s*)*[A-Za-z.\-]*)$", prefix)
    if m and " " in m.group("title"):
        return "article", m.group("title").strip(), "", m.group("author").strip()
    return "item", prefix, "", None


def kind_of(text: str, default: str) -> str:
    t = text.strip().lower()
    if t.startswith("advertisement"):
        return "advertisement"
    if t.startswith("vogue"):
        return "cover"
    return default


def parse_page(text: str):
    """Return a dict of parsed header fields, or None if no header is present."""
    m = CITE_1892.search(text)
    if m:
        prefix = last_line(text[:m.start()])
        kind, title, company, author = split_title_author_1892(prefix)
        return _row(kind, title, company, author, int(m.group("no")), None,
                    m.group("mon"), int(m.group("day")), int(m.group("year")),
                    m.group("pages"), prefix + " " + m.group(0))

    m = CITE_MODERN.search(text)
    if m:
        prefix = last_line(text[:m.start()])
        mid = re.sub(r"\s+", " ", m.group("mid")).strip().rstrip(".")
        low = prefix.strip().lower()
        author = ""
        if not low.startswith(("advertisement", "vogue")):
            author_m = AUTHOR.search(prefix.strip())
            if author_m:
                author = author_m.group("author").strip()
        title = (mid or "Advertisement") if low.startswith("advertisement") else (mid or prefix.strip())
        kind = kind_of(prefix, kind_of(mid, "article"))
        return _row(kind, title, "", author, None, m.group("vol"),
                    m.group("mon"), int(m.group("day")), int(m.group("year")),
                    m.group("pages"), prefix + " " + m.group(0))

    m = CITE_1900.search(text)
    if m:
        prefix = last_line(text[:m.start()])
        qt = re.search(r'"([^"]+)"', prefix)
        if qt:
            title = qt.group(1).strip().rstrip(".")
            rest = prefix[:qt.start()].strip()
        else:
            title, rest = "", prefix.strip()
        author = ""
        if not rest.lower().startswith(("advertisement", "vogue")):
            author_m = AUTHOR.search(rest)
            if author_m:
                author = author_m.group("author").strip()
        title = title or rest
        kind = kind_of(prefix, "cover" if title.strip().lower() == "vogue" else "article")
        return _row(kind, title, "", author, None, None,
                    m.group("mon"), int(m.group("day")), int(m.group("year")),
                    m.group("pages"), prefix + " " + m.group(0))

    return None


def _row(kind, title, company, author, issue_no, volume, mon, day, year, pages, citation):
    return {
        "matched": True, "kind": kind, "title": title, "company": company or "",
        "author": author or "", "issue_no": issue_no, "volume": volume,
        "date_iso": f"{year:04d}-{MONTHS[mon.capitalize()]:02d}-{day:02d}",
        "printed_pages": re.sub(r"\s+", " ", pages).strip(), "citation": citation.strip(),
    }


def main() -> None:
    issues = {it["date_iso"] for it in json.load(open(ISSUES, encoding="utf-8"))}
    rows = []
    for issue in sorted(issues):
        for path in sorted(glob.glob(os.path.join(PAGES, issue, "page-*.txt"))):
            n = int(os.path.basename(path)[5:8])
            text = open(path, encoding="utf-8").read()
            row = parse_page(text)
            if not row:
                rows.append({"issue": issue, "page": n, "matched": False})
            else:
                rows.append({"issue": issue, "page": n, **row})
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    matched = sum(1 for r in rows if r["matched"])
    print(f"{matched}/{len(rows)} pages matched a citation header -> {OUT}")


if __name__ == "__main__":
    main()
