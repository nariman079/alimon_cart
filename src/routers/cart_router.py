from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from src.depends import get_user
from src.models import Cart, CartItem
from src.schemas import CartItemCreate
from src.services import get_product

cart_router = APIRouter(tags=["carts"])

async def get_user_cart(user_id: int) -> Cart:
    """Получение корзины пользователя"""
    return await Cart.find_first_by_kwargs(status='open', user_id=user_id)

@cart_router.get("/carts/")
async def get_full_cart(
    user: Annotated[get_user, Depends()]
):
    """Получение корзины"""
    user_cart = await get_user_cart(user.user_id)
    if not user_cart:
        raise HTTPException(
            detail="Такой корзины нет в бд", status_code=status.HTTP_404_NOT_FOUND
        )
    return user_cart


@cart_router.post(
    "/carts/", 
    status_code=status.HTTP_201_CREATED
)
async def create_cart(user: Annotated[get_user, Depends()]):
    """Создание корзины"""
    cart = await Cart.find_first_by_kwargs(user_id=user.user_id)
    if not cart:
        cart = await Cart.create(user_id=user.user_id)
    return {
        "message": f"Корзина создана",
        "data": {
            "cart_id": cart.id,
        },
    }


@cart_router.post(
    "/cart-items/", 
    status_code=status.HTTP_201_CREATED
    )
async def create_cartline(
    user: Annotated[get_user, Depends()],
    cart_item: Annotated[CartItemCreate, Body()],
):
    """Создание товара в корзине"""
    cart = await get_user_cart(user.user_id)
    product = await get_product(cart_item.product_id)
    cart_item.total_price = cart_item.quantity * product.price
    cart_item.price_per_item = product.price
    new_cart_item = await CartItem.create(**cart_item.model_dump(), cart_id=cart.id)
    
    return {
        "message": f"Товар создан в корзине",
        "data": {
            "cart": new_cart_item.cart_id,
            "product_id": new_cart_item.product_id,
            "total_price": new_cart_item.total_price,
        },
    }


@cart_router.post(
    "/cart-items/increase-item/", 
    status_code=status.HTTP_201_CREATED
)
async def delete_product(
    user: Annotated[get_user, Depends()],
    product_id: Annotated[int, Body(embed=True)]
):
    user_cart = await get_user_cart(user.user_id)
    cart_item = await CartItem.find_first_by_kwargs(
        cart_id=user_cart.id, product_id=product_id
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого товара нет в корзине"
        )

    await cart_item.update(
        total_price=cart_item.total_price + cart_item.price_per_item,
        quantity=cart_item.quantity + 1
    )
    
    return {
        "message": f"Увеличение количества товара",
        "data": {
            "product_id": cart_item.product_id,
            "total_price": cart_item.total_price,
            "quantity": cart_item.quantity
        }
    }

@cart_router.post(
    "/cart-items/decrease-item/", 
    status_code=status.HTTP_201_CREATED
)
async def decrease_cart_item(
    user: Annotated[get_user, Depends()],
    product_id: Annotated[int, Body(embed=True)]
):
    """Уменьшение количества товара"""
    user_cart = await get_user_cart(user_id=user.user_id)
    cart_item = await CartItem.find_first_by_kwargs(
        product_id=product_id, cart_id=user_cart.id
    )
    if not cart_item:
        raise HTTPException(
            detail="Такого товара нет в корзине",
            status_code=status.HTTP_404_NOT_FOUND
        )
    await cart_item.update(
        total_price=cart_item.total_price - cart_item.price_per_item,
        quantity=cart_item.quantity - 1
    )
    return {
        'message': "Уменьшение количества товара в корзине",
        'dict': {
            'total_price':cart_item.total_price,
            'quantity': cart_item.quantity
        }
    }