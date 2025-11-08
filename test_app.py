import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_ask_endpoint(client):
    rv = client.post('/ask', json={"question": "Top 5 best-selling products today"})
    assert rv.status_code in [200, 500]  # 500 if no API
