from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.conf.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True)
    total_price = Column(Float, default=0.0)
    status = Column(String, default='open')
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, total_price={self.total_price})>"


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"))
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_per_item = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    cart = relationship("Cart", back_populates="items")

    def __repr__(self):
        return (
            f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, "
            f"quantity={self.quantity}, price_per_item={self.price_per_item}, total_price={self.total_price})>"
        )
