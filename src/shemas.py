from pydantic import BaseModel
from typing import List

class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    price_per_item: float
    total_price: float

    class Config:
        orm_mode = True

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    cart_id: int

    class Config:
        orm_mode = True

class CartBase(BaseModel):
    user_id: int
    total_price: float

    class Config:
        orm_mode = True

class CartCreate(CartBase):
    pass

class CartSchema(CartBase):
    id: int
    items: List[CartItem] = []

    class Config:
        orm_mode = True
       