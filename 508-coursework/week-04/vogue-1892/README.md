# Vogue 1892 —— 一个真正的关系库，和一个渐进式 skill

第四周作业：把上周的小库长成一个**真数据库**（关系型、可核对、可继续生长），并把
**一个 skill** 变成一个**渐进式 skill**（按需加载、随数据与问题扩展）。

材料是三期真实旧刊：**《Vogue》Vol. I, Nos. 1–3（1892-12-17 / 24 / 31）**，共 88 页
扫描图，来自本地 PDF（`sources/raw/`，无文字层，全部由本机 OCR）。

## 数据库 `vogue-1892.db`

**7 张表、6 个外键、575 行。**

```
sources ──< issues ──< pages ──< entries
                                 ├──< advertisers
                                 ├──< people
                                 └──< topics
```

| 表 | 行 | 装什么 |
|---|---|---|
| `sources` | 4 | 每份文献（三期 PDF + 档案元数据） |
| `issues` | 3 | 三期，含原始日期与规范化日期 |
| `pages` | 88 | 每个扫描页：印刷页号、栏目、档案引用头 |
| `entries` | 70 | 页面上的条目：文章/广告/公告，含作者与印刷页 |
| `advertisers` | 98 | 广告主：名称、类别、地址、城市 |
| `people` | 154 | 人物：姓名、身份 |
| `topics` | 158 | 服饰/材料/颜色/场所/事件/花卉 |

- **外键**：`issues.source_id`、`pages.issue_id`、`entries/advertisers/people/topics.page_id`。
- **每行都有 `source`**（`Vogue Vol. I.1 (December 17, 1892), printed p. vii., scan image 7`）
  **与 `note`**（存疑时写明）。
- **规范化与原始并列**：`issues.date_raw`/`date_iso`/`date_basis`；
  `advertisers`、`people` 各有 `name_raw`/`name_norm`。

## 渐进式 skill

`skills/vogue-1892/SKILL.md` 保持简短（库是什么、何时用、如何引用、无答案时怎么办），
细节拆到按需再读的文件：

| 文件 | 内容 |
|---|---|
| `skills/vogue-1892/schema.md` | 每张表的列与关联 |
| `skills/vogue-1892/queries.md` | 常用查询示例（均已实测可跑） |
| `skills/vogue-1892/rules.md` | 日期/名称/出处/语言规则 |
| `skills/add-material/SKILL.md` | 第二个 skill：如何加新材料（由上一个交棒） |

Agent 名叫 **Miss Redding**，得名于《Vogue》1892 年的主编 Mrs. Josephine Redding
（她本人记在 `[people 26]`）。语气克制、专业、逐条给 `[表 id]` 与 `source`。

## 怎么重建

```bash
# 1) 原件 -> 每页 OCR 与页图（需要 Xcode 命令行工具）
swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
  -target arm64-apple-macosx26.0 -o /tmp/ocr_pdf code/ocr_pdf.swift
for d in 1892-12-17 1892-12-24 1892-12-31; do
  /tmp/ocr_pdf "sources/raw/Vogue - $d.pdf" "artifacts/pages/$d" 2.0
done

python3 code/parse_headers.py     # 解析每页的档案引用头 -> artifacts/headers.json
#   （advertisers/people/topics 的候选见 artifacts/candidates/*.json，已逐字校验）
python3 code/extract_facts.py     # -> research/data/*.json（追加式）
python3 code/build_db.py          # -> vogue-1892.db
python3 code/check_db.py          # 抽 20 行回原件核对 -> research/checks.md
```

## 文件

| 文件 | 内容 |
|---|---|
| `vogue-1892.db` | SQLite，7 表 575 行 |
| `code/` | OCR、解析、抽取、建库、核对脚本 |
| `research/data/*.json` | 整理后的行（库只从这里建） |
| `research/method.md` | 完整步骤，加料按同一套走 |
| `research/checks.md` | 20 行抽样核对 |
| `rubric.md` / `test-questions.md` | 评分标准与 12 个实测问题 |
| `improvement-log.md` | 4 条「前/改/后」 |
| `questions.md` | 未决问题 |
| `artifacts/` | 页图与 OCR（大文件，不入 git） |

## 说明

原件 PDF 约 130 MB，放在 `sources/raw/` 但被 git 忽略；页图与 OCR 同理。
`research/data/*.json` 加脚本足以重建数据库。
