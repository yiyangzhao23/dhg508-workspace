#!/usr/bin/env python3
"""Build vogue-1892.db from the curated JSON in research/data/.

Seven tables, six foreign keys:

    sources ──< issues ──< pages ──< entries
                                     ├──< advertisers
                                     ├──< people
                                     └──< topics

Every fact row (entries/advertisers/people/topics) carries its own `source`
(document + printed page + scan page) and a `note` for anything uncertain, and
normalised values sit beside the original wording (`*_raw` / `*_norm`).

Usage: python3 code/build_db.py
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "research", "data")
DB = os.path.join(ROOT, "vogue-1892.db")

TABLES = ["sources", "issues", "pages", "entries", "advertisers", "people", "topics"]

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
    id          INTEGER PRIMARY KEY,
    source_key  TEXT UNIQUE NOT NULL,
    publication TEXT NOT NULL,
    kind        TEXT,
    label       TEXT,
    filename    TEXT,
    url         TEXT,
    note        TEXT
);

CREATE TABLE issues (
    id         INTEGER PRIMARY KEY,
    issue_no   INTEGER NOT NULL,
    date_raw   TEXT NOT NULL,
    date_iso   TEXT NOT NULL,
    date_basis TEXT,
    volume     TEXT,
    page_count INTEGER,
    source_id  INTEGER NOT NULL REFERENCES sources(id),
    note       TEXT
);

CREATE TABLE pages (
    id            INTEGER PRIMARY KEY,
    issue_id      INTEGER NOT NULL REFERENCES issues(id),
    ocr_page      INTEGER NOT NULL,
    printed_label TEXT,
    section       TEXT,
    header_kind   TEXT,
    header_title  TEXT,
    header_author TEXT,
    header_company TEXT,
    matched       INTEGER,
    chars         INTEGER,
    note          TEXT
);

CREATE TABLE entries (
    id                INTEGER PRIMARY KEY,
    page_id           INTEGER NOT NULL REFERENCES pages(id),
    kind              TEXT,
    title_raw         TEXT,
    author_raw        TEXT,
    company_raw       TEXT,
    printed_pages_raw TEXT,
    citation_raw      TEXT,
    source            TEXT,
    note              TEXT
);

CREATE TABLE advertisers (
    id           INTEGER PRIMARY KEY,
    page_id      INTEGER NOT NULL REFERENCES pages(id),
    name_raw     TEXT NOT NULL,
    name_norm    TEXT,
    category_raw TEXT,
    address_raw  TEXT,
    city_raw     TEXT,
    source       TEXT,
    note         TEXT
);

CREATE TABLE people (
    id       INTEGER PRIMARY KEY,
    page_id  INTEGER NOT NULL REFERENCES pages(id),
    name_raw TEXT NOT NULL,
    name_norm TEXT,
    role_raw TEXT,
    source   TEXT,
    note     TEXT
);

CREATE TABLE topics (
    id       INTEGER PRIMARY KEY,
    page_id  INTEGER NOT NULL REFERENCES pages(id),
    term_raw TEXT NOT NULL,
    kind     TEXT,
    source   TEXT,
    note     TEXT
);

CREATE INDEX idx_pages_issue ON pages(issue_id);
CREATE INDEX idx_entries_page ON entries(page_id);
CREATE INDEX idx_advertisers_page ON advertisers(page_id);
CREATE INDEX idx_people_page ON people(page_id);
CREATE INDEX idx_topics_page ON topics(page_id);
"""


def norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().rstrip(",.;")).strip()


def load(name):
    with open(os.path.join(DATA, name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    sources = load("sources")
    issues = load("issues")
    pages = load("pages")
    entries = load("entries")
    advertisers = load("advertisers")
    people = load("people")
    topics = load("topics")

    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    src_id = {}
    for i, s in enumerate(sources, 1):
        src_id[s["source_key"]] = i
        con.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)", (
            i, s["source_key"], s["publication"], s.get("kind", ""), s.get("label", ""),
            s.get("filename", ""), s.get("url", ""), s.get("note", "")))

    issue_id = {}
    for i, it in enumerate(issues, 1):
        issue_id[it["date_iso"]] = i
        con.execute("INSERT INTO issues VALUES (?,?,?,?,?,?,?,?,?)", (
            i, it["issue_no"], it["date_raw"], it["date_iso"], it.get("date_basis", ""),
            it.get("volume", ""), it.get("page_count"), src_id[it["source_key"]], it.get("note", "")))

    page_id = {}
    issue_meta = {it["date_iso"]: it for it in issues}
    for p in pages:
        page_id[(p["issue"], p["ocr_page"])] = p["id"]
        con.execute("INSERT INTO pages VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            p["id"], issue_id[p["issue"]], p["ocr_page"], p["printed_label"], p["section"],
            p["header_kind"], p["header_title"], p["header_author"], p["header_company"],
            1 if p["matched"] else 0, p["chars"], p["note"]))

    def source_cite(issue, ocr_page, printed_label):
        it = issue_meta[issue]
        lab = printed_label or "—"
        return f"Vogue Vol. {it['volume']}.{it['issue_no']} ({it['date_raw']}), printed p. {lab}, scan image {ocr_page}"

    for e in entries:
        pid = page_id[(e["issue"], e["ocr_page"])]
        lab = next(p["printed_label"] for p in pages if p["id"] == pid)
        con.execute("INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)", (
            None, pid, e["kind"], e["title_raw"], e["author_raw"], e["company_raw"],
            e["printed_pages_raw"], e["citation_raw"],
            source_cite(e["issue"], e["ocr_page"], lab), e.get("note", "")))

    for a in advertisers:
        pid = page_id[(a["issue"], a["ocr_page"])]
        lab = next(p["printed_label"] for p in pages if p["id"] == pid)
        con.execute("INSERT INTO advertisers VALUES (?,?,?,?,?,?,?,?,?)", (
            None, pid, a["name_raw"], norm_name(a["name_raw"]), a["category_raw"],
            a["address_raw"], a["city_raw"], source_cite(a["issue"], a["ocr_page"], lab), a.get("note", "")))

    for p in people:
        pid = page_id[(p["issue"], p["ocr_page"])]
        lab = next(x["printed_label"] for x in pages if x["id"] == pid)
        con.execute("INSERT INTO people VALUES (?,?,?,?,?,?,?)", (
            None, pid, p["name_raw"], norm_name(p["name_raw"]), p["role_raw"],
            source_cite(p["issue"], p["ocr_page"], lab), p.get("note", "")))

    for t in topics:
        pid = page_id[(t["issue"], t["ocr_page"])]
        lab = next(x["printed_label"] for x in pages if x["id"] == pid)
        con.execute("INSERT INTO topics VALUES (?,?,?,?,?,?)", (
            None, pid, t["term_raw"], t["kind"], source_cite(t["issue"], t["ocr_page"], lab), t.get("note", "")))

    con.commit()
    print(f"wrote {DB}")
    for t in TABLES:
        print(f"  {t:12} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>4} rows")
    total = con.execute("SELECT " + "+".join(f"(SELECT COUNT(*) FROM {t})" for t in TABLES)).fetchone()[0]
    print(f"  {'TOTAL':12} {total:>4} rows")
    con.close()


if __name__ == "__main__":
    main()
