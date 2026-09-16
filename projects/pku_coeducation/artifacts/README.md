# Artifacts

Large generated outputs and local rebuild products go here.

This directory is ignored by git except for this README.

## issue-559-pages/

The other three pages (p1, p3, p4) of 《北京大學日刊》第559號, 1920-03-11, kept
locally so the whole issue is on hand. Not committed to git (redundant / bulky).

Rebuild:

```bash
mkdir -p issue-559-pages
for n in 0 2 3; do
  curl -sL "https://archive.org/download/beida-rikan-1920.03.11/page/n${n}.jpg" \
    -o "issue-559-pages/beida-rikan-1920-03-11-559-p$((n+1)).jpg"
done
```
