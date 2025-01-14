from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from src.depends import get_user
from src.models import Cart, CartItem
from src.schemas import CartItemCreate
from src.services import get_product

cart_router = APIRouter(tags=["carts"])


@cart_router.get("/carts/")
async def get_full_cart(
    user: Annotated[get_user, Depends()]
):
    """Получение корзины"""
    cart = await Cart.find_first_by_kwargs(
        user_id=user.user_id,
        status='open'
    )
    if not cart:
        raise HTTPException(
            detail="Такой корзины нет в бд", status_code=status.HTTP_404_NOT_FOUND
        )
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=cart
    )


@cart_router.post("/carts/", status_code=201)
async def create_cart(user: Annotated[get_user, Depends()]):
    """Создание корзины"""
    cart = await Cart.find_first_by_kwargs(user_id=user.user_id)
    if not cart:
        cart = await Cart.create(user_id=user.user_id)
    return {
        "message": f"Получена корзина для пользователя {user}",
        "data": {
            "cart_id": cart.id,
        },
    }


@cart_router.post("/cart-lines/", status_code=201)
async def create_cartline(
    user: Annotated[get_user, Depends()],
    cart_item: Annotated[CartItemCreate, Body()],
):
    """Создание товара в корзине"""
    cart = await Cart.find_first_by_kwargs(user_id=user.user_id)
    product = await get_product(cart_item.product_id)
    cart_item.total_price = cart_item.quantity * product.price
    cart_item.price_per_item = product.price
    new_cart_item = await CartItem.create(**cart_item.model_dump(), cart_id=cart.id)
    
    return {
        "message": f"Товар {product.id} создан в корзине {new_cart_item.cart_id} для пользователя {user}",
        "data": {
            "cart": new_cart_item.cart_id,
            "product_id": new_cart_item.product_id,
            "total_price": new_cart_item.total_price,
        },
    }


@cart_router.delete("/api/cart-lines/add-item/")
async def delete_product(
    user: Annotated[get_user, Depends()],
    cart_id: Annotated[int, Body()],
    product_id: Annotated[int, Body()]
):
    cart_line_with_products = await CartItem.find_all_by_kwargs(
        cart_id=cart_id, product_id=product_id
    )
    product_count = len(cart_line_with_products)

    for cart_line in cart_line_with_products:
        await cart_line.delete()

    return {
        "message": f"Deleted product {product_count} from cart {cart_id}"
    }
