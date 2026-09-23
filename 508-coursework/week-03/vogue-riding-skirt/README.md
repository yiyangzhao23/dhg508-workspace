# 作业：ride-she-would（《Vogue》一页 → 数据 → 小库 → skill）

同一条链：**来源 → 文本 → 数据 → 小库 → 一个 skill**，再演示它的两种说话方式
（老师／人物）。整条链从一页真实原件开始。

| 文件 | 是什么 |
|---|---|
| `pages/vogue-p48.jpg` | 原件页面：《Vogue》第 48 页，无署名文章 “RIDE SHE WOULD”。页面未印年月 |
| `pages/ocr-text-p48.txt` | 人读（vision）逐字文本——课堂里它就是 OCR 的结果 |
| `pages/raw-ocr-p48.txt` | 机器 OCR（Apple Vision，见 `tools/ocr_vision.swift`）——真正的 OCR 输出，带错字，用来对比 |
| `records.json` | 从这页抽出的 26 条事实（每条带 `source` 与 `note`） |
| `build_db.py` | 由 `records.json` 用 Python（标准库 sqlite3）建库 |
| `data.db` | SQLite 数据库，26 行 |
| `SKILL.md` | 给 agent 的：这里有什么 + 两种说话方式（老师／The Countess） |
| `demo.md` | 两种说话方式的演示（带 `[id]` 引用） |
| `tools/ocr_vision.swift` | 生成 `raw-ocr-p48.txt` 的机器 OCR 程序 |

## 怎么用

数据库就是一个 SQLite 文件。**不用装工具**：让 agent 用 Python 读它（机器上没有
python3 就先装上），自己写小脚本去查。重建数据库：

```bash
python3 build_db.py
```

重建机器 OCR（可选，需要 Xcode 命令行工具）：

```bash
swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
  -target arm64-apple-macosx26.0 -o /tmp/ocr_vision tools/ocr_vision.swift
/tmp/ocr_vision pages/vogue-p48.jpg > pages/raw-ocr-p48.txt
```

## 课堂线索

1. 看页面 → 「这是《Vogue》的一页，文章 “RIDE SHE WOULD”」
2. 对比两份文本（人读 vs 机器 OCR）→「OCR 会错，要人核」：机器把
   `deaf` 读成 `dear`、`supply` 读成 `sun • ply`、`61` 读成 `6r`，还漏掉
   `It`、`In`、`The material was laid` 等词。
3. 打开数据库 → 「数据变成库，查得到，还带出处」
4. 给 agent `SKILL.md`：
   - 「她是怎么受伤的？」→ 带 `[id]` 的回答
   - 「她的新马鞍长什么样？」→ `[15]`
   - 「这一页是哪一年出版的？」→ 库里没有（本页未印年月），应拒绝
   - 「伯爵夫妇叫什么名字？」→ 原文未载姓名，应拒绝
   - 「请以伯爵夫人口吻讲康复后的事」→ 只用库里的行，且标注这是模拟语气

## 存疑（与 demo 的“数字被遮住”对应）

- 本页**未印出版年月**：不能据此页定年（见 `[1]`）。要定年需另找同一期的其他页
  或书目记录，已记入 `questions.md`。
- 伯爵夫妇**没有姓名**：原文只写 “the young Countess”“the Earl”
  “a well-known hunting house in Warwickshire”（见 `[5]`、`[13]`）。
- 页内插图**无图注**：不能断定画的就是文中那副新鞍（见 `[26]`）。
