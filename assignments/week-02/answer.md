# Week 2 — Answer

## Question

When did Peking University (北京大學) first admit women — and what did
"admit" actually mean: being allowed into classes, or being formally enrolled?

## Answer

Peking University opened to women at the start of **1920**, but it did so in two
stages, so the honest answer depends on which "admit" you mean:

- **February–March 1920 — admitted as auditors (旁聽生).** Wang Lan (王蘭)
  began attending in mid-February 1920; Xi Zhen (奚浈) and Zha Xiaoyuan
  (查曉園) joined soon after, and by mid-March six more had entered, nine in
  all. They sat in classes, but were registered only as auditors.
- **Summer/autumn 1920 — formally enrolled.** After the summer entrance
  examination, women were admitted as regular, matriculated students.

So: **classes from February 1920; formal enrolment from the summer of 1920.**
"Opening the door to women" is best dated to early 1920, with full formal
admission following later that year.

## Evidence

**1. 《北京大學日刊》第559號, 11 March 1920, 第2版「本校女生消息」** — a
primary, contemporaneous notice issued *by the university itself*, with a
「女學生一覽表」 listing the women and their course, school and intake month.
Crucially, the table labels them **旁聽生** (auditors) and gives
「到校年月 = 九年二月」 (Feb 1920).
Scan: <https://archive.org/details/beida-rikan-1920.03.11>
(local copy: `projects/pku_coeducation/sources/raw/beida-rikan-1920-03-11-559-p2.jpg`).

*Why reliable:* it is the institution's own document from the same month, not a
later summary. It also settles the "attend vs. enrol" question directly, because
it names the category the women held.

**2. 蔡元培, 〈我在北京大學的經歷〉 (1934)** — the president who made the
decision writes: *"九年，有女學生要求進校，以考期已過，姑錄為旁聽生。及暑假
招考，就正式招收女生。"* ("In year 9 [1920] some women asked to enter; as the
exams had passed they were first taken on as auditors, and at the summer
examination women were formally recruited.")
<https://zh.wikisource.org/wiki/我在北京大學的經歷>

*Why reliable:* a first-person account by the decision-maker. It independently
confirms the two-stage story and matches the 日刊 notice.

**Supporting:** a contemporaneous report in 上海《民國日報》 (3 March 1920)
names 王蘭 (哲學系) and 奚湞 / 查曉園 (英文系) as the first entrants; modern
北大校史館 / 北大新聞網 / 澎湃 accounts agree. Full list in
`projects/pku_coeducation/research/references/references.md`.

## How I did the OCR

- **Source needing OCR:** the scan above. Its text has *not* been converted to
  machine-readable text worth using.
- **Step 1 (LLM API):** skipped — I had no OpenRouter/DeepSeek key, so I could
  not try that route first.
- **Step 2 (PaddleOCR API):** not reached, because step 3 worked.
- **Step 3 (OpenCode vision): worked.** I transcribed the notice directly from
  the page image.

**Useful tricks and problems**

- *The module is printed sideways.* The bottom strip of 第2版 is rotated ~90°.
  Rotating it upright (90° CCW) is what makes it legible at all — the archive's
  own OCR completely missed this.
- *The archive's existing OCR is useless here.* Internet Archive already ships a
  Tesseract OCR of this page; on this sideways, small-type module it is noise.
  A sample is kept at
  `projects/pku_coeducation/sources/processed/beida-rikan-1920-03-11-559-archive-tesseract.txt`.
  Comparing the two is a good demonstration of why a vision model beats
  per-character OCR on this kind of page.
- *Cropping + contrast + a 3–4× upscale* of just the notice gave the best
  results; reading the whole page at once was far worse.
- *A real limitation:* the table's **姓名 column is cut off at the bound edge**
  of the scan, so the names cannot be recovered from this document — only the
  other columns (籍貫 / 年齡 / 經過學校 / 到校年月 / 現在肄業). I recorded the
  readable fields and confirmed the names from the other sources. This is a
  normal archival problem worth flagging rather than papering over.

Full transcription: `projects/pku_coeducation/sources/processed/beida-rikan-1920-03-11-559-p2-ocr.md`.
