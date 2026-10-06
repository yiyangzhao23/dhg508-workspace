# 怎么维护 —— 往档案里加材料

任务从「回答问题」变成「扩充档案」时，从 `SKILL.md` 交棒到这里。同一套步骤，
每次加材料都照跑一遍，只追加、不破坏旧行。

**不变量：绝不原地改 `sources/raw/` 里的原始 PDF；绝不编造广告主、人物、日期或出处；
每条新行都必须带 `source`（能回指扫描页）。**

## 加一期新刊（完整步骤）

以新增 `Vogue - 1893-01-14.pdf` 为例：

1. **放进原件。** 把 PDF 放到 `sources/raw/`（原件只读；大文件可软链到仓库内的
   `508-coursework/vogue/`，因为 `sources/raw/` 被 git 忽略）。在 `research/data/sources.json`
   与 `issues.json` 里各加一行（期号、日期、卷号/期号——没有就留空并在 `note` 说明）。
2. **OCR（PDF → 每页文本 + 页图）。**
   ```bash
   swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
     -target arm64-apple-macosx26.0 -o /tmp/ocr_pdf code/ocr_pdf.swift
   /tmp/ocr_pdf "sources/raw/Vogue - 1893-01-14.pdf" artifacts/pages/1893-01-14 2.0
   ```
3. **解析页面引用头。** 期号清单读自 `research/data/issues.json`，**无需改代码**；
   `parse_headers.py` 会依次匹配三种引用头格式（1892–93 的 `Vogue1.`、
   1900-07 的 `Vogue, Mon DD, YYYY.`、1900-08 的 `(YYYY, Mon D). … Retrieved from`）。
   遇到全新格式，就在 `code/parse_headers.py` 里加一条正则：
   ```bash
   python3 code/parse_headers.py        # -> artifacts/headers.json
   ```
4. **抽取事实候选**（广告主 / 人物 / 主题），每行从它所在的页里逐字复制，写
   `artifacts/candidates/<日期>.json`。
5. **逐字校验候选。** 每个 `*_raw` 必须能在其页的 OCR 文本里找到（大小写与空白归一后
   精确匹配）；对不上的丢弃并记录。这一步保证「字字有据」。
6. **生成整理后的 JSON**（追加，不覆盖旧行）。同样读 `issues.json`，**无需改代码**：
   ```bash
   python3 code/extract_facts.py        # -> research/data/*.json（追加新行）
   ```
7. **重建数据库。**
   ```bash
   python3 code/build_db.py             # -> vogue.db
   ```
8. **核对。** 重新抽样 20 行与原件比对：
   ```bash
   python3 code/check_db.py             # -> research/checks.md
   ```
9. **记录。** 改过规则或结构，就往 `improvement-log.md` 加一条；未决问题进 `questions.md`。

## 只加零散材料（不整期）

直接往 `research/data/` 下对应文件追加一行，再跑第 6–8 步：

- 新广告主 → `advertisers.json`（`name_raw` 必填，可留 `category_raw`/`address_raw`/`city_raw`）。
- 新人物 → `people.json`。
- 新主题 → `topics.json`（`kind` ∈ garment/material/color/place/event/flower/object）。
- 每行都要有 `issue` 与 `ocr_page`，用来找回扫描页写出 `source`。

## 结构改动

只要**加列/加表**、不改旧列名，旧行不会坏。改表结构后：

```bash
python3 code/build_db.py && python3 code/check_db.py
```

并在 `improvement-log.md` 记一条（问题 → 改动 → 改后结果）。
