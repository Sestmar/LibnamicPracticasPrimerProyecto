from pydantic import BaseModel
from datetime import datetime

# --- PRODUCTOS ---
class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    sku: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

# --- USUARIOS (No implementada aún) ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# Lo que recibimos del cliente (solo id y cantidad)
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

# Lo que recibimos para crear el pedido completo (lista de items)
class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

# --- SCHEMAS PARA RESPUESTAS (LEER PEDIDOS) ---

# Detalle del item dentro del pedido (incluye nombre del producto)
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    
    class Config:
        from_attributes = True

# El pedido completo con todos sus datos
class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemResponse] # Lista anidada

    class Config:
        from_attributes = True        