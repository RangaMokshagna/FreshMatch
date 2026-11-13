# FreshMatch academic project report

The 34-page PDF follows the supplied academic reference: A4 pages, serif type, aligned paragraphs, page borders, front matter, nine chapters, figures, tables and references. The Word edition is editable; pagination can change with locally installed fonts.

Authors:
- K. Darshan Sai — RA2311027010002
- J. Ranga Mokshagna — RA2311027010003
- P. Bharat Sai — RA2311027010007

The report describes the recorded FreshMatch implementation and frozen evaluation at project commit `c767a0c`. It includes actual application screenshots, real Instacart data provenance, model configuration, the improved hybrid, evaluation uncertainty and limitations. Reported results are not invented or adjusted for presentation.

Institutional wording and the SRM logo follow the user-supplied reference. As requested, faculty and department details match the reference: Dr. Archana R (Assistant Professor), Dr. Kavitha V (Professor & Head), and the Department of Data Science and Business Systems. Signatures and signing dates remain blank. Review institutional declarations before signing or submission.

To update faculty details, edit `report_profile.json` and rebuild:

```bash
python reports/build_report.py
```

Generation requires Python with reportlab, python-docx, Pillow, matplotlib and the Liberation font family. The builder reads the existing project experiment artifacts and application screenshots. `report_structure.json` records page numbering; `layout_audit.json` records the PDF layout positions.
