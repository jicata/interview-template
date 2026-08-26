"""Pricing rules, tested with no database at all.

That is the point of `pricing.py` being pure: a layered architecture's one real
cost is that business rules need infrastructure to test, and this file is the
proof it was bought back. If any test here needs a fixture, the module leaked.
"""
from decimal import Decimal

import pytest

from app.features.orders import pricing


def d(value: str) -> Decimal:
    return Decimal(value)


@pytest.mark.parametrize(
    'unit_price, quantity, expected_rate, expected_discount, expected_total',
    [
        # Widget A, pack of 12 — four packs stays under the threshold.
        ('10.00', 48, '0', '0.00', '480.00'),
        # Five packs crosses it.
        ('10.00', 60, '0.10', '60.00', '540.00'),
        # Supply Z, pack of 1 — the threshold is strict, so exactly 50 earns nothing.
        ('25.00', 50, '0', '0.00', '1250.00'),
        ('25.00', 51, '0.10', '127.50', '1147.50'),
        # Gadget X, pack of 4 — thirteen packs.
        ('50.00', 52, '0.10', '260.00', '2340.00'),
        # A single pack of a cheap product: no discount, no rounding to do.
        ('15.00', 6, '0', '0.00', '90.00'),
    ],
)
def test_price_line(unit_price, quantity, expected_rate, expected_discount, expected_total):
    line = pricing.price_line(d(unit_price), quantity)

    assert line.discount_rate == d(expected_rate)
    assert line.discount_amount == d(expected_discount)
    assert line.line_total == d(expected_total)


def test_discount_applies_strictly_above_the_threshold():
    assert pricing.DISCOUNT_THRESHOLD_UNITS == 50
    assert pricing.price_line(d('1.00'), 50).discount_rate == d('0')
    assert pricing.price_line(d('1.00'), 51).discount_rate == d('0.10')


def test_discount_amount_rounds_half_up_to_the_cent():
    # gross 50.49 -> discount 5.049, which must round UP to 5.05, not down to 5.04.
    line = pricing.price_line(d('0.99'), 51)

    assert line.discount_amount == d('5.05')
    assert line.line_total == d('45.44')


def test_line_total_carries_two_decimal_places_exactly():
    line = pricing.price_line(d('0.99'), 51)

    assert line.line_total.as_tuple().exponent == -2


def test_order_total_sums_already_rounded_line_totals():
    lines = [pricing.price_line(d('10.00'), 60), pricing.price_line(d('15.00'), 6)]

    assert pricing.order_total(lines) == d('630.00')


def test_order_total_is_the_sum_of_rounded_lines_not_the_rounding_of_a_sum():
    """ADR 002's rounding decision, made falsifiable.

    Each line grosses 61.05, discounts 6.105 -> 6.11, so charges 54.94. Summing
    the charges gives 109.88. Summing *unrounded* lines gives 109.89. The order
    total must equal what the lines actually charge, so the customer can add up
    the column and get the same answer.
    """
    lines = [pricing.price_line(d('1.11'), 55), pricing.price_line(d('1.11'), 55)]

    assert pricing.order_total(lines) == d('109.88')
    assert pricing.order_total(lines) != d('109.89')


def test_order_total_of_an_empty_order_is_zero():
    assert pricing.order_total([]) == d('0.00')
