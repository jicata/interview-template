from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello_default():
    r = client.get('/hello')
    assert r.status_code == 200
    assert r.json()['message'] == 'Hello, World!'


def test_hello_with_name():
    r = client.get('/hello?name=Alice')
    assert r.status_code == 200
    assert r.json()['message'] == 'Hello, Alice!'
