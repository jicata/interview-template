"""Pure reorder-cadence inference — no database import, no clock read.

Takes already-fetched completed-order rows and a reference date, and reports
which customer/product pairs are due to reorder and how overdue each is.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import groupby


@dataclass(frozen=True, slots=True)
class Suggestion:
    product_id: int
    name: str
    sku: str
    pack_size: int
    unit_price: float
    last_order_date: date
    cadence_days: int
    next_due_date: date
    days_overdue: int
    suggested_quantity: int


def suggest(rows: list[dict], as_of: date) -> list[Suggestion]:
    """Infer reorder suggestions from completed-order rows.

    Each row carries `product_id`, `name`, `sku`, `pack_size`, `unit_price`
    and `order_date` (ISO string) for one completed order line. A
    product_id with fewer than two rows has no gap to average and is
    excluded, not defaulted to an assumed cadence.
    """
    by_product = sorted(rows, key=lambda r: (r['product_id'], r['order_date']))
    grouped = (list(group) for _, group in groupby(by_product, key=lambda r: r['product_id']))

    due = []
    for product_rows in grouped:
        if len(product_rows) < 2:
            continue
        suggestion = _suggest_for_product(product_rows, as_of)
        if suggestion.days_overdue >= 0:
            due.append(suggestion)
    return sorted(due, key=lambda s: s.days_overdue, reverse=True)


def _suggest_for_product(rows: list[dict], as_of: date) -> Suggestion:
    order_dates = [date.fromisoformat(r['order_date']) for r in rows]
    gaps = [
        (later - earlier).days
        for earlier, later in zip(order_dates, order_dates[1:])
    ]
    cadence_days = round(sum(gaps) / len(gaps))
    last_order_date = order_dates[-1]
    next_due_date = last_order_date + timedelta(days=cadence_days)
    last_row = rows[-1]

    return Suggestion(
        product_id=last_row['product_id'],
        name=last_row['name'],
        sku=last_row['sku'],
        pack_size=last_row['pack_size'],
        unit_price=last_row['unit_price'],
        last_order_date=last_order_date,
        cadence_days=cadence_days,
        next_due_date=next_due_date,
        days_overdue=(as_of - next_due_date).days,
        suggested_quantity=last_row['pack_size'],
    )
