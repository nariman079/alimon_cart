from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from src.depends import get_cart, get_user
from src.models import Cart, CartItem
from src.services import get_product

cart_router = APIRouter(tags=["carts"])


@cart_router.get("/carts/{cart_id}")
async def get_full_cart(cart_id: int):
    cart = await Cart.find_first_by_id(cart_id)
    if not cart:
        raise HTTPException(
            detail="Такой корзины нет в бд", status_code=status.HTTP_404_NOT_FOUND
        )
    return cart


@cart_router.post("/carts/")
async def create_cart(user: Annotated[int, Depends(get_user)]):
    """Get or create cart for user"""
    cart = await Cart.find_first_by_kwargs(user_id=user)
    if not cart:
        cart = await Cart.create(user_id=user)
    return {
        "message": f"Created cart for user {user}",
        "data": {
            "cart_id": cart.id,
        },
    }


@cart_router.post("/carts/{cart_id}/cart-lines/")
async def create_cartline(
    user: Annotated[get_user, Depends()],
    cart: Annotated[get_cart, Depends()],
    product_id: Annotated[int, Body()],
    price_per_item: Annotated[int, Body()],
    quantity: Annotated[int, Body()],
):
    product = await get_product(product_id)
    total_price = quantity * product.price
    cart_item = await CartItem.create(
        cart_id=cart,
        product_id=product_id,
        quantity=quantity,
        total_price=total_price,
        price_per_item=price_per_item,
    )
    return {
        "message": f"CartItem added on cart {cart} to user {user}",
        "data": {
            "cart": cart,
            "product_id": cart_item.product_id,
            "total_price": cart_item.total_price,
        },
    }


# @cart_router.post('/carts/')
# async def create_cart():
#     pass

# @cart_router.post('/carts/{cart_id}/cart-lines/')
# async def create_cartline():
#     pass
