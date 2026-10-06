# Method —— 档案怎么建、怎么长

同一套步骤，每次加材料都照跑一遍，只追加、不破坏旧行。

## 0. 来源

九期《Vogue》，共 254 页扫描图：

- 1892：12-17 / 12-24 / 12-31（Vol. I, Nos. 1–3）
- 1893：01-07 / 02-04 / 03-25（Vol. I, Nos. 4 / 8 / 15）
- 1900：07-05 / 07-19（引用头未给卷号）与 08-23（Vol. 16）

PDF 放在 `sources/raw/`，只读。**没有文字层**，全部内容由本机 OCR 得到。
1916 与 1920（法文版）暂不在档案内，见 `questions.md`。

## 1. 渲染 + OCR（PDF → 每页文本与页图）

`code/ocr_pdf.swift`（Apple PDFKit + Vision）：

```bash
swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
  -target arm64-apple-macosx26.0 -o /tmp/ocr_pdf code/ocr_pdf.swift
for d in 1892-12-17 1892-12-24 1892-12-31 1893-01-07 1893-02-04 1893-03-25 \
         1900-07-05 1900-07-19 1900-08-23; do
  /tmp/ocr_pdf "sources/raw/Vogue - $d.pdf" "artifacts/pages/$d" 2.0
done
```

每页输出 `page-NNN.txt`（按上→下、左→右排序）与 `page-NNN.jpg`。页图与 OCR 放在
`artifacts/`（大文件，不入 git）。合并文本存 `sources/processed/<date>-ocr.txt`。

## 2. 解析页面引用头（→ `entries` 与页元数据）

每张扫描页上印有一行档案自己加的引用头；**它的写法随年代变过**，`code/parse_headers.py`
依次匹配三种，把它解析成标题、作者、期号/卷号、印刷页，写 `artifacts/headers.json`：

| 年代 | 形态 |
|---|---|
| 1892–1893 | `'Le Bon Oncle…' Janvier, Thomas. Vogue1. 1 (Dec 17, 1892): 4, 5, 6, 7.;` |
| 1900-07 | `Clippings LUND, ADELAIDE. "Clippings." Vogue, Jul 05, 1900. 458, http://…;` |
| 1900-08 | `A Midsummer… TAYLOR, E. (1900, Aug 23). A midsummer night's dream. Vogue, 16, 118-118. Retrieved from http://…;` |

期号清单读自 `research/data/issues.json`。254 页里 206 页读到引用头；其余 48 页是
续页（`pages.matched = 0`，`section = continuation`）。

## 3. 抽取事实候选

对每期，从页文本里抽取三类候选：**广告主**（含类别/地址/城市）、**人物**（含身份）、
**主题**（garment/material/color/place/event/flower/object）。存
`artifacts/candidates/<date>.json`。

## 4. 逐字校验（关键的一步）

每个候选的 `raw` 必须能在**它自己那一页**的 OCR 文本里逐字找到（空白/大小写归一后精确
匹配）。对不上的行直接丢弃——这一关是「字字有据」的保证。随后人工剔除/改类：
代词所有格（`Mr. George Vanderbilt's conservatory`）不是人物，花朵名（`Madame Caroline
Testout`、`American Beauties`、`green carnation`）的 kind 改为 `flower`，抽象词
`Aristocracy` 丢弃。规则写在 `code/extract_facts.py`。

## 5. 生成整理后的 JSON

`code/extract_facts.py` 把页元数据、条目、校验后的事实写成
`research/data/{pages,entries,advertisers,people,topics}.json`——这五个文件由**累积的
候选**确定性重生成，新期只会新增行、不动旧行。人工修订改
`artifacts/candidates/*.json`；`sources.json` 与 `issues.json` 手工维护。

## 6. 建库

`code/build_db.py` 从 `research/data/*.json` 重建 `vogue.db`：7 张表、6 个外键、
1876 行。每条事实行都算出自己的 `source`（期、印刷页、扫描页），并把原始与规范化名称并列。
`issue_no`/`volume` 缺失时（如 1900-07），`source` 只写「Vogue (July 5, 1900)」，不编造卷期。

## 7. 核对

`code/check_db.py` 固定种子抽样 20 行，逐行回原件（该页 OCR 文本）核对：
- **grounding**：`*_raw` 仍在它那一页；
- **parse**：条目的印刷页能从 `citation_raw` 重新解析出来；
- **normalise**：`name_norm` 正是 `name_raw` 的既定转换。

结果写 `research/checks.md`。最近一次：**20/20 通过**。

## 8. 记录与生长

因答案不好而做的每次改动进 `improvement-log.md`；未决问题进 `questions.md`。加料步骤
加料步骤写在 `skills/vogue/how-to-maintain.md`（由 `skills/vogue/SKILL.md` 这个索引交棒）。

## 已知边界

- OCR 无文字层，分栏页会串读，所以只抽可靠的行，不逐句转正文。
- 引文一律不抽、不编；库内只有可核对的短串（名、标题、词）。
- 页图（`artifacts/pages/*.jpg`）与 OCR 文本不入 git；`research/data/*.json` 与脚本足以重建。
