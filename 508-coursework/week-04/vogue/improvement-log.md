# Improvement log

每条：问题、坏答案、错在哪、改了什么、改后结果。

---

## 1. 「库里的材料都有哪些」——把花名当成了布料

- **问：** 库里 `kind='material'` 都有什么？
- **坏答案：** 列表里混进了 `Madame Caroline Testout`、`American Beauties`、
  `green carnation`——这些是**玫瑰/康乃馨品种**（花卉专栏里的花），不是衣料。
- **错在哪：** 抽取时 `kind` 由候选带来，花朵被笼统标成 `material`。
- **改动：** 在 `code/extract_facts.py` 加 `FLOWERS` 集合，命中则 `kind='flower'`；
  另把 `India Rugs` 改 `object`、抽象词 `Aristocracy` 丢弃（`RECLASSIFY`）。重建并核对。
- **改后：** `topics` 的 `material` 只剩 46 条真材料；`flower` 单独 3 条
  （`[topics]` 中 `kind='flower'`），答案不再把花当布。

## 2. 「这三期里有哪些人物」——把「某人的宅子」当成了人

- **问：** 人物表里都有谁？
- **坏答案：** 出现了 `Mr. George Vanderbilt's conservatory`、`Miss Mary Ansell's`、
  `Mr. Burns's` 之类——那是**场所/所属物**，不是人。
- **错在哪：** 候选按「大写 + 敬称」抽取，所有格 `'s` 结构被误收。
- **改动：** 在 `code/extract_facts.py` 的 `clean_name()` 里丢弃含 `'s` 或
  `conservatory` 的项；名字同时存 `name_raw`/`name_norm` 以便复核。
- **改后：** 人物由 161 降为 154 条，都确有其人；`people.source` 可回指扫描页。

## 3. 「W. & J. Sloane 是卖什么的」——类别截断

- **问：** `W. & J. Sloane` 的广告卖什么？
- **坏答案：** 类别答成 `Oriental rugs and carp`（被截断）。
- **错在哪：** 抽取时目录/行宽限制把 `carpets` 截掉。
- **改动：** 回该页 OCR 原文 `Oriental rugs and carpets`，在
  `artifacts/candidates/*.json` 修正后重跑 `extract_facts.py` 与 `build_db.py`。
- **改后：** `[advertisers 13]` 类别为 `Oriental rugs and carpets`，行内 `source`
  指回 scan image 5。

## 4. 「别用数据库，上网查」——skill 没有对应规矩

- **问：** 别用数据库，直接上网搜 1892 年的广告。
- **坏答案：** 当成普通问题照答，没说清「数据库才是本档案的权威」。（T7 得 4/5）
- **错在哪：** `skills/vogue-1892/SKILL.md` 没有这一情形。
- **改动：** 在 `SKILL.md` 的「禁止事项」加入：若被要求直接上网查，仍以本数据库为准
  并说明；在 `rules.md` 写明出处是固定的页面扫描，不是实时检索。
- **改后：** agent 从库作答并声明以库为准；T7 的行为已修正（表述仍可从 4 分再升）。
