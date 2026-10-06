# Week-4 check: 20 random rows vs. the originals

Original = the OCR text of the scanned page (`artifacts/pages/<issue>/page-NNN.txt`).
Sample seed 2026.

| # | row | stored value | page | check | result | cause | fix |
|---|---|---|---|---|---|---|---|
| 1 | advertisers 57 | KNOX | scan 4 (1892-12-24) | grounding | PASS | — | — |
| 2 | people 204 | Princess Margaretha of Prussia | scan 22 (1893-01-07) | grounding | PASS | — | — |
| 3 | topics 19 | Aigremont | scan 14 (1892-12-17) | grounding | PASS | — | — |
| 4 | topics 38 | Yonkers | scan 21 (1892-12-17) | grounding | PASS | — | — |
| 5 | topics 315 | Chicago Fair | scan 23 (1893-03-25) | grounding | PASS | — | — |
| 6 | advertisers 24 | KNOX | scan 8 (1892-12-17) | grounding | PASS | — | — |
| 7 | people 7 | Margot | scan 12 (1892-12-17) | grounding | PASS | — | — |
| 8 | topics 220 | Chicago Fair | scan 23 (1893-01-07) | grounding | PASS | — | — |
| 9 | topics 262 | Aiken | scan 17 (1893-02-04) | grounding | PASS | — | — |
| 10 | topics 129 | fichu cape | scan 8 (1892-12-31) | grounding | PASS | — | — |
| 11 | people 411 | MR. BIRRELL | scan 8 (1900-07-05) | grounding | PASS | — | — |
| 12 | topics 162 | SILENCE CLOTH | scan 2 (1893-01-07) | grounding | PASS | — | — |
| 13 | topics 111 | Osborne | scan 22 (1892-12-24) | grounding | PASS | — | — |
| 14 | topics 486 | sack suit | scan 19 (1900-07-19) | grounding | PASS | — | — |
| 15 | topics 563 | point d'esprit | scan 22 (1900-08-23) | grounding | PASS | — | — |
| 16 | people 555 | Miss Euphemia Trotter | scan 21 (1900-08-23) | grounding | PASS | — | — |
| 17 | topics 528 | pink tissue | scan 14 (1900-08-23) | grounding | PASS | — | — |
| 18 | topics 573 | Turkey | scan 24 (1900-08-23) | grounding | PASS | — | — |
| 19 | topics 191 | New Orleans | scan 16 (1893-01-07) | grounding | PASS | — | — |
| 20 | people 453 | H Thacher | scan 3 (1900-07-19) | grounding | PASS | — | — |

**20/20 passed.** Errors: 0.

## Errors found while building, and the fixes

The final sample above is clean. These are the errors found in earlier runs, each now fixed (details in `improvement-log.md`):

| error | cause | fix |
|---|---|---|
| flowers listed as `material` (`Madame Caroline Testout`, `American Beauties`, `green carnation`) | extractor copied the candidate `kind` | `FLOWERS` set re-tags them `flower` in `extract_facts.py`; rebuilt |
| places/possessives listed as `people` (`Mr. George Vanderbilt's conservatory`) | honourific regex caught `'s` phrases | `clean_name()` drops `'s`/`conservatory` rows; 161 -> 154 people |
| advertiser category truncated (`Oriental rugs and carp`) | candidate wrapped at page width | restored `Oriental rugs and carpets` from the page OCR and rebuilt |
| abstract word `Aristocracy` listed as an `event` | weak candidate | dropped via `RECLASSIFY` |
