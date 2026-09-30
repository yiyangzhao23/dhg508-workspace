#!/usr/bin/env python3
"""Build data.db (one flat table) from records.json.

Week 3: a *small* database. One table, one row per fact, each row carrying its
own source. Standard-library sqlite3 only.

Usage: python3 build_db.py
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDS = os.path.join(HERE, "records.json")
DB = os.path.join(HERE, "data.db")

COLUMNS = ["id", "date", "event", "place", "people", "source", "note"]


def main() -> None:
    rows = json.load(open(RECORDS, encoding="utf-8"))
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.execute(
        """
        CREATE TABLE records (
            id     INTEGER PRIMARY KEY,
            date   TEXT,
            event  TEXT,
            place  TEXT,
            people TEXT,
            source TEXT,
            note   TEXT
        )
        """
    )
    con.executemany(
        "INSERT INTO records (id, date, event, place, people, source, note) "
        "VALUES (:id, :date, :event, :place, :people, :source, :note)",
        [{c: r.get(c, "") for c in COLUMNS} for r in rows],
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    con.close()
    print(f"wrote {DB} with {n} rows")


if __name__ == "__main__":
    main()
