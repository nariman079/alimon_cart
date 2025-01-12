import json

import pytest
from fastapi.testclient import TestClient

from src.conf.settings import redis
from src.main import app

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.OXRl_urG-myPUh7RDv4Q7XalDMgAnk_21YIEez5oulI'

@pytest.fixture
def redis_connection():
    for i in range(1,10):
        redis.set(str(i), json.dumps(dict(id=i, price=i*20, name=f"{i}Name")))
    return redis


def test_add_to_cart(redis_connection):
    client = TestClient(app)
    response = client.post(
        "/api/carts/",
        headers={
            "Authorization":f"Bearer {token}"
        }
    )
    assert response.status_code == 201
    assert "Получена корзина" in response.json()['message']
    
