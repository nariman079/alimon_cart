import json

import pytest
from fastapi.testclient import TestClient

from src.conf.settings import redis
from src.main import app
from src.schemas import CartItemCreate
from src.services import get_product

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.OXRl_urG-myPUh7RDv4Q7XalDMgAnk_21YIEez5oulI'

@pytest.fixture
def redis_connection():
    for i in range(1,10):
        redis.set(str(i), json.dumps(dict(id=i, price=i*20, name=f"{i}Name")))
    return redis

@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as client:
        yield client

def test_create_cart(redis_connection, client):
    response = client.post(
        "/api/carts/",
        headers={
            "Authorization":f"Bearer {token}"
        }
    )
    assert response.status_code == 201
    assert "Получена корзина" in response.json()['message']
    
@pytest.mark.asyncio
async def test_add_cart_item(client):

    cart_item = CartItemCreate(
        product_id=1,
        quantity=1
    )
    response = client.post(
        "/api/cart-lines/",
        json=cart_item.dict(),
        headers={
            "Authorization":f"Bearer {token}"
        }
    )
    product = await get_product(cart_item.product_id)
    assert response.status_code == 201
    assert f"Товар {product.id} создан в корзине" in response.json()['message'] 
    assert response.json()['data']['total_price'] == product.price * cart_item.quantity
    
    
redis.delete(*range(1,10))