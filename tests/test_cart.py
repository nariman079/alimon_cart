import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.conf.settings import redis

@pytest.fixture
def redis_connection():
    redis.set("1", '{"id": 1, "price": 100, "name":"test"}')
    return redis

def test_add_to_cart(redis_connection):
    client = TestClient(app)
    response = client.post("/api/carts/2/cart-lines/?user_id=1", json={"product_id": 1, "quantity": 3})

    assert response.status_code == 200
    raise ValueError(response.json()['data'])
