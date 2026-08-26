import pytest
from fastapi.testclient import TestClient

from app.db import get_connection, transaction
from app.features.draft import queries as draft_queries
from app.main import app

client = TestClient(app)

ACME = 1
BETA_CORP = 2
WIDGET_A = 1  # unit_price 10.00, pack_size 12
WIDGET_B = 2  # unit_price 15.00, pack_size 6
UNKNOWN_PRODUCT = 999
UNKNOWN_CUSTOMER = 99
ACME_DRAFT_ORDER_ID = 19


def _orders_count():
    return get_connection().execute('SELECT COUNT(*) AS n FROM orders').fetchone()['n']


def test_save_one_line_for_acme_adds_to_existing_draft_no_new_order():
    before = _orders_count()

    r = client.post(
        f'/customers/{ACME}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    assert r.status_code == 200
    body = r.json()
    assert body['id'] == ACME_DRAFT_ORDER_ID
    assert body['customer_id'] == ACME
    assert _orders_count() == before


def test_save_one_line_for_beta_corp_creates_empty_draft_then_adds_line():
    r = client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    assert r.status_code == 200
    body = r.json()
    assert body['customer_id'] == BETA_CORP
    assert body['status'] == 'draft'
    assert len(body['lines']) == 1
    assert body['lines'][0]['product_id'] == WIDGET_A
    assert body['lines'][0]['quantity'] == 12


def test_saving_same_product_again_in_later_request_increments_existing_row():
    client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    r = client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    assert r.status_code == 200
    body = r.json()
    assert len(body['lines']) == 1
    assert body['lines'][0]['quantity'] == 24


def test_same_product_twice_in_one_batch_is_summed_before_writing():
    r = client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={
            'lines': [
                {'product_id': WIDGET_A, 'quantity': 12},
                {'product_id': WIDGET_A, 'quantity': 12},
            ]
        },
    )

    assert r.status_code == 200
    body = r.json()
    assert len(body['lines']) == 1
    assert body['lines'][0]['quantity'] == 24


def test_written_unit_price_matches_product_price_and_is_not_derived_on_read():
    r = client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    assert r.status_code == 200
    line = r.json()['lines'][0]
    assert line['unit_price'] == 10.00

    stored = get_connection().execute(
        'SELECT unit_price FROM order_lines WHERE order_id = ? AND product_id = ?',
        (r.json()['id'], WIDGET_A),
    ).fetchone()
    assert stored['unit_price'] == 10.00


def test_stored_unit_price_is_historical_not_refreshed_from_products():
    # order_lines.unit_price equals products.unit_price for every seeded
    # row, which hides the historical-vs-current distinction from any test
    # that only ever writes at the seeded price. Mutating the product's
    # price between two writes makes the two values genuinely diverge, so
    # this actually fails if `read_draft_order` were ever changed to join
    # `products` for `unit_price` instead of selecting the frozen value off
    # `order_lines`.
    client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    with transaction() as tx:
        tx.execute('UPDATE products SET unit_price = 99.00 WHERE id = ?', (WIDGET_A,))
    try:
        r = client.post(
            f'/customers/{BETA_CORP}/draft/lines',
            json={'lines': [{'product_id': WIDGET_B, 'quantity': 6}]},
        )
        assert r.status_code == 200
        line = next(l for l in r.json()['lines'] if l['product_id'] == WIDGET_A)
        assert line['unit_price'] == 10.00  # historical, not the now-current 99.00
    finally:
        with transaction() as tx:
            tx.execute('UPDATE products SET unit_price = 10.00 WHERE id = ?', (WIDGET_A,))


def test_a_failure_after_the_first_write_rolls_back_everything(monkeypatch):
    # Validation completes before the first write, so no test reaching this
    # endpoint through the API can otherwise force a failure mid-batch — the
    # rollback path (the repo's one planted defect, b0a7929) would stay
    # unguarded without this. Forces `insert_line`'s second call to raise,
    # after the draft has already been created and the first line written,
    # and asserts db.transaction() actually discarded both.
    real_insert_line = draft_queries.insert_line
    calls = {'n': 0}

    def failing_insert_line(conn, order_id, product_id, quantity, unit_price):
        calls['n'] += 1
        if calls['n'] == 2:
            raise RuntimeError('simulated failure after the first write')
        return real_insert_line(conn, order_id, product_id, quantity, unit_price)

    monkeypatch.setattr(draft_queries, 'insert_line', failing_insert_line)

    before_orders = _orders_count()

    with pytest.raises(RuntimeError):
        client.post(
            f'/customers/{BETA_CORP}/draft/lines',
            json={
                'lines': [
                    {'product_id': WIDGET_A, 'quantity': 12},
                    {'product_id': WIDGET_B, 'quantity': 6},
                ]
            },
        )

    assert _orders_count() == before_orders, 'the phantom draft must be rolled back too'
    draft_lines = get_connection().execute(
        "SELECT ol.* FROM order_lines ol JOIN orders o ON o.id = ol.order_id "
        "WHERE o.customer_id = ? AND o.status = 'draft'",
        (BETA_CORP,),
    ).fetchall()
    assert draft_lines == []


def test_batch_with_unknown_product_id_as_last_item_writes_nothing():
    before_orders = _orders_count()

    r = client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={
            'lines': [
                {'product_id': WIDGET_A, 'quantity': 12},
                {'product_id': UNKNOWN_PRODUCT, 'quantity': 5},
            ]
        },
    )

    assert r.status_code == 422
    assert _orders_count() == before_orders
    draft_lines = get_connection().execute(
        "SELECT ol.* FROM order_lines ol JOIN orders o ON o.id = ol.order_id "
        "WHERE o.customer_id = ? AND o.status = 'draft'",
        (BETA_CORP,),
    ).fetchall()
    assert draft_lines == []


def test_unknown_customer_id_is_404_and_creates_no_order():
    before = _orders_count()

    r = client.post(
        f'/customers/{UNKNOWN_CUSTOMER}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 12}]},
    )

    assert r.status_code == 404
    assert _orders_count() == before


def test_empty_line_list_is_422():
    r = client.post(f'/customers/{ACME}/draft/lines', json={'lines': []})
    assert r.status_code == 422


def test_zero_or_negative_quantity_is_422():
    r_zero = client.post(
        f'/customers/{ACME}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': 0}]},
    )
    r_negative = client.post(
        f'/customers/{ACME}/draft/lines',
        json={'lines': [{'product_id': WIDGET_A, 'quantity': -1}]},
    )

    assert r_zero.status_code == 422
    assert r_negative.status_code == 422


def test_response_carries_draft_order_and_its_lines():
    r = client.post(
        f'/customers/{BETA_CORP}/draft/lines',
        json={'lines': [{'product_id': WIDGET_B, 'quantity': 6}]},
    )

    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {'id', 'customer_id', 'status', 'lines'}
    assert set(body['lines'][0].keys()) == {'product_id', 'name', 'sku', 'quantity', 'unit_price'}
    assert body['lines'][0]['name'] == 'Widget B'
    assert body['lines'][0]['sku'] == 'WIDG-B'
