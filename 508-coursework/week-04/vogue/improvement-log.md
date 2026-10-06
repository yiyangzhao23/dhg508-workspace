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
- **错在哪：** `skills/vogue/SKILL.md` 没有这一情形。
- **改动：** 在 `SKILL.md` 的「禁止事项」加入：若被要求直接上网查，仍以本数据库为准
  并说明；在该 skill 的规矩里写明出处是固定的页面扫描，不是实时检索（文件现名
  `skills/vogue/principles.md`）。
- **改后：** agent 从库作答并声明以库为准；T7 的行为已修正（表述仍可从 4 分再升）。

## 5. 扩充档案——库从 1892「三期」长到 1892–1900「九期」

- **问题：** 原库只为 1892 年 12 月三期硬编码。加入 1893 与 1900 的期号后，
  `parse_headers.py` 只认 `Vogue1.` 一种引用头，1900 的两套 ProQuest 写法全部漏掉；
  `extract_facts.py`、`check_db.py` 的 `ISSUES` 也写死了三期。
- **改动：**
  1. 改名：项目、库、skill 由 `vogue-1892` 统一为 `vogue`。
  2. `parse_headers.py` 改成**数据驱动**（期号读 `research/data/issues.json`）并依次匹配
     三种引用头：1892–93 的 `Vogue1.`、1900-07 的 `Vogue, Mon DD, YYYY. page,`、
     1900-08 的 `(YYYY, Mon D). Title. Vogue, vol, pages. Retrieved from`。
  3. `extract_facts.py` / `check_db.py` 同样读 `issues.json`；核对时的「印刷页重解析」
     也支持三种格式。
  4. 1900-07 引用头不给卷号/期号：`issues.issue_no` 改为可空，`source` 相应只写日期。
  5. 新增 6 期的 OCR、引用头解析与广告主/人物/主题候选；候选逐字回页校验后全部通过。
- **改后：** 库由 **7 表 575 行 → 1876 行**（`pages` 254、`entries` 206、`advertisers` 264、
  `people` 560、`topics` 573）；`check_db.py` 仍 **20/20 通过**。1916 与 1920（法文版）
  未纳入，理由记在 `questions.md`。

## 6. skill 重构——从「技能 + 附带文件」到「索引 + 三类文件」

- **背景：** 第四周的 `SKILL.md` 既当说明又当索引，回答规则、维护步骤、原则混在一起；
  另外还有一个独立的 `add-material` skill。第五周要求改成**一个短索引 + 三类文件**
  （它做什么 / 怎么维护 / 原则），每个文件一件事、互相指路、不重复。
- **改动：**
  1. `skills/vogue/SKILL.md` 缩成**纯索引**（该读哪个文件 + 一句话规矩）。
  2. 新增 `what-it-does.md`（怎么查、怎么引、怎么表述）、`how-to-maintain.md`
     （逐步加料）、`principles.md`（始终成立的几条规矩）。
  3. 原 `rules.md` 的规范化/引用规则并入 `what-it-does.md`；独立的 `add-material` skill
     并入 `how-to-maintain.md`，去掉重复的第二份 skill。
  4. `schema.md`、`queries.md` 作为 `what-it-does.md` 的细节保留。
- **改后：** `skills/vogue/` 下 = 1 个索引 + 3 类文件 + 2 个细节文件；README、`method.md`、
  `test-questions.md` 的指向同步更新，无悬空引用。

## 7. 人物按性别分类 —— `people.gender`（推断值）

- **需求：** 把库中人物分成男人和女人。
- **难点：** 性别从不印在报上，只能**推断**；必须与「原文事实」区分开，不能假装是印出来的。
- **改动：** 在 `code/build_db.py` 的 `people` 表加两列 `gender`（`man`/`woman`/`unknown`）与
  `gender_basis`（推断依据）。推断按优先级：**称谓**（Mr./Mrs./Miss/Lady/Duchess…，含德
  Herr、法 Mme 等）→ **身份词**（actress/bridegroom/wife/gentleman…）→ **名字**（内置英法常见
  男女名表，先折叠变音符号，`Thérèse`→`therese`）。
- **改后：** 560 人中 **man 175、woman 210、unknown 175**；依据分布：称谓 255、名字 101、
  身份 29。`schema.md` 与 `queries.md` 写明：`gender` 是便利性推断，引用时须同给 `gender_basis`，
  勿当作原文事实。
