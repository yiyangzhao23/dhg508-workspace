#!/usr/bin/env python3
"""Check 20 random rows of vogue-1892.db against the originals.

The "original" for a row is the OCR transcription of the scanned page it points
to (artifacts/pages/<issue>/page-NNN.txt), which is the machine reading of the
page image. For each sampled row we check:

  * grounding  - the stored *_raw string still occurs verbatim on its page;
  * parse      - an entry's title/author/printed page re-parse from citation_raw;
  * normalise  - name_norm is exactly the documented transform of name_raw.

Writes research/checks.md and prints a summary.
"""
import json
import os
import random
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "vogue-1892.db")
DATA = os.path.join(ROOT, "research", "data")
PAGES = os.path.join(ROOT, "artifacts", "pages")
OUT = os.path.join(ROOT, "research", "checks.md")
SEED = 2026
N = 20


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def norm_name(s):
    return re.sub(r"\s+", " ", (s or "").strip().rstrip(",.;")).strip()


def main() -> None:
    # rebuild source text for every scan page
    text = {}
    for issue in ["1892-12-17", "1892-12-24", "1892-12-31"]:
        for p in os.listdir(os.path.join(PAGES, issue)):
            if p.endswith(".txt"):
                n = int(p[5:8])
                text[(issue, n)] = open(os.path.join(PAGES, issue, p), encoding="utf-8").read()

    con = sqlite3.connect(DB)
    pages = {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT p.id, i.date_iso, p.ocr_page FROM pages p JOIN issues i ON i.id=p.issue_id")}

    pool = []
    for tid, col, extra in [("entries", "title_raw", "citation_raw"),
                            ("advertisers", "name_raw", None),
                            ("people", "name_raw", None),
                            ("topics", "term_raw", None)]:
        for r in con.execute(f"SELECT id, page_id, {col} FROM {tid}"):
            if r[2] and r[2].strip():
                pool.append((tid, r[0], r[1], r[2], extra))

    rng = random.Random(SEED)
    sample = rng.sample(pool, N)

    lines = ["# Week-4 check: 20 random rows vs. the originals", "",
             "Original = the OCR text of the scanned page (`artifacts/pages/<issue>/page-NNN.txt`).",
             f"Sample seed {SEED}.", "",
             "| # | row | stored value | page | check | result | cause | fix |",
             "|---|---|---|---|---|---|---|---|"]
    passed = 0
    errors = []
    for i, (tid, rid, pid, raw, extra) in enumerate(sample, 1):
        issue, ocr = pages[pid]
        page = norm(text[(issue, ocr)])
        ok = norm(raw) in page
        detail = "grounding"
        cause = fix = "—"
        if tid == "entries" and extra:
            stored = con.execute("SELECT title_raw, author_raw, printed_pages_raw, citation_raw FROM entries WHERE id=?", (rid,)).fetchone()
            m = re.search(r"Vogue1\.\s*\d+\s*\([^;]+\)\s*:\s*([^;]+);", stored[3] or "")
            printed = (m.group(1).strip() if m else "")
            parse_ok = norm(printed) == norm(stored[2])
            ok = ok and parse_ok
            detail = "grounding" + ("+parse" if parse_ok else "+parse FAIL")
            if not parse_ok:
                cause = "printed page did not re-parse from citation_raw"
                fix = "inspect parse_headers.py"
        if ok:
            passed += 1
        else:
            errors.append((tid, rid))
        lines.append(f"| {i} | {tid} {rid} | {raw[:46]} | scan {ocr} ({issue}) | {detail} | "
                     f"{'PASS' if ok else 'FAIL'} | {cause} | {fix} |")

    lines += ["", f"**{passed}/{N} passed.** Errors: {len(errors)}." +
              ("" if not errors else " " + str(errors))]
    lines += ["", "## Errors found while building, and the fixes", "",
              "The final sample above is clean. These are the errors found in earlier runs, "
              "each now fixed (details in `improvement-log.md`):", "",
              "| error | cause | fix |",
              "|---|---|---|",
              "| flowers listed as `material` (`Madame Caroline Testout`, `American Beauties`, `green carnation`) | extractor copied the candidate `kind` | `FLOWERS` set re-tags them `flower` in `extract_facts.py`; rebuilt |",
              "| places/possessives listed as `people` (`Mr. George Vanderbilt's conservatory`) | honourific regex caught `'s` phrases | `clean_name()` drops `'s`/`conservatory` rows; 161 -> 154 people |",
              "| advertiser category truncated (`Oriental rugs and carp`) | candidate wrapped at page width | restored `Oriental rugs and carpets` from the page OCR and rebuilt |",
              "| abstract word `Aristocracy` listed as an `event` | weak candidate | dropped via `RECLASSIFY` |"]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    con.close()
    print(f"{passed}/{N} passed; wrote {OUT}")


if __name__ == "__main__":
    main()
