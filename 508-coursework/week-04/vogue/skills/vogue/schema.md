# schema —— 表结构

`vogue.db` 有 7 张表、6 个外键：

```
sources ──< issues ──< pages ──< entries
                                 ├──< advertisers
                                 ├──< people
                                 └──< topics
```

## 表与列

### sources（10）
文献。`id, source_key, publication, kind, label, filename, url, note`

### issues（9）
九期。《Vogue》1892-12-17 / 24 / 31、1893-01-07 / 02-04 / 03-25、1900-07-05 / 07-19 / 08-23。
`id, issue_no, date_raw, date_iso, date_basis, volume, page_count, source_id→sources.id, note`

> `issue_no` 可为空：1900 年 7 月的 ProQuest 引用头不给卷号/期号，如实留空。

### pages（254）
每个扫描页。
`id, issue_id→issues.id, ocr_page, printed_label, section, header_kind, header_title,
header_author, header_company, matched, chars, note`

- `ocr_page`：PDF/扫描里的第几页（1 起）。
- `printed_label`：该页在刊物里的印刷页号（如 `4, 5, 6, 7.`、`iii.`、`S1, S2.`、`48.`）。
- `section`：`cover` / `editorial` / `advertisements` / `society supplement` / `continuation`。
- `matched`：能否在扫描页上读到档案的引用头（0/1）；`continuation` 页为 0，是上一页的续页。

### entries（206）
页面上的条目，来自每页档案引用头（`code/parse_headers.py`）。
`id, page_id→pages.id, kind, title_raw, author_raw, company_raw, printed_pages_raw,
citation_raw, source, note`

- `kind`：`article` / `advertisement` / `item`。
- `title_raw` / `author_raw`：印出的标题与作者原样（如 `Janvier, Thomas`）。
- `citation_raw`：档案加在页面上的整行引用头原样，可复核。

### advertisers（264）
广告主。`id, page_id→pages.id, name_raw, name_norm, category_raw, address_raw, city_raw, source, note`

### people（560）
人物。`id, page_id→pages.id, name_raw, name_norm, role_raw, source, note`

### topics（573）
可检索的主题。`id, page_id→pages.id, term_raw, kind, source, note`
`kind` ∈ `garment` / `material` / `color` / `place` / `event` / `flower` / `object`。

## 外键

| 子表.列 | → 父表.列 |
|---|---|
| `issues.source_id` | `sources.id` |
| `pages.issue_id` | `issues.id` |
| `entries.page_id` | `pages.id` |
| `advertisers.page_id` | `pages.id` |
| `people.page_id` | `pages.id` |
| `topics.page_id` | `pages.id` |

## 行数

用这条只看档案规模：

```sql
SELECT (SELECT COUNT(*) FROM sources)       AS sources,
       (SELECT COUNT(*) FROM issues)        AS issues,
       (SELECT COUNT(*) FROM pages)         AS pages,
       (SELECT COUNT(*) FROM entries)       AS entries,
       (SELECT COUNT(*) FROM advertisers)   AS advertisers,
       (SELECT COUNT(*) FROM people)        AS people,
       (SELECT COUNT(*) FROM topics)        AS topics;
```
