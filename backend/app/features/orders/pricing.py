"""Order-line pricing rules.

Pure by construction: this module imports nothing from `app.db`, takes no
connection, and knows nothing about rows. It is the one place the volume-discount
rule and the rounding policy live. See `docs/adr/002-pricing-derived-not-stored.md`.
"""
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

#: A line earns the volume discount when its quantity is *strictly* greater than
#: this. Exactly 50 earns nothing.
DISCOUNT_THRESHOLD_UNITS = 50
DISCOUNT_RATE = Decimal('0.10')

NO_DISCOUNT = Decimal('0')
_CENTS = Decimal('0.01')
_ZERO = Decimal('0.00')


@dataclass(frozen=True, slots=True)
class PricedLine:
    """What one order line is charged. All money already rounded to the cent."""

    quantity: int
    unit_price: Decimal
    discount_rate: Decimal
    discount_amount: Decimal
    line_total: Decimal


def discount_rate_for(quantity: int) -> Decimal:
    return DISCOUNT_RATE if quantity > DISCOUNT_THRESHOLD_UNITS else NO_DISCOUNT


def price_line(unit_price: Decimal, quantity: int) -> PricedLine:
    """Price one line: unit price x quantity, less the volume discount."""
    gross = _to_cents(unit_price * quantity)
    rate = discount_rate_for(quantity)
    discount_amount = _to_cents(gross * rate)
    return PricedLine(
        quantity=quantity,
        unit_price=unit_price,
        discount_rate=rate,
        discount_amount=discount_amount,
        line_total=gross - discount_amount,
    )


def order_total(lines: Iterable[PricedLine]) -> Decimal:
    """Sum what the lines actually charge — not the rounding of an unrounded sum.

    The distinction is worth a cent or two on a long order, and it is the
    difference between a total the customer can verify by adding up the column
    and one they cannot. ADR 002.
    """
    return sum((line.line_total for line in lines), _ZERO)


def _to_cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENTS, rounding=ROUND_HALF_UP)
