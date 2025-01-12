from pydantic import BaseModel


class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    price_per_item: float | None = None
    total_price: float | None = None

    class Config:
        orm_mode = True


class CartItemCreate(CartItemBase):
    cart_id: int


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
    items: list[CartItem] = []

    class Config:
        orm_mode = True


class AuthUser(BaseModel):
    user_id: int
