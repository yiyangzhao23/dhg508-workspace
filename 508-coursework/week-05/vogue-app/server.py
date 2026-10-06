#!/usr/bin/env python3
"""Ask Miss Redding — a web page, this server, a real model, and the Vogue archive.

    export DEEPSEEK_API_KEY=sk-...        # your key, never in a file
    python3 server.py                      # then open http://localhost:8000
    PORT=8765 python3 server.py            # if 8000 is busy

Standard library only; nothing to install. The database is the Week 4 archive
(../../week-04/vogue/vogue.db, 9 issues 1892–1900, 1876 rows).

This is the app that grows out of the skill: the page sends a question, the
server pulls the matching rows out of the database, and a **real** DeepSeek call
writes the answer. `ask_model()` below is THE ONE SPOT that used to be a fixture:
the Week 5 demo returned the same saved JSON for every photo; here it sends the
retrieved rows to DeepSeek and asks for an answer grounded in them.

API used (from the official docs, https://api-docs.deepseek.com):
    POST https://api.deepseek.com/chat/completions
    Authorization: Bearer $DEEPSEEK_API_KEY
    {"model": "deepseek-flash", "messages": [...], "stream": false}
"""
import json
import os
import re
import sqlite3
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE.parent.parent / "week-04" / "vogue" / "vogue.db"
STATIC = HERE / "static"
PORT = int(os.environ.get("PORT", 8000))

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")

WORD = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")

SYSTEM = (
    "You are Miss Redding, editor of Vogue from 1892 to 1900. "
    "Answer ONLY from the archive records given below; never add facts from memory. "
    "Cite every statement with the row id in square brackets, e.g. [advertisers 16], "
    "and give its source line (issue, printed page, scan image). "
    "If the records do not contain the answer, say so plainly in character and stop — "
    "do not guess. Reply in the language of the question, and keep it short."
)


def connect():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def issues(con):
    return [dict(r) for r in con.execute(
        "SELECT id, date_raw, date_iso, volume, issue_no, page_count FROM issues ORDER BY date_iso")]


def _terms(question):
    return sorted({t.lower() for t in WORD.findall(question)})


def _intent_kinds(ql):
    rules = [
        (("广告", "advertis", "brand", "shop"), "advertisers"),
        (("人物", "谁", "主编", "编辑", "people", "who", "editor"), "people"),
        (("材料", "面料", "布料", "fabric", "material", "textile"), ("topics", "material")),
        (("颜色", "color", "colour"), ("topics", "color")),
        (("服饰", "服装", "衣服", "裙", "garment", "dress", "gown", "fashion"), ("topics", "garment")),
        (("场所", "地点", "城市", "place", "city", "where"), ("topics", "place")),
        (("花卉", "花", "flower", "floral"), ("topics", "flower")),
        (("文章", "标题", "article", "title"), "entries"),
    ]
    kinds = []
    for keys, target in rules:
        if any(k in ql for k in keys):
            kinds.append(target)
    return kinds


