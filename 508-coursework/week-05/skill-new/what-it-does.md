# 它做什么 —— 如何从数据库回答问题

本 skill 的唯一数据源是项目根目录下的 **`vogue.db`**，用 Python 的 `sqlite3` 读取。
这个文件讲「怎么答」；能不能答、会不会算错见 `principles.md`。

## 库里有什么

9 期《Vogue》（1892–1900）、254 个扫描页，7 张表、共 1876 行：

| 表 | 行 | 装什么 |
|---|---|---|
| `sources` | 10 | 每份文献 |
| `issues` | 9 | 九期：日期、卷号/期号 |
| `pages` | 254 | 每个扫描页：印刷页号、栏目、档案引用头 |
| `entries` | 206 | 页面上的条目（文章 / 广告 / 公告） |
| `advertisers` | 264 | 广告主 |
| `people` | 560 | 人物 |
| `topics` | 573 | 服饰 / 材料 / 颜色 / 场所 / 事件 |

覆盖：1892-12-17/24/31、1893-01-07/02-04/03-25、1900-07-05/07-19/08-23。
列与关联见 `schema.md`；每条事实行都带 `source`（期、印刷页、扫描页）与 `note`。

## 怎么答（步骤）

1. **把问题落到表上**：广告主 → `advertisers`；人物 → `people`；服饰/材料/颜色/场所 →
   `topics`；文章与广告条目 → `entries`；日期与卷期 → `issues`。
2. **需要就 join**：`advertisers`/`people`/`topics` → `pages` → `issues`。
3. **每条都给 `[表 id]` 与 `source`**，不只报期号。查询示例（均可跑）见 `queries.md`。
4. **用提问的语言作答**。

## 引用与规范化规则

- **出处**：形如 `Vogue Vol. I.1 (December 17, 1892), printed p. vii., scan image 7`；
  1900-07 未给卷号时只写 `Vogue (July 5, 1900), …`。引用时 `id` 与 `source` 一起给，例如
  `Park & Tilford 的香水广告 [advertisers 16] —— Vogue Vol. I.1 (Dec 17, 1892), printed p. vii., scan image 7`。
- **日期**：`date_raw` 印出来的样子（`December 17, 1892`）；`date_iso` 机器形式（`1892-12-17`，
  仅把英文月日年照抄成 ISO，不推断）；`date_basis` 写明来源（报头或引用头）。期号 ≠ 日期。
- **名称**：`*_raw` 印刷原样（含 OCR 错字）；`*_norm` 只做「去行末标点、并空白」，
  **不改拼写 / 大小写 / 缩写**（`PARK AND TILFORD,` → `PARK AND TILFORD`）。
- **条目标题**：取自扫描页上的**档案引用头**，整行存进 `citation_raw`。引用头有三种历史写法
  （见 `research/method.md`）；1900 的 `title_raw` 是档案显示行，未逐字校对，以 `citation_raw` 为准。
- **语言**：用提问语言；引用 `*_raw` 照抄，不翻译、不改错字，需要时括号给中文意译并注明。

## 边界

OCR 无文字层、分栏页会串读，所以库里只有**可核对的短串**（广告主名、人名、标题、主题词），
不转正文、不给引语。存疑写在 `note`。详见 `research/method.md` 的「已知边界」。
