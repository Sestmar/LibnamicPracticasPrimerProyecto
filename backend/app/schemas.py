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

# --- USUARIOS ---
class UserBase(BaseModel):
    email: str
    first_name: str  # Nuevo
    last_name: str   # Nuevo
    phone: str | None = None
    role: str = "user"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True

# --- SCHEMAS PARA CREAR PEDIDOS (Input) ---

# Lo que recibimos del cliente (solo id y cantidad)
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

# Lo que recibimos para crear el pedido completo (lista de items)
class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


# --- SCHEMAS PARA RESPUESTAS (LEER PEDIDOS) ---

# 1. Detalle del item dentro del pedido (Response)
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    
    class Config:
        from_attributes = True

# 2. Esquema pequeñito para mostrar datos del dueño del pedido
class UserInOrder(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    
    class Config:
        from_attributes = True

# 3. El pedido completo con todos sus datos
class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    total_price: float
    status: str
    items: list[OrderItemResponse] = []
    
    # Aquí incrustamos al usuario
    owner: UserInOrder 

    class Config:
        from_attributes = True