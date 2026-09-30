---
name: vogue-1892-add-material
description: 往 vogue-1892.db 加入新的《Vogue》期号或新材料。当被要求扩充这个 1892 年档案（再扫一期、再加广告/人物/主题）时，从 vogue-1892 这个 skill 交棒过来。说明完整步骤并逐条执行。
---

# vogue-1892-add-material

这是 **vogue-1892** 这个 skill 的“加料”伙伴。当任务从“回答问题”变成“扩充档案”时，
`vogue-1892/SKILL.md` 会指向这里。

**不变量：绝不原地改 `sources/raw/` 里的原始 PDF；绝不编造广告主、人物、日期或出处；
每条新行都必须带 `source`（能回指扫描页）。**

## 加一期新刊（同一套步骤）

以新增 `Vogue - 1893-01-07.pdf` 为例：

1. **放进原件。** 把 PDF 放到 `sources/raw/`。原件只读，不改。
2. **OCR（PDF → 每页文本 + 页图）。**
   ```bash
   swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
     -target arm64-apple-macosx26.0 -o /tmp/ocr_pdf code/ocr_pdf.swift
   /tmp/ocr_pdf "sources/raw/Vogue - 1893-01-07.pdf" artifacts/pages/1893-01-07 2.0
   ```
3. **解析页面引用头**（标题 / 作者 / 印刷页）。在 `code/parse_headers.py` 的
   `ISSUES` 列表里加上新期号，然后重跑：
   ```bash
   python3 code/parse_headers.py        # -> artifacts/headers.json
   ```
4. **抽取事实候选**（广告主 / 人物 / 主题），每行从它所在的页里逐字复制。得到
   `artifacts/candidates/1893-01-07.json`。
5. **逐字校验候选。** 每个 `*_raw` 必须能在其页的 OCR 文本里找到（大小写与空白归一后
   精确匹配）；对不上的丢弃并记录。这一步保证“字字有据”。
6. **生成整理后的 JSON**（追加，不覆盖旧行）。在 `code/extract_facts.py` 的 `ISSUES`
   里加上新期号，重跑：
   ```bash
   python3 code/extract_facts.py        # -> research/data/*.json（追加新行）
   ```
7. **重建数据库。**
   ```bash
   python3 code/build_db.py             # -> vogue-1892.db
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
