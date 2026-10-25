# Free Small-Business Forms Pack

Six fill-in business forms as plain HTML/CSS, built into **unbranded, print-ready
PDFs** by one local script. No signups, no accounts, no network calls — open the
folder, run two commands, get clean PDFs.

Made by **Asdale Dynamics, LLC** in the "explain it like a friend would" spirit:
plain language, tested, local-first. Free under the MIT License.

## What's inside

| Form | PDF in `printables/` | Friendly guide |
| --- | --- | --- |
| Simple service invoice | `service-invoice.pdf` | [`guides/invoice.md`](guides/invoice.md) |
| Expense log sheet | `expense-log.pdf` | [`guides/expense-log.md`](guides/expense-log.md) |
| Content-calendar grid | `content-calendar.pdf` | [`guides/content-calendar.md`](guides/content-calendar.md) |
| Weekly money-review checklist | `weekly-money-review.pdf` | [`guides/money-review.md`](guides/money-review.md) |
| Contract-sanity checklist | `contract-sanity-checklist.pdf` | [`guides/contract-checklist.md`](guides/contract-checklist.md) |
| Customer email templates | `customer-email-templates.pdf` | [`guides/customer-emails.md`](guides/customer-emails.md) |

Plus:

- **`notes/indiana-llc-lite.md`** — links-only starting page for Indiana LLC
  basics (official state/federal links only; **not legal advice**).
- **`tests/`** — verifies every form builds a valid PDF.

## How to use it (totally local)

```bash
# 1. Optional: install Chrome if you don't have it (any modern Chromium works).
#    Fallback engine: pip install weasyprint

# 2. Build all six PDFs into printables/:
python3 build.py

# 3. Verify every PDF exists and is a valid, renderable file:
python3 -m unittest discover -s tests -v

# Extras:
python3 build.py --clean    # remove built PDFs and rebuild from scratch
python3 build.py --out /somewhere/else  # build into a different folder
```

**Printing tip:** the PDFs are US Letter. Print at 100% scale ("Actual size")
with headers/footers off — the forms already leave clean margins.

**Prefer to fill forms on screen?** Open any `forms/*.html` in a browser, type
into the lines, and Ctrl+P / Cmd+P → Save as PDF. Same clean output, your typing
included.

## How it works

- `forms/*.html` + `assets/print.css` — the sources. Letter-size print styles,
  gray-ink-friendly (borders instead of dark fills), no branding in print output.
- `build.py` — stdlib-only Python. Renders each form headlessly (Chrome
  preferred, WeasyPrint fallback) and validates each PDF (`%PDF` magic, `%%EOF`,
  and at least one real page object, compressed streams included).
- `printables/` — the output PDFs. Unbranded: no logos, no credits printed
  inside the forms. Credit lives here in the README.

## Requirements

- Python 3.8+ (stdlib only — no pip installs needed for the happy path)
- Google Chrome / Chromium **or** `pip install weasyprint` as the fallback engine

## Design decisions (the short version)

- **Unbranded PDFs.** The forms are yours — blank paper with good lines, not a
  flyer. Everything about who made this lives in this repo, not on your printout.
- **One-page discipline.** Each checklist/grid form targets a single Letter
  page; its component fits in one packed page.
- **Fill anywhere.** Blank print now, typed screen fill anytime, same layout.

## Known gaps

See [`STATUS.md`](STATUS.md) for the honest list (e.g., no auto-numbering, no
saved per-client data, email templates are copy-paste rather than a mailto: flow).

## License and credit

MIT — see [`LICENSE`](LICENSE). Built and maintained by **Asdale Dynamics,
LLC**. Find more plain-English AI and small-business tools at
https://dylanasdale.github.io
