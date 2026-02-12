"""
SQLAlchemy ORM models for the IntelliQuery AI e-commerce database.

Tables
------
- **regions** – Geographic regions / markets.
- **customers** – Registered customers with segment labels.
- **products** – Product catalogue with cost & price.
- **orders** – Customer orders with dates and fulfilment status.
- **order_items** – Line items linking orders to products.
"""

from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship


# ── Base ─────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Shared declarative base for all models."""


# ── Regions ──────────────────────────────────────────────────────────────────

class Region(Base):
    __tablename__ = "regions"

    region_id = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)

    # relationships
    customers = relationship("Customer", back_populates="region")

    def __repr__(self) -> str:
        return f"<Region(region_id={self.region_id}, name='{self.region_name}')>"


# ── Customers ────────────────────────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    registration_date = Column(Date, nullable=False)
    customer_segment = Column(String(20), nullable=False)  # Gold / Silver / Bronze

    # relationships
    region = relationship("Region", back_populates="customers")
    orders = relationship("Order", back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer(customer_id={self.customer_id}, name='{self.customer_name}')>"


# ── Products ─────────────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    sub_category = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)

    # relationships
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(product_id={self.product_id}, name='{self.product_name}')>"


# ── Orders ───────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    order_date = Column(Date, nullable=False)
    ship_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False)  # Delivered / Shipped / Processing / Cancelled

    # relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    def __repr__(self) -> str:
        return f"<Order(order_id={self.order_id}, status='{self.status}')>"


# ── Order Items ──────────────────────────────────────────────────────────────

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(5, 2), nullable=False, default=0)

    # relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem(order_item_id={self.order_item_id}, "
            f"order_id={self.order_id}, product_id={self.product_id})>"
        )
