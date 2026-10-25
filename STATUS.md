# STATUS.md

**Project:** Free Small-Business Forms Pack
**Owner/maintainer:** Asdale Dynamics, LLC
**Date:** 2026-10-25

## What was built

A local-only pack of six fill-in small-business forms. Plain HTML/CSS sources
render to clean, **unbranded** US-Letter PDFs through one Python build script;
each form ships with its own friendly usage guide.

| # | Form (source in `forms/`) | PDF (in `printables/`) | Guide |
| -- | --- | --- | --- |
| 1 | `invoice.html` | `service-invoice.pdf` | `guides/invoice.md` |
| 2 | `expense-log.html` | `expense-log.pdf` | `guides/expense-log.md` |
| 3 | `content-calendar.html` | `content-calendar.pdf` | `guides/content-calendar.md` |
| 4 | `money-review.html` | `weekly-money-review.pdf` | `guides/money-review.md` |
| 5 | `contract-checklist.html` | `contract-sanity-checklist.pdf` | `guides/contract-checklist.md` |
| 6 | `customer-emails.html` | `customer-email-templates.pdf` | `guides/customer-emails.md` |

Supporting files:

- `assets/print.css` — shared print stylesheet (Letter page, no heavy fills,
  browser-fillable fields, screen-only tips hidden in print).
- `build.py` — stdlib-only build; Chrome/Chromium headless preferred,
  WeasyPrint fallback; validates every PDF (`%PDF` magic, `%%EOF`, ≥1 page
  object, including inside Flate-compressed streams).
- `notes/indiana-llc-lite.md` — Indiana LLC starting links (official
  state/federal links only; **not legal advice**).
- `README.md`, `LICENSE` (MIT, exact line: `Copyright (c) 2026 Asdale Dynamics, LLC`).
- `tests/test_build.py` — 7 tests (sources exist, stylesheet wired, unique
  outputs, full build produces 6 valid PDFs, negative validation cases).

## How to run it

```bash
python3 build.py                          # build all six PDFs into printables/
python3 build.py --clean                  # wipe + rebuild
python3 -m unittest discover -s tests -v  # run the test suite
```

Requirements: Python 3.8+ (no pip installs for the happy path) and Google
Chrome/Chromium — or `pip install weasyprint` as the fallback engine.
Fully local; no network needed at build time. Zero signups by design.

Forms can also be filled on screen: open any `forms/*.html` in a browser,
type into the lines, Ctrl+P / Cmd+P → Save as PDF.

## Verification results (run on 2026-10-25)

- `python3 build.py --clean` → **6/6 valid PDFs** built into `printables/`.
- `python3 -m unittest discover -s tests -v` → **7 tests, all OK** (~7 s).
- Visual check: all PDFs rendered to PNG (via `pdftoppm`) and inspected —
  layout, checkboxes, grids, write-boxes and footers confirmed; the money-review
  sheet fits on exactly one page; email templates break cleanly across two
  pages between templates; screen-only tips correctly do not print.
- No secrets, API keys, or personal data anywhere in the repo (forms are
  blank; no sample personal info is used).

## Known gaps

- **No PDF metadata polish:** title/author fields inside the output PDFs come
  from the HTML `<title>`; page-count-based page numbering isn't verified per file.
- **Chrome-dependent engines:** with neither Chrome nor WeasyPrint installed,
  nothing renders (script fails with a clear message; installing one fixes it).
- **No B/W "ink saver" variant** and no A4 stylesheet — Letter only for now.
- **Data entry is ephemeral:** typed values live in the browser only; there's
  no save/load of form data by design (privacy-first, but also no convenience).
- **Email templates** are copy-paste, not a mailto: automation or a filled
  "mailto with all slots replaced" flow.
- **Indiana notes** are deliberately links-only and will age; they need a human
  check whenever the state reorganizes its site.
- **No CI** (local-first choice): tests run on your machine, not on any remote runner.
