# Service Invoice — how to use it

The one-sentence version: fill it in, send it, keep a copy.

## Two ways to use it

**Blank (hand-written):** run `python3 build.py` and print `printables/service-invoice.pdf`.
An empty invoice is a real invoice — the fields are for a pen.

**On screen (typed):** open `forms/invoice.html` in any browser. Click a line and type.
Then press **Ctrl+P / Cmd+P → Save as PDF**. Your typed invoice, styled the same way.

## Filling it in, line by line

- **From** — your name or business name. Free tool, no invoice software needed.
- **Invoice number** — the trick is *just start* at 1 and go up. `2026-001`,
  `2026-002`... The year keeps your files tidy in December.
- **Bill to** — whoever actually pays you. Spell the company name the way it
  appears on their checks, not the way their rep signs off emails.
- **Dates** — issue date is today. Due date is the day you two agreed — if it
  was never discussed, this *is* the discussion: 30 days is a friendly default.
- **Services** — describe work like you'd explain it to a smart friend: what,
  how much, how long. Vague lines become payment-time arguments.
- **Subtotal / discount / tax** — most solo service providers in most US states
  don't charge sales tax on services, but your state may differ. When in doubt,
  ask your state's revenue site (it's normally a 10-minute rabbit hole, cap it).

## Gentle habits that pay off

1. Send the invoice **the same day** you finish. Slow invoicing quietly leaks income.
2. Log it somewhere before dinner, even just a sticky note: number, client, amount.
3. If it goes unpaid past the due date, the "friendly late-payment nudge" email in
   the customer email templates sheet is there for exactly this moment.

## Not-yet facts (so you don't overthink)

This form doesn't track recurring billing, multi-currency, or 50-invoice months.
It's for the first stretch of real work, where simple and finished beats powerful
and abandoned.
