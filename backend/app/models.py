import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # ELIMINAMOS username. Ahora el email es el identificador único.
    email = Column(String, unique=True, index=True)
    first_name = Column(String)  # Nuevo
    last_name = Column(String)   # Nuevo
    phone = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

    # items = relationship("Item", back_populates="owner") La clase Item ya no existe, usamos Orders
    orders = relationship("Order", back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    stock = Column(Integer, default=0)
    sku = Column(String, unique=True, index=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="PENDIENTE")
    
    # Relaciones
    # Un pedido pertenece a un usuario
    owner = relationship("User", back_populates="orders")
    # Un pedido tiene muchos items
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Float) # Guardo el precio al momento de la compra

    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product") # Para saber qué producto es