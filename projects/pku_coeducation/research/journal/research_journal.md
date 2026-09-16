# Research Journal

- [Design Document](../design/design_doc.md)

## 2026-09-16

- Picked the question: when did Peking University first admit women, and what
  did "admit" mean.
- Found the primary notice: 《北京大學日刊》第559號, 11 March 1920, 「本校女生
  消息」 with a 「女學生一覽表」. Located a scan on the Internet Archive
  (`beida-rikan-1920.03.11`).
- Internet Archive already supplies a Tesseract OCR of the page; it is garbage
  on this sideways, small-type module (sample kept in
  `sources/processed/beida-rikan-1920-03-11-559-archive-tesseract.txt`).
- No OpenRouter/DeepSeek key available, so went straight to OpenCode vision and
  transcribed the module by eye from the page image. The strip is printed
  sideways; rotating it upright makes it readable.
- Limitation found: the table's 姓名 column is cut off at the bound edge in this
  scan, so names cannot be recovered from it. Recorded the readable fields
  (籍貫 / 年齡 / 經過學校 / 到校年月 / 現在肄業) instead. The key fact —
  the women are entered as **旁聽生**, 到校年月 九年二月 — is clear.
- Cross-checked with Cai Yuanpei's 1934 memoir and modern secondary accounts:
  two-stage admission (auditors Feb–Mar 1920, formal enrolment summer 1920).
