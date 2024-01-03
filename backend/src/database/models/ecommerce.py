from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orders: List["Order"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', created_at='{self.created_at}')>"


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str
    price: float = Field(nullable=False)
    stock: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    order_items: List["OrderItem"] = Relationship(back_populates="product")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default='pending')

    user: User = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(nullable=False, foreign_key="order.id")
    product_id: int = Field(nullable=False, foreign_key="product.id")
    quantity: int = Field(nullable=False)

    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")
