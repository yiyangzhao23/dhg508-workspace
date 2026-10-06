#!/usr/bin/env python3
"""Build vogue.db from the curated JSON in research/data/.

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
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "research", "data")
DB = os.path.join(ROOT, "vogue.db")

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
    issue_no   INTEGER,
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
    gender   TEXT,          -- inferred: 'man' / 'woman' / 'unknown' (never printed)
    gender_basis TEXT,      -- what the guess rests on (honorific / role / given name)
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


# ---- gender: inferred (never printed), so every row carries its basis ----
MALE_HON = {"mr", "mister", "sir", "lord", "king", "prince", "duke", "count", "baron",
            "monsieur", "m", "rev", "reverend", "dr", "doctor", "col", "colonel", "capt",
            "captain", "major", "gen", "general", "hon", "esq", "father", "fr", "abbe",
            "pere", "signor", "senor", "herr", "emperor", "tsar", "pope", "cardinal",
            "bishop", "uncle", "brother"}
FEMALE_HON = {"mrs", "miss", "ms", "madam", "madame", "mme", "mlle", "mademoiselle",
              "lady", "queen", "princess", "duchess", "countess", "baroness", "empress",
              "signora", "signorina", "frau", "fraulein", "senora", "senorita", "dame",
              "aunt", "sister", "mother"}
MALE_ROLE = {"actor", "gentleman", "gentlemen", "bridegroom", "husband", "widower",
             "father", "uncle", "brother", "son", "priest", "beau", "sportsman", "groom",
             "king", "prince", "duke", "count", "baron"}
FEMALE_ROLE = {"actress", "gentlewoman", "lady", "ladies", "wife", "widow", "bride",
               "mother", "aunt", "sister", "daughter", "woman", "women", "queen",
               "princess", "duchess", "countess", "baroness", "milliner", "dressmaker",
               "seamstress", "modiste", "couturiere", "danseuse", "raconteuse"}
MALE_NAMES = {"thomas", "john", "charles", "joseph", "james", "edward", "henry", "william",
              "george", "robert", "richard", "arthur", "albert", "frederic", "frank", "walter",
              "harold", "edwin", "alfred", "samuel", "david", "daniel", "michael", "peter",
              "paul", "martin", "patrick", "hugh", "philip", "leo", "oscar", "felix", "hugo",
              "ivan", "carl", "karl", "otto", "hans", "franz", "adam", "alexander", "antoine",
              "auguste", "claude", "edmond", "edouard", "emile", "eugene", "francois", "gaston",
              "guillaume", "henri", "jacques", "jean", "jules", "louis", "lucien", "marcel",
              "maurice", "octave", "pierre", "raymond", "rene", "theodore", "victor", "vincent",
              "carolus", "paulus", "weeden", "vernon", "brander", "edgar", "julien", "beau",
              "andre", "armand", "etienne", "fernand", "gustave", "luc", "marc", "mathieu",
              "nicolas", "pascal", "reginald", "percival", "clarence", "herbert", "cecil",
              "leonard", "horace", "montague", "augustus", "pembroke", "everard"}
FEMALE_NAMES = {"mary", "marie", "frances", "emelie", "toinette", "margot", "therese",
                "elizabeth", "eliza", "anne", "anna", "margaret", "catherine", "katherine",
                "jane", "sarah", "emily", "caroline", "charlotte", "louise", "clara", "alice",
                "edith", "helen", "grace", "rose", "rosa", "agnes", "beatrice", "florence",
                "gertrude", "harriet", "isabel", "isabella", "julia", "laura", "lucy", "martha",
                "nellie", "nora", "olivia", "rebecca", "sophia", "susan", "victoria", "virginia",
                "adelaide", "amelia", "augusta", "bertha", "cornelia", "eleanor", "ethel",
                "evelyn", "ida", "irene", "jeanne", "josephine", "marguerite", "mathilde",
                "nathalie", "pauline", "suzanne", "valentine", "yvonne", "clemence", "hortense",
                "eugenie", "amelie", "celine", "colette", "gabrielle", "henriette", "juliette",
                "odette", "simone", "yvette", "zoe", "corinne", "delphine", "elise", "leonore",
                "mabel", "maud", "millicent", "olive", "ruth", "sybil", "winifred", "blanche"}


def fold(s: str) -> str:
    """Lowercase and strip diacritics, so 'Thérèse' -> 'therese'."""
    return "".join(c for c in unicodedata.normalize("NFKD", s or "")
                   if not unicodedata.combining(c)).lower()


def classify_gender(name_raw: str, role_raw: str):
    """Return (gender, basis). Gender is never printed, so it is always marked inferred."""
    words = re.findall(r"[a-z]+", fold(name_raw))
    role = fold(role_raw)
    for w in words:
        if w in FEMALE_HON:
            return "woman", f'honorific "{w}."'
        if w in MALE_HON:
            return "man", f'honorific "{w}."'
    for kw in sorted(FEMALE_ROLE):
        if re.search(rf"\b{re.escape(kw)}\b", role):
            return "woman", f'role "{kw}"'
    for kw in sorted(MALE_ROLE):
        if re.search(rf"\b{re.escape(kw)}\b", role):
            return "man", f'role "{kw}"'
    for w in words:
        if w in FEMALE_NAMES:
            return "woman", f'given name "{w.capitalize()}"'
        if w in MALE_NAMES:
            return "man", f'given name "{w.capitalize()}"'
    return "unknown", ""


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
        vol, no = it.get("volume") or "", it.get("issue_no")
        if vol and no:
            prefix = f"Vogue Vol. {vol}.{no}"
        elif vol:
            prefix = f"Vogue Vol. {vol}"
        else:
            prefix = "Vogue"
        return f"{prefix} ({it['date_raw']}), printed p. {lab}, scan image {ocr_page}"

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
        gender, basis = classify_gender(p["name_raw"], p.get("role_raw", ""))
        con.execute("INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?)", (
            None, pid, p["name_raw"], norm_name(p["name_raw"]), p["role_raw"],
            gender, basis, source_cite(p["issue"], p["ocr_page"], lab), p.get("note", "")))

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
