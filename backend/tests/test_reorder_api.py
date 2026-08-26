from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_suggestions_for_customer_1_at_2026_05_10():
    # Widget B is due 2026-05-04 (cadence 92 from 2025-08-01, 2025-11-01,
    # 2026-02-01); Widget A is not due until 2026-05-26. Only Widget B shows.
    r = client.get('/customers/1/reorder-suggestions?as_of=2026-05-10')
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]['sku'] == 'WIDG-B'
    assert body[0]['days_overdue'] == 6


def test_suggestions_for_customer_1_at_2026_08_26_orders_most_overdue_first():
    r = client.get('/customers/1/reorder-suggestions?as_of=2026-08-26')
    assert r.status_code == 200
    body = r.json()
    skus = [s['sku'] for s in body]
    assert skus == ['WIDG-B', 'WIDG-A']
    assert body[0]['days_overdue'] == 114
    assert body[1]['days_overdue'] == 92


def test_as_of_before_all_seeded_orders_returns_empty_list():
    r = client.get('/customers/1/reorder-suggestions?as_of=2026-01-01')
    assert r.status_code == 200
    assert r.json() == []


def test_as_of_omitted_defaults_to_today():
    r = client.get('/customers/1/reorder-suggestions')
    assert r.status_code == 200


def test_malformed_as_of_is_422():
    r = client.get('/customers/1/reorder-suggestions?as_of=not-a-date')
    assert r.status_code == 422


def test_unknown_customer_is_404():
    r = client.get('/customers/99/reorder-suggestions?as_of=2026-08-26')
    assert r.status_code == 404


def test_response_carries_every_declared_field():
    r = client.get('/customers/1/reorder-suggestions?as_of=2026-08-26')
    body = r.json()[0]
    assert set(body.keys()) == {
        'product_id',
        'name',
        'sku',
        'pack_size',
        'unit_price',
        'last_order_date',
        'cadence_days',
        'next_due_date',
        'days_overdue',
        'suggested_quantity',
    }
