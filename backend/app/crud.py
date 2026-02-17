from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

# --- PRODUCTOS ---
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_sku(db: Session, sku: str):
    return db.query(models.Product).filter(models.Product.sku == sku).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        sku=product.sku
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    # 1. Crear la cabecera del pedido (aún precio 0)
    db_order = models.Order(user_id=user_id, status="completado", total_price=0.0)
    db.add(db_order)
    db.commit()      # Guardamos para obtener el ID del pedido
    db.refresh(db_order)

    total_amount = 0.0

    # 2. Procesar cada item
    for item in order.items:
        # Buscamos el producto
        product = get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        
        # VERIFICAR STOCK (Lógica de Negocio Real)
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

        # RESTAR STOCK
        product.stock -= item.quantity
        
        # Calcular precio del item
        cost = product.price * item.quantity
        total_amount += cost

        # Crear el OrderItem
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price # Congelamos el precio
        )
        db.add(db_item)

    # 3. Actualizar el precio total del pedido
    db_order.total_price = total_amount
    db.add(db_order) # Marcamos para actualizar
    db.commit()      # Confirmamos toda la transacción (items + actualización de pedido + stock)
    db.refresh(db_order)
    
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()