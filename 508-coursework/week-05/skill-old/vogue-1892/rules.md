# rules —— 日期、名称、出处、语言

数据来自 1892 年的印刷页，由 Apple Vision OCR 得到。下面是规范化与作答的规则。

## 日期

- **原始措辞与机器形式并列。** `issues.date_raw` 是印出来的样子
  （`December 17, 1892`）；`issues.date_iso` 是机器用的 `1892-12-17`。
- **转换规则只有一条**：把印出的英文月日年照抄成 ISO（月名 → 两位数字），不做任何推断。
  `issues.date_basis` 写明这一行是从哪里读到的（报头或档案引用头）。
- **期号 ≠ 日期。** “Vol. I, No. 1”是期号；“December 17, 1892”是日期，两者都在库里。
- 报告某一事实时，报**印刷页 + 扫描页**，不要只报期号。

## 名称

- `name_raw` 保留印刷原样，含 OCR 错字（如 `Gorham M'f'g Company`、`HODGKINS & HODGKINS`）。
- `name_norm` 是规范化形式，转换规则固定为：去掉行末的逗号/句点/分号、把连续空白并成一个空格。
  **不改拼写、不改大小写、不补全缩写。** 例：`PARK AND TILFORD,` → `PARK AND TILFORD`。
- 两条规则都写进表里，原始与规范化并列，任何一行都可回查它怎么变的。

## 条目标题与作者

- `entries.title_raw` / `author_raw` / `printed_pages_raw` 全部取自扫描页上的**档案引用头**
  （形如 `'Le Bon Oncle D'amérique' Janvier, Thomas. Vogue1. 1 (Dec 17, 1892): 4, 5, 6, 7.;`），
  并把整行原样存进 `citation_raw`，便于复核。
- 同一篇文章跨多页时会有多行 `entries`（各页一行），这是有意的：每行都指回它所在的扫描页。

## 出处

每条事实行都有自带的 `source`，形如
`Vogue Vol. I.1 (December 17, 1892), printed p. vii., scan image 7`。
引用时行 `id` 与 `source` 一起给，例如：
`Park & Tilford 的香水广告 [advertisers 16] —— Vogue Vol. I.1 (Dec 17, 1892), printed p. vii., scan image 7`。

## 语言

- 用提问的语言作答（中文问就用中文，英文问就用英文）。
- 引用 `*_raw` 时照抄原样，不要翻译或改错字；需要时在括号里给中文意译，并注明是意译。

## OCR 的边界

- 这些 PDF 没有文字层，全部内容由本机 OCR 得到；难读处的错字保留在 `*_raw` 中。
- 页面多为分栏，OCR 会把栏目串读；因此本库只抽取**可靠的行**（广告主名、人名、标题、
  主题词），不逐句转录正文。`note` 里会标出存疑之处。
