from datetime import date

import pytest

from app.features.reorder.cadence import suggest


def _row(product_id, name, sku, pack_size, unit_price, order_date):
    return {
        'product_id': product_id,
        'name': name,
        'sku': sku,
        'pack_size': pack_size,
        'unit_price': unit_price,
        'order_date': order_date,
    }


def test_single_pair_overdue_by_six_days():
    rows = [
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-04-03'),  # 92 days later
    ]
    result = suggest(rows, as_of=date(2026, 7, 10))  # 6 days past projected due date

    assert len(result) == 1
    assert result[0].product_id == 1
    assert result[0].days_overdue == 6


def test_cadence_is_mean_of_gaps_not_last_gap():
    # Gaps: Jan 1 -> Jan 31 = 30 days; Jan 31 -> Mar 22 = 50 days. Mean = 40.
    # Last order + mean(40) = May 1; last order + last-gap(50) would be May 11 —
    # the two diverge, so the assertion below only passes if the mean is used.
    rows = [
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-31'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-03-22'),
    ]
    result = suggest(rows, as_of=date(2026, 5, 5))

    assert result[0].cadence_days == 40
    assert result[0].days_overdue == 4


def test_single_completed_order_is_excluded():
    rows = [_row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01')]
    result = suggest(rows, as_of=date(2026, 12, 1))

    assert result == []


def test_not_yet_due_pair_is_excluded():
    rows = [
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-02-01'),  # cadence 31
    ]
    result = suggest(rows, as_of=date(2026, 2, 5))  # next due 2026-03-04, not yet

    assert result == []


def test_due_exactly_on_as_of_is_included():
    rows = [
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-02-01'),  # cadence 31 -> next due 2026-03-04
    ]
    result = suggest(rows, as_of=date(2026, 3, 4))

    assert len(result) == 1
    assert result[0].days_overdue == 0


def test_most_overdue_first():
    rows = [
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-02-01'),  # cadence 31, due 2026-03-04
        _row(2, 'Widget B', 'WIDG-B', 6, 15.0, '2025-12-01'),
        _row(2, 'Widget B', 'WIDG-B', 6, 15.0, '2025-12-31'),  # cadence 30, due 2026-01-30
    ]
    result = suggest(rows, as_of=date(2026, 4, 1))

    assert [r.product_id for r in result] == [2, 1]


def test_suggested_quantity_is_pack_size():
    rows = [
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-01-01'),
        _row(1, 'Widget A', 'WIDG-A', 12, 10.0, '2026-02-01'),
    ]
    result = suggest(rows, as_of=date(2026, 4, 1))

    assert result[0].suggested_quantity == 12


def test_empty_input_returns_empty_list():
    assert suggest([], as_of=date(2026, 1, 1)) == []


# Real seeded pairs, as of 2026-08-26 (backend/data/orders.csv,
# order_lines.csv, products.csv). Expected values are literals derived
# independently from the CSVs, not recomputed the way the implementation
# computes them. Supply Z's gaps are 30 and 28 (February 2026 has 28 days),
# so its mean of 29 is exact — this pins that the seed data does not exercise
# Python's banker's rounding on a `.5` mean, per issue #2's sharp edges.
@pytest.mark.parametrize(
    'product_id, name, sku, pack_size, unit_price, order_dates, expected_cadence, expected_next_due, expected_overdue',
    [
        (
            1, 'Widget A', 'WIDG-A', 12, 10.00,
            ['2025-09-01', '2025-11-01', '2026-01-15', '2026-03-20'],
            67, date(2026, 5, 26), 92,
        ),
        (
            2, 'Widget B', 'WIDG-B', 6, 15.00,
            ['2025-08-01', '2025-11-01', '2026-02-01'],
            92, date(2026, 5, 4), 114,
        ),
        (
            3, 'Supply Z', 'SUPP-Z', 1, 25.00,
            ['2026-01-05', '2026-02-04', '2026-03-04'],
            29, date(2026, 4, 2), 146,
        ),
        (
            4, 'Gadget X', 'GADG-X', 4, 50.00,
            ['2025-10-01', '2025-11-15', '2025-12-30', '2026-02-10', '2026-03-25', '2026-05-05'],
            43, date(2026, 6, 17), 70,
        ),
        (
            5, 'Gadget Y', 'GADG-Y', 1, 75.00,
            ['2025-10-01', '2026-02-05'],
            127, date(2026, 6, 12), 75,
        ),
    ],
)
def test_all_five_seeded_pairs(
    product_id, name, sku, pack_size, unit_price,
    order_dates, expected_cadence, expected_next_due, expected_overdue,
):
    rows = [
        _row(product_id, name, sku, pack_size, unit_price, order_date)
        for order_date in order_dates
    ]
    result = suggest(rows, as_of=date(2026, 8, 26))

    assert len(result) == 1
    suggestion = result[0]
    assert suggestion.cadence_days == expected_cadence
    assert suggestion.next_due_date == expected_next_due
    assert suggestion.days_overdue == expected_overdue
