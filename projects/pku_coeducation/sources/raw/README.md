# Raw sources

Original source material, kept unchanged.

## beida-rikan-1920-03-11-559-p2.jpg

- **Document:** 《北京大學日刊》(Beijing University Daily), 第559號,
  民國九年三月十一日 (11 March 1920), 第2版.
- **Module used:** 「本校女生消息」 — the university's notice that women had
  been admitted, with a 「女學生一覽表」 table listing them as 旁聽生.
- **Source:** Internet Archive, item `beida-rikan-1920.03.11`
  <https://archive.org/details/beida-rikan-1920.03.11>
- **Direct file:** `https://archive.org/download/beida-rikan-1920.03.11/page/n1.jpg`
- **Retrieved:** 2026-09-16
- **Rights:** Published 1920; public domain.

The other three pages of the same issue (n0, n2, n3) are stored locally under
`../../artifacts/issue-559-pages/` and deliberately kept out of git as
redundant/large. They can be re-downloaded with:

```bash
for n in 0 2 3; do
  curl -sL "https://archive.org/download/beida-rikan-1920.03.11/page/n${n}.jpg" \
    -o "issue-559-pages/beida-rikan-1920-03-11-559-p$((n+1)).jpg"
done
```