def retrieve(con, question, per_term=8, sample=15):
    """Pull the rows the model is allowed to use: keyword matches + intent samples."""
    records, seen = [], set()

    def add(table, rid, label, detail, source):
        key = (table, rid)
        if key in seen or not (label or "").strip():
            return
        seen.add(key)
        records.append({"table": table, "id": rid, "label": label.strip(),
                        "detail": (detail or "").strip(), "source": source or ""})

    for term in _terms(question):
        like = f"%{term}%"
        for r in con.execute("SELECT id,name_raw,category_raw,city_raw,source FROM advertisers "
                             "WHERE lower(name_raw) LIKE ? LIMIT ?", (like, per_term)):
            add("advertisers", r["id"], r["name_raw"], " / ".join(x for x in (r["category_raw"], r["city_raw"]) if x), r["source"])
        for r in con.execute("SELECT id,name_raw,role_raw,source FROM people "
                             "WHERE lower(name_raw) LIKE ? LIMIT ?", (like, per_term)):
            add("people", r["id"], r["name_raw"], r["role_raw"], r["source"])
        for r in con.execute("SELECT id,term_raw,kind,source FROM topics "
                             "WHERE lower(term_raw) LIKE ? LIMIT ?", (like, per_term)):
            add("topics", r["id"], r["term_raw"], r["kind"], r["source"])
        for r in con.execute("SELECT id,title_raw,kind,author_raw,printed_pages_raw,source FROM entries "
                             "WHERE lower(title_raw) LIKE ? LIMIT ?", (like, per_term)):
            add("entries", r["id"], r["title_raw"], " / ".join(x for x in (r["kind"], r["author_raw"], r["printed_pages_raw"]) if x), r["source"])

    # when the question names a category (often in Chinese), add a small sample
    for target in _intent_kinds(question.lower()):
        if isinstance(target, tuple):
            table, kind = target
            for r in con.execute("SELECT id,term_raw,kind,source FROM topics WHERE kind=? "
                                 "ORDER BY term_raw LIMIT ?", (kind, sample)):
                add("topics", r["id"], r["term_raw"], r["kind"], r["source"])
        elif target == "advertisers":
            for r in con.execute("SELECT id,name_raw,category_raw,city_raw,source FROM advertisers "
                                 "ORDER BY id LIMIT ?", (sample,)):
                add("advertisers", r["id"], r["name_raw"], " / ".join(x for x in (r["category_raw"], r["city_raw"]) if x), r["source"])
        elif target == "people":
            for r in con.execute("SELECT id,name_raw,role_raw,source FROM people ORDER BY id LIMIT ?", (sample,)):
                add("people", r["id"], r["name_raw"], r["role_raw"], r["source"])
        elif target == "entries":
            for r in con.execute("SELECT id,title_raw,kind,author_raw,printed_pages_raw,source FROM entries "
                                 "ORDER BY id LIMIT ?", (sample,)):
                add("entries", r["id"], r["title_raw"], " / ".join(x for x in (r["kind"], r["author_raw"], r["printed_pages_raw"]) if x), r["source"])

    return records


def build_messages(question, iss, records):
    lines = ["Issues in the archive (id | date | volume.issue | pages):"]
    for it in iss:
        vol = f"{it['volume']}.{it['issue_no']}" if it["volume"] and it["issue_no"] else (it["volume"] or "—")
        lines.append(f"  issues {it['id']} | {it['date_raw']} | {vol} | {it['page_count']} pages")
    lines.append("")
    lines.append("Archive records you may use (table id | value | detail | source):")
    if records:
        for r in records:
            lines.append(f"  {r['table']} {r['id']} | {r['label']} | {r['detail']} | {r['source']}")
    else:
        lines.append("  (none matched — say the archive has no matching record)")
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Question: {question}\n\n" + "\n".join(lines)},
    ]


def ask_model(messages):
    """THE ONE SPOT THAT WAS A FIXTURE.

    The Week 5 demo's ask_model() returned fixtures/model-response.json for every
    photo. This one sends the retrieved rows to DeepSeek and returns the answer.
    """
    payload = json.dumps({"model": MODEL, "messages": messages,
                          "stream": False, "temperature": 0.2}).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=payload, method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"], data.get("model", MODEL)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body: bytes, kind: str):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
        self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/ask":
            return self._send(404, b"not found", "text/plain")
        try:
            length = int(self.headers.get("Content-Length", 0))
            question = (json.loads(self.rfile.read(length) or b"{}").get("question") or "").strip()
        except (ValueError, json.JSONDecodeError):
            return self._send(400, json.dumps({"error": "bad request"}).encode(), "application/json")

        if not question:
            return self._send(400, json.dumps({"error": "empty question"}).encode(), "application/json")

        try:
            con = connect()
        except sqlite3.OperationalError as exc:
            return self._send(500, json.dumps({"error": f"database not found: {DB} ({exc})"}).encode(), "application/json")

        iss = issues(con)
        records = retrieve(con, question)
        con.close()

        answer, model_used, error = "", MODEL, None
        if not API_KEY:
            error = "DEEPSEEK_API_KEY is not set — showing the retrieved records only."
        else:
            try:
                answer, model_used = ask_model(build_messages(question, iss, records))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:300]
                error = f"DeepSeek API error {exc.code}: {detail}"
            except Exception as exc:  # network, timeout, malformed response
                error = f"DeepSeek call failed: {exc}"

        body = json.dumps({"answer": answer, "model": model_used, "error": error,
                           "records": records, "issues": iss}, ensure_ascii=False)
        self._send(200, body.encode("utf-8"), "application/json; charset=utf-8")

    def log_message(self, fmt, *args):
        print("  " + fmt % args)


if __name__ == "__main__":
    if not DB.is_file():
        raise SystemExit(f"database not found: {DB}")
    print(f"Open http://localhost:{PORT}   (Ctrl+C to stop)")
    if not API_KEY:
        print("  note: DEEPSEEK_API_KEY is not set; /api/ask will return records without a model answer")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
