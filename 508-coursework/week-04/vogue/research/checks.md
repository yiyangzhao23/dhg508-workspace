# Week-4 check: 20 random rows vs. the originals

Original = the OCR text of the scanned page (`artifacts/pages/<issue>/page-NNN.txt`).
Sample seed 2026.

| # | row | stored value | page | check | result | cause | fix |
|---|---|---|---|---|---|---|---|
| 1 | advertisers 3 | ALLCOCK'S | scan 2 (1892-12-17) | grounding | PASS | — | — |
| 2 | people 8 | Tartigny | scan 12 (1892-12-17) | grounding | PASS | — | — |
| 3 | people 102 | Mrs. Pierre Lorillard, Jr. | scan 21 (1892-12-24) | grounding | PASS | — | — |
| 4 | people 107 | Mr. and Mrs. Rogers | scan 22 (1892-12-24) | grounding | PASS | — | — |
| 5 | topics 22 | twill | scan 18 (1892-12-17) | grounding | PASS | — | — |
| 6 | topics 131 | reception gown | scan 8 (1892-12-31) | grounding | PASS | — | — |
| 7 | entries 64 | The Incident Of Rataplan: A Farce Which Concer | scan 16 (1892-12-31) | grounding+parse | PASS | — | — |
| 8 | topics 143 | yellow | scan 14 (1892-12-31) | grounding | PASS | — | — |
| 9 | advertisers 57 | KNOX | scan 4 (1892-12-24) | grounding | PASS | — | — |
| 10 | topics 149 | Ephesus | scan 18 (1892-12-31) | grounding | PASS | — | — |
| 11 | people 152 | Mr. Wilton Lackaye | scan 19 (1892-12-31) | grounding | PASS | — | — |
| 12 | topics 9 | Langley's studio | scan 12 (1892-12-17) | grounding | PASS | — | — |
| 13 | people 129 | J. EMILE ERGENS | scan 2 (1892-12-31) | grounding | PASS | — | — |
| 14 | people 60 | Mrs. Bradley-Martin | scan 27 (1892-12-17) | grounding | PASS | — | — |
| 15 | topics 92 | heliotrope | scan 11 (1892-12-24) | grounding | PASS | — | — |
| 16 | people 138 | Margaret Wyaman | scan 10 (1892-12-31) | grounding | PASS | — | — |
| 17 | people 125 | Miss Conyngham | scan 23 (1892-12-24) | grounding | PASS | — | — |
| 18 | topics 122 | World's Fair | scan 25 (1892-12-24) | grounding | PASS | — | — |
| 19 | topics 65 | Sherry's Blue Room | scan 36 (1892-12-17) | grounding | PASS | — | — |
| 20 | topics 88 | Brussels lace | scan 11 (1892-12-24) | grounding | PASS | — | — |

**20/20 passed.** Errors: 0.

## Errors found while building, and the fixes

The final sample above is clean. These are the errors found in earlier runs, each now fixed (details in `improvement-log.md`):

| error | cause | fix |
|---|---|---|
| flowers listed as `material` (`Madame Caroline Testout`, `American Beauties`, `green carnation`) | extractor copied the candidate `kind` | `FLOWERS` set re-tags them `flower` in `extract_facts.py`; rebuilt |
| places/possessives listed as `people` (`Mr. George Vanderbilt's conservatory`) | honourific regex caught `'s` phrases | `clean_name()` drops `'s`/`conservatory` rows; 161 -> 154 people |
| advertiser category truncated (`Oriental rugs and carp`) | candidate wrapped at page width | restored `Oriental rugs and carpets` from the page OCR and rebuilt |
| abstract word `Aristocracy` listed as an `event` | weak candidate | dropped via `RECLASSIFY` |
