# queries —— 常用查询示例

用 Python 的 `sqlite3` 执行。**始终把 `id` 与 `source` 选出来**，答案才能标注出处。
表结构见 `schema.md`。

```python
import sqlite3
con = sqlite3.connect("vogue.db")
for row in con.execute("SELECT ..."):
    print(row)
```

## 1. 跨表：一家广告主在各期里的投放，带出处

```sql
SELECT a.id, a.name_raw, a.category_raw, a.city_raw,
       i.date_raw AS issue, p.printed_label, a.source
FROM advertisers a
JOIN pages  p ON p.id = a.page_id
JOIN issues i ON i.id = p.issue_id
WHERE a.name_norm LIKE '%Tilford%'
ORDER BY i.date_iso;
```

## 2. 一期里的全部广告主

```sql
SELECT a.id, a.name_raw, a.category_raw, a.address_raw, a.source
FROM advertisers a
JOIN pages  p ON p.id = a.page_id
JOIN issues i ON i.id = p.issue_id
WHERE i.date_iso = '1892-12-17'
ORDER BY a.id;
```

## 3. 社交增刊里最常出现的人物（带出处）

```sql
SELECT pe.id, pe.name_raw, pe.role_raw, p.printed_label, pe.source
FROM people pe
JOIN pages p ON p.id = pe.page_id
WHERE p.section = 'society supplement'
ORDER BY pe.id
LIMIT 20;
```

## 4. 按类别找服饰 / 材料 / 场所

```sql
SELECT t.id, t.term_raw, t.kind, p.printed_label, t.source
FROM topics t JOIN pages p ON p.id = t.page_id
WHERE t.kind = 'material'
ORDER BY t.term_raw;
```

## 5. 一篇文章及其作者、印刷页

```sql
SELECT e.id, e.title_raw, e.author_raw, e.printed_pages_raw, e.source
FROM entries e
WHERE e.kind = 'article';
```

## 6. 某一印刷页上的全部内容

```sql
SELECT 'entry'  AS what, e.id, e.title_raw AS value FROM entries e
  JOIN pages p ON p.id = e.page_id WHERE p.printed_label LIKE '48%'
UNION ALL
SELECT 'advertiser', a.id, a.name_raw FROM advertisers a
  JOIN pages p ON p.id = a.page_id WHERE p.printed_label LIKE '48%'
UNION ALL
SELECT 'person', pe.id, pe.name_raw FROM people pe
  JOIN pages p ON p.id = pe.page_id WHERE p.printed_label LIKE '48%'
UNION ALL
SELECT 'topic', t.id, t.term_raw FROM topics t
  JOIN pages p ON p.id = t.page_id WHERE p.printed_label LIKE '48%';
```

## 7. “Ride She Would”那一页（印在第 48 页）的条目与主题

```sql
-- 该页在档案引用头里叫 "Publishers' Notices"，正文标题才是 RIDE SHE WOULD
SELECT e.id AS entry_id, e.title_raw, e.kind, e.printed_pages_raw, e.source
FROM entries e WHERE e.printed_pages_raw LIKE '48%';
```

```sql
SELECT t.id, t.term_raw, t.kind, t.source
FROM topics t JOIN pages p ON p.id = t.page_id
WHERE p.printed_label LIKE '48%';
```

## 8. 城市分布

```sql
SELECT city_raw, COUNT(*) AS n
FROM advertisers
WHERE city_raw <> ''
GROUP BY city_raw ORDER BY n DESC;
```

## 9. 按名称检索人物（原始与规范化都可查）

```sql
SELECT id, name_raw, name_norm, role_raw, source
FROM people
WHERE name_raw LIKE '%Lorillard%' OR name_norm LIKE '%Lorillard%';
```

## 10. 找一行并证明出处

```sql
SELECT t.term_raw, t.source, src.label AS document, iss.date_raw, p.ocr_page, t.note
FROM topics t
JOIN pages  p   ON p.id = t.page_id
JOIN issues iss ON iss.id = p.issue_id
JOIN sources src ON src.id = iss.source_id
WHERE t.id = 150;
```

> 注：`issues` 是表名，join 时用别名（`iss`），免得与列名混淆。
