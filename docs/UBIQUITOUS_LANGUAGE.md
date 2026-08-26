# Ubiquitous Language — interview-template

The domain nouns, as the schema and seed data name them. Use these in code, tests, PRs and conversation. Maintained by `/ubiquitous-language`; disputes are settled by `backend/app/db.py`'s schema, which is the source of truth.

**One bounded context.** A small order-management domain — no sub-domains, no aliases.

| Term | Means | Not |
| --- | --- | --- |
| **Customer** | A company that places orders. `id`, `name`, `email`. Three exist in the seed. | client, account, buyer |
| **Product** | A sellable item. Carries a current `unit_price` and a `pack_size`. | item, SKU (the SKU is a *field* on a product, not the product) |
| **SKU** | The product's stock code — `WIDG-A`, `SUPP-Z`. A field, unique per product. | the product itself |
| **Pack size** | How many units ship in one pack of a product. In the seed data every historical order quantity equals the product's pack size. | case size, batch, bundle |
| **Order** | A customer's purchase. Has a `status` and, when placed, an `order_date`. | purchase, cart, basket |
| **Order line** | One product-and-quantity row on an order, with the `unit_price` **charged at the time**. Every seeded order has exactly one. | line item, item, order detail |
| **Status** | Exactly `completed` or `draft`. Enforced by a `CHECK` constraint — no other value can be written. | state, stage |
| **Draft** | An order not yet placed: `status = 'draft'`, `order_date` empty. Order 19 is the only one, and it has no lines. | pending, open, in progress |
| **Completed** | An order that has been placed, with an `order_date`. | fulfilled, shipped, closed |
| **Unit price** | Ambiguous on purpose — always qualify it. On **products** it is the current price; on **order lines** it is the historical price charged. They are equal in the seed data, which hides the difference. | price |
| **Pack multiple** | A quantity that is an exact multiple of the product's `pack_size`. The only quantity an order line accepts — 12 or 24 of a pack-of-12 product, never 10. | valid quantity, round quantity |
| **Volume discount** | The one pricing rule: a line whose `quantity` is **strictly greater than 50** earns 10% off that line. Applies per line, not per order. A quantity of exactly 50 earns nothing. | bulk discount, tier, promotion, rebate |
| **Discount rate** | The fraction taken off a line — `0.10` when the volume discount applies, `0.0` otherwise. A rate, never an amount. | discount, markdown |
| **Discount amount** | The money the discount rate takes off a line, rounded to 2dp. | discount, saving |
| **Line total** | What one order line is charged: `unit_price × quantity` less the discount amount. Already rounded. | subtotal, extended price, amount |
| **Order total** | The sum of the order's line totals. The sum of *rounded* line totals — see ADR 002. | grand total, subtotal, sum |

## Conventions

- **Code uses the schema's `snake_case` names** — `order_line`, `pack_size`, `customer_id`. The frontend mirrors them as-is in its TypeScript interfaces rather than renaming to camelCase, because there is no codegen layer to do the translation and a hand-mapped rename is a bug surface.
- **A new term is added here before it is added to code**, not after — that ordering is the whole point of the file.
