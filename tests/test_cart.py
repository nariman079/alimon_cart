import json

import pytest
from fastapi.testclient import TestClient

from src.conf.settings import redis
from src.main import app
from src.schemas import CartItemCreate
from src.services import get_product

from tests.utils import assert_response

@pytest.fixture
def redis_connection():
    for i in range(1, 10):
        redis.set(str(i), json.dumps(dict(id=i, price=i * 20, name=f"{i}Name")))
    return redis


@pytest.fixture
def headers():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.OXRl_urG-myPUh7RDv4Q7XalDMgAnk_21YIEez5oulI"

    return {
        'Authorization': f"Bearer {token}"
    }

@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as client:
        yield client


def test_create_cart(redis_connection, client, headers):
    assert_response(
        client.post("/api/carts/", headers=headers),
        expected_code=201,
        expected_data={
            'message':"Корзина создана"
        }
    )
    
@pytest.mark.asyncio
async def test_create_cart_item(client, headers):
    cart_item = CartItemCreate(product_id=1, quantity=1)
    response = client.post(
        "/api/cart-lines/",
        json=cart_item.model_dump(),
        headers=headers,
    )
    product = await get_product(cart_item.product_id)

    assert_response(
        response,
        expected_code=201,
        expected_data={
            'message':"Товар создан в корзине"
        }
    )

    assert response.json()["data"]["total_price"] == product.price * cart_item.quantity


@pytest.mark.asyncio
async def test_add_item_in_cartitem_by_exists(client, headers):
    product_id = 1
    request_data = {
            'product_id': product_id
        }
    
    client.post(
        "/api/cart-lines/add-item/",
        json=request_data,
        headers=headers
    )
    response = client.post(
        "/api/cart-lines/add-item/",
        json=request_data,
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["message"] == f"Увеличение количества товара {request_data['product_id']}"
    assert response.json()['data']['product_id'] == request_data['product_id']
    assert response.json()['data']['total_price'] == 60
    assert response.json()['data']['quantity'] == 3
 
@pytest.mark.asyncio
async def test_add_item_in_cartitem_by_not_exists_item(client, headers):
    product_id = 3
    request_data = {
            'product_id': product_id
        }
    response = client.post(
        "/api/cart-lines/add-item/",
        json=request_data,
        headers=headers
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio 
async def test_decrease_item_from_cart(client, headers):
    assert_response(
        client.post(
            '/api/cart-items/decrease-item/',
            headers=headers,
            json={'product_id': 1}
        ),
        expected_code=201,
        expected_data={
            'message': "Уменьшение количества товара в корзине",
            'dict': {
                'total_price':40.0,
                'quantity': 2
            }
        }
    )


redis.delete(*range(1, 10))
