from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_products_returns_the_seeded_catalogue():
    response = client.get('/products')

    assert response.status_code == 200
    products = response.json()
    assert len(products) == 5
    assert {p['sku'] for p in products} == {
        'WIDG-A',
        'WIDG-B',
        'SUPP-Z',
        'GADG-X',
        'GADG-Y',
    }


def test_each_product_carries_the_pack_size_the_form_needs():
    products = {p['sku']: p for p in client.get('/products').json()}

    assert products['WIDG-A']['pack_size'] == 12
    assert products['WIDG-A']['unit_price'] == 10.00
    assert products['SUPP-Z']['pack_size'] == 1
