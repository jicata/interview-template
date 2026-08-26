"""The Order Builder through HTTP — routing, validation and serialization included.

Seed facts these tests lean on (`backend/data/*.csv`):
  order 19  — the only draft, customer 1, no lines
  order 1   — completed
  product 1 — Widget A, 10.00, pack of 12
  product 2 — Widget B, 15.00, pack of 6
  product 3 — Supply Z, 25.00, pack of 1
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

DRAFT_ORDER = 19
COMPLETED_ORDER = 1
WIDGET_A = 1
WIDGET_B = 2
SUPPLY_Z = 3


def add_line(order_id: int, product_id: int, quantity: int):
    return client.post(
        f'/orders/{order_id}/lines',
        json={'product_id': product_id, 'quantity': quantity},
    )


# --- reading an order back -------------------------------------------------


def test_the_seeded_draft_starts_empty_and_totals_zero():
    response = client.get(f'/orders/{DRAFT_ORDER}')

    assert response.status_code == 200
    order = response.json()
    assert order['status'] == 'draft'
    assert order['order_date'] is None
    assert order['lines'] == []
    assert order['order_total'] == 0.0


def test_reading_an_unknown_order_is_a_404():
    response = client.get('/orders/9999')

    assert response.status_code == 404
    assert 'No order with id 9999' in response.json()['detail']


# --- adding lines ----------------------------------------------------------


def test_adding_two_packs_prices_the_line_without_a_discount():
    response = add_line(DRAFT_ORDER, WIDGET_A, 24)

    assert response.status_code == 201
    (line,) = response.json()['lines']
    assert line['product_name'] == 'Widget A'
    assert line['quantity'] == 24
    assert line['unit_price'] == 10.00
    assert line['discount_rate'] == 0.0
    assert line['discount_amount'] == 0.0
    assert line['line_total'] == 240.00
    assert response.json()['order_total'] == 240.00


def test_a_line_over_fifty_units_earns_the_volume_discount():
    response = add_line(DRAFT_ORDER, WIDGET_A, 60)

    (line,) = response.json()['lines']
    assert line['discount_rate'] == 0.1
    assert line['discount_amount'] == 60.00
    assert line['line_total'] == 540.00


def test_exactly_fifty_units_earns_nothing():
    # Supply Z ships in packs of 1, so 50 is orderable and lands on the boundary.
    response = add_line(DRAFT_ORDER, SUPPLY_Z, 50)

    (line,) = response.json()['lines']
    assert line['discount_rate'] == 0.0
    assert line['line_total'] == 1250.00


def test_fifty_one_units_earns_the_discount():
    response = add_line(DRAFT_ORDER, SUPPLY_Z, 51)

    (line,) = response.json()['lines']
    assert line['discount_rate'] == 0.1
    assert line['line_total'] == 1147.50


def test_the_order_total_is_the_sum_of_its_line_totals():
    add_line(DRAFT_ORDER, WIDGET_A, 60)
    response = add_line(DRAFT_ORDER, WIDGET_B, 6)

    order = response.json()
    assert [line['line_total'] for line in order['lines']] == [540.00, 90.00]
    assert order['order_total'] == 630.00


# --- the pack-size rule ----------------------------------------------------


def test_a_quantity_that_is_not_a_whole_number_of_packs_is_rejected():
    response = add_line(DRAFT_ORDER, WIDGET_A, 10)

    assert response.status_code == 422
    expected = (
        'Widget A ships in packs of 12, so 10 cannot be ordered. '
        'Use a multiple of 12.'
    )
    assert response.json()['detail'] == expected


def test_a_rejected_line_is_not_written():
    add_line(DRAFT_ORDER, WIDGET_A, 10)

    assert client.get(f'/orders/{DRAFT_ORDER}').json()['lines'] == []


def test_zero_and_negative_quantities_are_rejected_before_the_handler():
    # 0 % pack_size == 0, so the pack rule alone would let zero through — the
    # Field(gt=0) constraint is what stops it.
    assert add_line(DRAFT_ORDER, WIDGET_A, 0).status_code == 422
    assert add_line(DRAFT_ORDER, WIDGET_A, -12).status_code == 422
    assert client.get(f'/orders/{DRAFT_ORDER}').json()['lines'] == []


def test_adding_an_unknown_product_is_a_404():
    response = add_line(DRAFT_ORDER, 9999, 12)

    assert response.status_code == 404
    assert 'No product with id 9999' in response.json()['detail']


def test_adding_to_an_unknown_order_is_a_404():
    assert add_line(9999, WIDGET_A, 12).status_code == 404


def test_a_completed_order_cannot_be_built_on():
    response = add_line(COMPLETED_ORDER, WIDGET_A, 12)

    assert response.status_code == 409
    assert 'completed' in response.json()['detail']


# --- adding a product twice ------------------------------------------------


def test_adding_the_same_product_again_grows_its_line():
    add_line(DRAFT_ORDER, WIDGET_A, 24)
    response = add_line(DRAFT_ORDER, WIDGET_A, 36)

    lines = response.json()['lines']
    assert len(lines) == 1
    assert lines[0]['quantity'] == 60


def test_a_merged_line_earns_the_discount_the_combined_quantity_deserves():
    add_line(DRAFT_ORDER, WIDGET_A, 24)
    response = add_line(DRAFT_ORDER, WIDGET_A, 36)

    (line,) = response.json()['lines']
    assert line['discount_rate'] == 0.1
    assert line['line_total'] == 540.00
    assert response.json()['order_total'] == 540.00


# --- removing lines --------------------------------------------------------


def test_removing_a_line_recomputes_the_total():
    add_line(DRAFT_ORDER, WIDGET_A, 60)
    order = add_line(DRAFT_ORDER, WIDGET_B, 6).json()
    widget_a_line = next(
        line for line in order['lines'] if line['product_id'] == WIDGET_A
    )

    response = client.delete(
        f'/orders/{DRAFT_ORDER}/lines/{widget_a_line["id"]}'
    )

    assert response.status_code == 200
    remaining = response.json()
    assert [line['product_id'] for line in remaining['lines']] == [WIDGET_B]
    assert remaining['order_total'] == 90.00


def test_removing_the_last_line_returns_the_order_to_zero():
    line_id = add_line(DRAFT_ORDER, WIDGET_A, 12).json()['lines'][0]['id']

    response = client.delete(f'/orders/{DRAFT_ORDER}/lines/{line_id}')

    assert response.json()['lines'] == []
    assert response.json()['order_total'] == 0.0


def test_removing_a_line_that_is_not_on_the_order_is_a_404():
    response = client.delete(f'/orders/{DRAFT_ORDER}/lines/9999')

    assert response.status_code == 404


def test_a_line_cannot_be_removed_through_the_wrong_order():
    line_id = add_line(DRAFT_ORDER, WIDGET_A, 12).json()['lines'][0]['id']

    response = client.delete(f'/orders/{COMPLETED_ORDER}/lines/{line_id}')

    assert response.status_code == 409
    assert client.get(f'/orders/{DRAFT_ORDER}').json()['lines'][0]['id'] == line_id


# --- the write actually landed --------------------------------------------


def test_a_line_survives_the_response_that_created_it():
    """The total shown after a POST must be the total a fresh GET reports.

    A feature whose state only exists inside the write's own response is
    indistinguishable from one that never persisted anything.
    """
    written = add_line(DRAFT_ORDER, WIDGET_A, 60).json()

    read_back = client.get(f'/orders/{DRAFT_ORDER}').json()

    assert read_back == written


# --- creating orders ------------------------------------------------------


def test_creating_an_order_returns_an_empty_draft():
    response = client.post('/orders', json={'customer_id': 1})

    assert response.status_code == 201
    order = response.json()
    assert order['status'] == 'draft'
    assert order['customer_id'] == 1
    assert order['order_date'] is None
    assert order['lines'] == []
    assert order['order_total'] == 0.0
    assert order['id'] != DRAFT_ORDER


def test_a_created_order_can_be_read_back_and_added_to():
    order_id = client.post('/orders', json={'customer_id': 2}).json()['id']

    assert add_line(order_id, WIDGET_B, 6).status_code == 201
    assert client.get(f'/orders/{order_id}').json()['order_total'] == 90.00


def test_creating_an_order_for_an_unknown_customer_is_a_404():
    response = client.post('/orders', json={'customer_id': 9999})

    assert response.status_code == 404
    assert 'No customer with id 9999' in response.json()['detail']


# --- the suite's own hygiene ---------------------------------------------


def test_the_seeded_draft_is_still_empty_after_every_test_above():
    """Guards the conftest fixture, not the app.

    This file writes to order 19 more than a dozen times against one shared
    module-level connection. If the restore fixture stopped working, the failure
    would otherwise show up as an unrelated test breaking somewhere downstream.
    """
    order = client.get(f'/orders/{DRAFT_ORDER}').json()

    assert order['lines'] == []
    assert order['order_total'] == 0.0
