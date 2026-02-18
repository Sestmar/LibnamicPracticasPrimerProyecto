from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from . import models, schemas
from fastapi import HTTPException
from app import security


# GESTIÓN DE USUARIOS (NUEVO SISTEMA)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Encripto la contraseña antes de guardarla
    hashed_pwd = security.get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        hashed_password=hashed_pwd, # - Guardamos encriptado
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==========================================
# GESTIÓN DE PRODUCTOS
# ==========================================

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

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return product

def update_product(db: Session, product_id: int, product_data: schemas.ProductCreate):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.name = product_data.name
        product.sku = product_data.sku
        product.description = product_data.description
        product.price = product_data.price
        product.stock = product_data.stock
        db.commit()
        db.refresh(product)
    return product


# ==========================================
# GESTIÓN DE PEDIDOS (LOGÍSTICA)
# ==========================================

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    # 1. Creamos la cabecera del pedido
    # CORRECCIÓN IMPORTANTE: Nace como "PENDIENTE", no "completado"
    db_order = models.Order(user_id=user_id, status="PENDIENTE", total_price=0.0)
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    total_amount = 0.0

    # 2. Procesamos cada item
    for item in order.items:
        # Buscamos el producto
        product = get_product(db, item.product_id)
        if not product:
            # Si falla, deberíamos hacer rollback en un caso real, pero por simplicidad:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        
        # VERIFICAR STOCK
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

        # RESTAR STOCK
        product.stock -= item.quantity
        
        # Calcular precio
        cost = product.price * item.quantity
        total_amount += cost

        # Crear OrderItem
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price
        )
        db.add(db_item)

    # 3. Actualizamos el precio total final
    db_order.total_price = total_amount
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    # Ordenamos para ver los más recientes primero
    return db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.id.desc()).all()

# --- FUNCIONES DE ADMIN ---

def get_all_orders(db: Session):
    return db.query(models.Order).order_by(models.Order.id.desc()).all()

def update_order_status(db: Session, order_id: int, new_status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = new_status
        db.commit()
        db.refresh(order)
    return order


# --- ESTADÍSTICAS DEL DASHBOARD (BI) ---

def get_dashboard_stats(db: Session):
    # 1. Ingresos totales y número de pedidos
    total_revenue = db.query(func.coalesce(func.sum(models.Order.total_price), 0)).scalar()
    total_orders = db.query(func.count(models.Order.id)).scalar()
    avg_ticket = round(total_revenue / total_orders, 2) if total_orders > 0 else 0

    # 2. Ventas agrupadas por mes (últimos 6 meses)
    monthly_sales = (
        db.query(
            extract('year', models.Order.created_at).label('year'),
            extract('month', models.Order.created_at).label('month'),
            func.sum(models.Order.total_price).label('revenue'),
            func.count(models.Order.id).label('orders')
        )
        .group_by('year', 'month')
        .order_by(extract('year', models.Order.created_at).desc(), extract('month', models.Order.created_at).desc())
        .limit(6)
        .all()
    )

    # Formateamos para el frontend (orden cronológico)
    months_data = [
        {"month": int(row.month), "year": int(row.year), "revenue": round(float(row.revenue), 2), "orders": int(row.orders)}
        for row in reversed(monthly_sales)
    ]

    # 3. Top 5 productos más vendidos (por unidades)
    top_products = (
        db.query(
            models.Product.name,
            func.sum(models.OrderItem.quantity).label('units_sold')
        )
        .join(models.OrderItem, models.Product.id == models.OrderItem.product_id)
        .group_by(models.Product.id, models.Product.name)
        .order_by(func.sum(models.OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    top_products_data = [
        {"name": row.name, "units_sold": int(row.units_sold)}
        for row in top_products
    ]

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": total_orders,
        "avg_ticket": avg_ticket,
        "monthly_sales": months_data,
        "top_products": top_products_data
    }