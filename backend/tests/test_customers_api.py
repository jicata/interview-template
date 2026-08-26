from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lists_seeded_customers_ordered_by_name():
    r = client.get('/customers')
    assert r.status_code == 200
    body = r.json()
    assert [c['name'] for c in body] == ['Acme', 'Beta Corp', 'Gamma LLC']


def test_response_carries_every_declared_field():
    r = client.get('/customers')
    body = r.json()[0]
    assert set(body.keys()) == {'id', 'name', 'email'}
