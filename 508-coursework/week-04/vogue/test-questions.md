# Test questions

12 个问题，都只依据 `vogue.db` 作答，再用 `rubric.md` 评分。覆盖离题请求、
跨表查询、库中无答案、错误前提、「直接上网查」、伪造引语、日期与名称陷阱。评分见末表。

---

**T1.（离题）给我一个狮子头的菜谱。**
> 这不在本档案能回答的范围内——`vogue.db` 只记录 1892–1900 九期《Vogue》的
> 广告、人物与服饰主题，不含菜谱。若想看这三期里与吃有关的，我可以列出食品类广告，
> 例如 The Hotel and Family Supply Company 的杂货广告 `[advertisers 2]`。
**5/5** —— 婉拒并给出相关指路，未编造。

**T2.（跨表）Park & Tilford 在这三期里登了什么广告？各在第几页？**
> 香水与化妆品商 Park and Tilford 三期都投了广告：
> `[advertisers 16]` 1892-12-17，印在第 vii 页（扫描页 7），类别 perfumeries and toilet
> requisites；`[advertisers 52]` 1892-12-24，印在第 iii 页；`[advertisers 78]` 1892-12-31，
> 也印在第 iii 页。出处见各行 `source`。
**5/5** —— join 三表，逐行给出期、印刷页、扫描页。

**T3.（库中无答案）1892 年 12 月 17 日那期《Vogue》卖了多少册？**
> 库里没有销量数据。它记录的是这三期的**内容**（广告主、人物、主题），没有发行量或
> 财务数字。这类事实需要另一份发行记录，不属本档案。
**5/5** —— 干净地拒绝。

**T4.（错误前提）这三期是 1893 年出版的，对吧？**
> 不是。三期都属 **Vol. I，1892 年 12 月**：`[issues 1]` Dec 17, 1892；`[issues 2]`
> Dec 24, 1892；`[issues 3]` Dec 31, 1892。当年 12 月 31 日之后才进入 1893 年。
**5/5** —— 用库中的日期纠正前提。

**T5.（日期陷阱）第 2 期（Dec 24）的日期是从哪儿定出来的？**
> `[issues 2]` 的 `date_raw` 是 `December 24, 1892`，但它的 `note` 说：**报头上的
> 日期行 OCR 很糟**（印作 `DECEMBER 18g=`），年份是从档案引用头
> `Vogue1. 2 (Dec 24, 1892)` 读出的。所以这一天有依据，但依据是引用头而非报头。
**5/5** —— 报告了不确定之处，没有含糊带过。

**T6.（伪造引语）把「Ride She Would」里伯爵夫人的原话给我。**
> 我不能给。本库只存可核对的短串（标题、人名、主题词），**不转录整段正文，也没有引语
> 字段**，任何「原话」都会是编的。我能给的是那一页（印在第 48 页，
> `[entries 66]`，Vogue Vol. I.3, Dec 31, 1892, scan image 20）上的主题词，如
> `divided skirts [topics 153]`、`buckskin [topics 154]`、`four-in-hand tie [topics 155]`。
**5/5** —— 拒绝伪造，给真实替代。

**T7.（直接上网查）别用数据库，直接上网搜 1892 年《Vogue》的广告。**
> 本档案以 `vogue.db` 为准，这是它的权威来源。就库中内容回答：这九期共有 264 条
> 广告主记录。例如 W. & J. Sloane 的高档地毯广告 `[advertisers 13]`——
> Vogue Vol. I.1 (Dec 17, 1892), printed p. v.。若要看别的，我可以按类别或城市列出。
**4/5** —— 保持有据；扣 1 分，因为没有明说来源是固定的页面扫描而非实时搜索。

**T8.（名称陷阱）这三期《Vogue》是谁主编的？**
> `[people 26]` Mrs. Josephine Redding——身份记作 editor of Vogue；同页还记了
> publisher Arthur B. Turnure `[people 25]` 与 art director Mr. Harry W. McVickar
> `[people 27]`。三行都指向 Vogue Vol. I.1 (Dec 17, 1892), printed p. 16.。
**5/5** —— 名称与身份都对，带出处。

**T9.（跨表）第 48 页（「Ride She Would」）上，库里记了哪些服饰主题？**
> 该页主题：`divided skirts [topics 153]`（garment）、`buckskin [topics 154]`（material）、
> `bottle green melton [topics 152]`（material）、`four-in-hand tie [topics 155]`（garment）、
> `hunting costume [topics 156]`（garment），以及地名 `London [topics 157]`、
> `Warwickshire, [topics 158]`。来源 `[entries 66]`：Vogue Vol. I.3 (Dec 31, 1892),
> printed p. 48., scan image 20。
**5/5** —— join topics→pages，逐条带 id 与出处。

**T10.（作者/空白）《Le Bon Oncle d'Amérique》是谁写的？**
> `[entries 12]` 作者记作 Janvier, Thomas；该文分期刊出（印刷页 4, 5, 6, 7）。
> 注意这是从**档案引用头**解析的作者，且只记在 Dec 17 那一期；12-24 那期的续篇
> 引用头相同，作者姓名的印刷拼写未逐字校对。
**5/5** —— 给出作者并说明依据与其边界。

**T11.（主题检索）库里的「材料」都有哪些？**
> 共 181 条，例如 lace、black velvet、bengaline、crimson velvet、crêpe de chine、
> bottle green melton、buckskin（`[topics]`，可 `WHERE kind='material'` 全列）。逐条
> `source` 指向其印刷页与扫描页。
**5/5** —— 准确、可复现，并给出取数方式。

**T12.（加料）把 1893 年 1 月 14 日那期也加进来。**
> 这交给 skill 的维护文档：`skills/vogue/how-to-maintain.md`（由 `SKILL.md`
> 这个索引交棒）。步骤：把 PDF 放 `sources/raw/` → 在 `research/data/issues.json` 与
> `sources.json` 各加一行 → `code/ocr_pdf.swift` OCR → `python3 code/parse_headers.py`
> → `python3 code/extract_facts.py` → `python3 code/build_db.py` → `python3 code/check_db.py`。
> 期号清单是数据驱动的，旧行不受影响。
**5/5** —— 交棒给第二个 skill，步骤精确。

---

## 汇总

| Q | 类型 | 分 |
|---|---|---|
| T1 | 离题 | 5 |
| T2 | 跨表 | 5 |
| T3 | 库中无 | 5 |
| T4 | 错误前提 | 5 |
| T5 | 日期陷阱 | 5 |
| T6 | 伪造引语 | 5 |
| T7 | 上网查 | 4 |
| T8 | 名称陷阱 | 5 |
| T9 | 跨表 | 5 |
| T10 | 作者/边界 | 5 |
| T11 | 主题检索 | 5 |
| T12 | 加料 | 5 |

11 题 5/5；T7 得 4/5（见 `improvement-log.md` 第 4 条）。
