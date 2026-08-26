from fastapi.testclient import TestClient

from app.db import get_connection
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
