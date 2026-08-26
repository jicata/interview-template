# 002. Derive order-line pricing on read; round each line, then sum

**Status:** accepted
**Date:** 2026-08-26

## Context

The Order Builder prices each order line — a volume discount above a unit
threshold — and keeps a running order total. Two questions had live alternatives.

**Where the computed money lives.** `order_lines` stores `quantity` and
`unit_price` and nothing else. A discount rate, a discount amount, and a line
total could each be persisted alongside them.

The constraints that bear on it:

- There are no migrations. A new column means editing `_build_db()`'s
  `executescript` *and* `data/order_lines.csv`, whose header drives the `INSERT`.
  A mismatch fails at import, which takes the whole app down at startup.
- `order_lines.unit_price` is already denormalized deliberately — it is the price
  charged at the time, not the product's current price. So the table does have
  precedent for storing a derived-looking value.
- The discount rule is a *rule*, not a fact about a row. It is the thing most
  likely to change (the threshold, the rate, per-line versus order-wide).

**How money rounds.** `products.unit_price` and `order_lines.unit_price` are
SQLite `REAL`. `unit price × quantity × 0.9` produces sub-cent fractions, and the
order total can be computed two ways that disagree: sum the unrounded line totals
then round once, or round each line then sum. On a 20-line order the two differ by
cents, and the difference is visible to the customer.

## Decision

**Derive all pricing on read.** No new column, no CSV edit. `order_lines` remains
`quantity` + historical `unit_price`; discount rate, discount amount, line total
and order total are computed on every read by `app/features/orders/pricing.py`,
which imports nothing from `app.db` and takes no connection.

**Compute in `Decimal`, round half-up to 2 decimal places, round each line before
summing.** The discount amount is quantized per line; the line total is
`gross - discount_amount`; the order total is the sum of already-rounded line
totals. `float` crosses the wire, matching the existing `REAL` columns.

The threshold and rate are module constants — `DISCOUNT_THRESHOLD_UNITS = 50`,
`DISCOUNT_RATE = Decimal('0.10')` — and the threshold is compared strictly, so a
quantity of exactly 50 is not discounted.

## Consequences

- Changing the discount rule changes one pure module. No stored rows to backfill,
  and no possibility of a persisted total disagreeing with the rule that produced
  it.
- `pricing.py` is testable with no database at all. That is worth naming: the one
  real cost of a layered architecture is that business rules need infrastructure
  to test, and a pure pricing module buys it back without introducing a port.
- Every read recomputes. Irrelevant at this scale; if order history ever needed
  the *rate that applied on the day*, the rule would have to be versioned or the
  outcome persisted, exactly as `unit_price` already is. That is the trade this
  forecloses, and it is the same trade `unit_price` resolved the other way.
- Rounding per line means the order total is the sum of what each line is actually
  charged, which is what an invoice shows and what a customer can check by adding
  up the column. It also means the total is *not* `round(sum(unrounded))`, and a
  test asserting that will fail — deliberately.
- `float` on the wire keeps one money representation end-to-end and avoids
  Pydantic serializing `Decimal` as a JSON string that the frontend would have to
  parse. Exactness is kept where it decides an outcome (the arithmetic) rather
  than where it is only displayed.
