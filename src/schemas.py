from pydantic import BaseModel


class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    price_per_item: float | None = None
    total_price: float | None = None

    class Config:
        from_attributes = True


class CartItemCreate(CartItemBase):
    pass


class CartItem(CartItemBase):
    id: int
    cart_id: int

    class Config:
        from_attributes = True


class CartBase(BaseModel):
    user_id: int
    total_price: float

    class Config:
        from_attributes = True


class CartCreate(CartBase):
    pass


class CartSchema(CartBase):
    id: int
    items: list[CartItem] = []

    class Config:
        from_attributes = True


class AuthUser(BaseModel):
    user_id: int
