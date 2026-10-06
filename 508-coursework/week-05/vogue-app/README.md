# Ask Miss Redding — a Vogue-archive app

A web page, a small Python server, a **real** model, and the Week 4 database.
You type a question about the 1892–1900 *Vogue* archive; the server pulls the
matching rows out of `vogue.db`; a live DeepSeek model writes the answer with
`[table id]` citations and source lines; the page shows both.

```sh
export DEEPSEEK_API_KEY=sk-...     # your key — kept in the environment, never in a file
python3 server.py                  # then open http://localhost:8000
PORT=8765 python3 server.py        # if 8000 is already in use
```

Python standard library only — nothing to install (`pip` not needed).
The database is read read-only from `../../week-04/vogue/vogue.db`
(9 issues, 254 scanned pages, 1876 rows).

| File | What it does |
|---|---|
| `static/index.html` | the page: ask a question, read the answer, see the rows behind it (plain HTML + JS) |
| `server.py` | the server: serves the page, receives the question at `POST /api/ask`, retrieves rows, calls DeepSeek |

## Where the fixture was

The Week 5 demo's `ask_model()` returned the same saved JSON for every photo
(`fixtures/model-response.json`) — it looked clever but never called a model.
Here the demo's one fixture spot is replaced by a **real call**:

`server.py` → `ask_model(messages)` → `POST https://api.deepseek.com/chat/completions`
(`Authorization: Bearer $DEEPSEEK_API_KEY`, `model: deepseek-flash`, `stream: false`),
per the official docs at <https://api-docs.deepseek.com>. The rest of the shape is
the demo's: page → server → model → database.

## What the users do, and what they get back

- **Do:** ask a question (Chinese or English), e.g. “Park & Tilford 登过什么广告？”,
  “1893 年出现过哪些材料？”, “谁主编了 Vogue？”.
- **Get back:** a short, in-character answer that cites `[table id]` and a `source`
  line, plus the full list of archive rows that were retrieved and used — so every
  claim can be traced back to a scanned page.

If `DEEPSEEK_API_KEY` is not set, the page still shows the retrieved records and a
note explaining that no model answer was produced.

## Pictures with the answer

Every row knows the scanned page it came from, and those pages are the images under
`../../week-04/vogue/artifacts/pages/`. The server serves them at
`/pages/<issue>/page-NNN.jpg`; the page shows the pages behind the answer as
thumbnails (click to open the full scan), and each `[table id]` citation links to
its page. The images are large local files (git-ignored); without them the answer
still works, just without pictures.

## How the answer stays grounded

1. `retrieve()` matches the question's words against `advertisers` / `people` /
   `topics` / `entries`, and adds category samples when the question names one
   (广告 / 人物 / 材料 / 服饰 / 花卉 …). The issue list is always included.
2. The system prompt makes the model answer **only** from those records, cite each
   fact, and say so when the archive has nothing — the same rules as the skill.
3. The page prints the answer next to the exact rows, so a wrong claim is visible.
