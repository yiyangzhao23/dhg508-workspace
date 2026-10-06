# Vogue 档案 —— 一个关系库，和一个渐进式 skill

第四周作业把上周的小库长成一个**真数据库**（关系型、可核对、可继续生长），并把一个
skill 变成**渐进式 skill**（按需加载、随数据与问题扩展）。第五周继续**扩充档案**：在原有
1892 三期之外加入 1893 与 1900 的期号，并把解析器改成**数据驱动**、支持这份档案多年
沿用的**多种引用头格式**。

材料现在是 **9 期真实旧刊、254 个扫描页**，全部来自本地 PDF（`sources/raw/`，无文字层，
由本机 Apple Vision OCR）：

| 年份 | 期号 | 卷 / 期号 | 扫描页 |
|---|---|---|---|
| 1892 | 12-17 / 12-24 / 12-31 | Vol. I, Nos. 1–3 | 88 |
| 1893 | 01-07 / 02-04 / 03-25 | Vol. I, Nos. 4 / 8 / 15 | 94 |
| 1900 | 07-05 / 07-19 | 引用头未给卷号 | 48 |
| 1900 | 08-23 | Vol. 16 | 24 |

## 数据库 `vogue.db`

**7 张表、6 个外键、1876 行。**

```
sources ──< issues ──< pages ──< entries
                                 ├──< advertisers
                                 ├──< people
                                 └──< topics
```

| 表 | 行 | 装什么 |
|---|---|---|
| `sources` | 10 | 每份文献（9 期 PDF + 档案元数据） |
| `issues` | 9 | 九期，含原始日期与规范化日期 |
| `pages` | 254 | 每个扫描页：印刷页号、栏目、档案引用头 |
| `entries` | 206 | 页面上的条目：文章/广告/公告，含作者与印刷页 |
| `advertisers` | 264 | 广告主：名称、类别、地址、城市 |
| `people` | 560 | 人物：姓名、身份、性别（推断） |
| `topics` | 573 | 服饰/材料/颜色/场所/事件/花卉 |

- **外键**：`issues.source_id`、`pages.issue_id`、`entries/advertisers/people/topics.page_id`。
- **每行都有 `source`**（`Vogue Vol. I.1 (December 17, 1892), printed p. vii., scan image 7`）
  **与 `note`**（存疑时写明）。
- **规范化与原始并列**：`issues.date_raw`/`date_iso`/`date_basis`；
  `advertisers`、`people` 各有 `name_raw`/`name_norm`。
- `issues.issue_no` 可为空：1900 年 7 月的 ProQuest 引用头不给卷号/期号，如实留空，
  出处里也不编造。

## 三种档案引用头（数据驱动解析）

扫描页顶端的档案引用头随年代变了写法，`code/parse_headers.py` 依次匹配三种，全部取自
OCR 原文：

| 年代 | 形态 |
|---|---|
| 1892–1893 | `'Le Bon Oncle…' Janvier, Thomas. Vogue1. 1 (Dec 17, 1892): 4, 5, 6, 7.;` |
| 1900-07 | `Clippings LUND, ADELAIDE. "Clippings." Vogue, Jul 05, 1900. 458, http://…;` |
| 1900-08 | `A Midsummer… TAYLOR, E. (1900, Aug 23). A midsummer night's dream. Vogue, 16, 118-118. Retrieved from http://…;` |

期号清单读自 `research/data/issues.json`——往那里加一行，解析与建库都会自动带上它。

## 渐进式 skill

按第五周要求，skill 重构成**一个索引 + 三类文件**，每个文件一件事、互相指路、不重复：

| 文件 | 内容 |
|---|---|
| `skills/vogue/SKILL.md` | **索引**：哪件事读哪个文件（很短） |
| `skills/vogue/what-it-does.md` | **它做什么**：如何从数据库回答问题、怎么引 |
| `skills/vogue/how-to-maintain.md` | **怎么维护**：逐步加入新期号 / 新材料 |
| `skills/vogue/principles.md` | **原则**：始终成立的几条规矩 |
| `skills/vogue/schema.md` | 细节：每张表的列与关联（由 what-it-does 指到） |
| `skills/vogue/queries.md` | 细节：常用查询示例（均可跑，由 what-it-does 指到） |

Agent 名叫 **Miss Redding**，得名于《Vogue》1892 年的主编 Mrs. Josephine Redding
（她本人记在 `[people 26]`）。语气克制、专业、逐条给 `[表 id]` 与 `source`。

## 怎么重建

```bash
# 1) 原件 -> 每页 OCR 与页图（需要 Xcode 命令行工具）
swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
  -target arm64-apple-macosx26.0 -o /tmp/ocr_pdf code/ocr_pdf.swift
for d in 1892-12-17 1892-12-24 1892-12-31 1893-01-07 1893-02-04 1893-03-25 \
         1900-07-05 1900-07-19 1900-08-23; do
  /tmp/ocr_pdf "sources/raw/Vogue - $d.pdf" "artifacts/pages/$d" 2.0
done

python3 code/parse_headers.py     # 解析每页的档案引用头 -> artifacts/headers.json
#   （advertisers/people/topics 的候选见 artifacts/candidates/*.json，已逐字校验）
python3 code/extract_facts.py     # -> research/data/*.json（追加式）
python3 code/build_db.py          # -> vogue.db
python3 code/check_db.py          # 抽 20 行回原件核对 -> research/checks.md
```

## 文件

| 文件 | 内容 |
|---|---|
| `vogue.db` | SQLite，7 表 1876 行 |
| `code/` | OCR、解析、抽取、建库、核对脚本 |
| `research/data/*.json` | 整理后的行（库只从这里建） |
| `research/method.md` | 完整步骤，加料按同一套走 |
| `research/checks.md` | 20 行抽样核对 |
| `rubric.md` / `test-questions.md` | 评分标准与 12 个实测问题 |
| `improvement-log.md` | 「前/改/后」记录 |
| `questions.md` | 未决问题 |
| `artifacts/` | 页图与 OCR（大文件，不入 git） |

## 说明

- 原件 PDF 放在 `sources/raw/` 但被 git 忽略；页图与 OCR 同理。
  `research/data/*.json` 加脚本足以重建数据库。
- `sources/raw/` 里 1893/1900 六期是指向仓库内 `508-coursework/vogue/` 的软链。
- **暂未纳入**：1916（每期约 150 页，规模过大）与 1920 的**法文版《Vogue》Paris**
  （扫描无档案引用头，且非英文）。见 `questions.md`。
