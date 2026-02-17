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
    # 1. Creo la cabecera del pedido (aún precio 0)
    db_order = models.Order(user_id=user_id, status="completado", total_price=0.0)
    db.add(db_order)
    db.commit()      # Guardp para obtener el ID del pedido
    db.refresh(db_order)

    total_amount = 0.0

    # 2. Procesp cada item
    for item in order.items:
        # Buscamos el producto
        product = get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        
        # VERIFICO STOCK
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

        # RESTO STOCK
        product.stock -= item.quantity
        
        # Calculo precio del item
        cost = product.price * item.quantity
        total_amount += cost

        # Creo el OrderItem
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price # Congelamos el precio
        )
        db.add(db_item)

    # 3. Actualizo el precio total del pedido
    db_order.total_price = total_amount
    db.add(db_order) # Marco para actualizar
    db.commit()      # Confirmo toda la transacción (items + actualización de pedido + stock)
    db.refresh(db_order)
    
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return product

def update_product(db: Session, product_id: int, product_data: schemas.ProductCreate):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        # Actualizamos campo a campo
        product.name = product_data.name
        product.sku = product_data.sku
        product.description = product_data.description
        product.price = product_data.price
        product.stock = product_data.stock
        db.commit()
        db.refresh(product)
    return product