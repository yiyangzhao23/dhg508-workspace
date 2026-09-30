# Vogue 1892-12-17 —— 一页/一期 → 文本 → 数据 → 小库 → 一个 skill

第三周作业：学 Markdown，写一个 skill；挑一段自己关心的历史材料，让 opencode 把事实
抽成行，存进一个 SQLite 小库，回原件核对几行；再写**一个** skill，把它变成一个有名字的
agent（**Miss Redding**），并演示它的说话方式。

材料是真实旧刊的一期：**《Vogue》Vol. I, No. 1（December 17, 1892）**，36 个扫描页。
PDF 无文字层，文本由本机 OCR（Apple Vision）得到。

## 链条

| 环节 | 文件 |
|---|---|
| 来源 | 原 PDF（约 66 MB，未入库；见下） |
| 文本 | `pages/1892-12-17-ocr.txt`（36 页 OCR） |
| 数据 | `records.json` —— 142 条事实，每条带 `source` 与 `note` |
| 小库 | `data.db` —— SQLite，一张表 `records`，142 行 |
| skill | `SKILL.md` —— agent **Miss Redding** 的规矩与口吻 |
| 演示 | `demo.md` —— 两种说话方式（老师 / Miss Redding），带 `[id]` |

## `records` 表

`id, date, event, place, people, source, note`。142 行来自这一期：
文章条目、98 条广告中的本期部分、以及本文人物。`source` 形如
`Vogue Vol. I.1 (December 17, 1892), printed p. vii., scan image 7`。

## 怎么用

```bash
python3 build_db.py          # 由 records.json 重建 data.db
```

用 Python 读库即可（标准库 `sqlite3`，不用装东西）：

```python
import sqlite3
con = sqlite3.connect("data.db")
con.execute("SELECT id, event, people, source FROM records WHERE event LIKE '%广告%'")
```

## 原件与大数据

原 PDF（约 66 MB）与页图不入 git；`pages/1892-12-17-ocr.txt` 与 `records.json`
足以重建小库。第四周会把这一期扩成三期、并把小库长成关系库。

## 存疑

- OCR 无文字层，分栏页会串读；本库只抽可靠的行（广告主、人物、标题），不逐句转正文。
- 广告类别词是阅读判断，非印刷原文；`note` 里会标出存疑处。
