import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import models, schemas, crud, database, security
import stripe

# Creo las tablas (ahora creará 'products' y 'users')
# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURIDAD Y DEPENDENCIAS ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Función auxiliar: Obtiene el usuario actual desde el token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificamos el token
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub") # Ahora el token guarda el email
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscamos al usuario en la DB
    user = crud.get_user_by_email(db, email=email) # Buscamos por email
    if user is None:
        raise credentials_exception
    return user

# Función auxiliar: Solo deja pasar si el rol es 'admin'
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de Administrador"
        )
    return current_user

# --- LOGIN (Token) ---
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    
    # Le paso (contraseña_que_escribe_pepe, contraseña_encriptada_en_db)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "email": user.email,
        "role": user.role,
        "full_name": f"{user.first_name} {user.last_name}"
    }

# --- RUTA PROTEGIDA DE PRUEBA ---
@app.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"mensaje": "¡Has entrado en la zona segura!", "usuario": current_user.username, "rol": current_user.role}

# --- PASARELA DE PAGO ---

@app.post("/create-payment-intent")
def create_payment_intent(
    order: schemas.OrderCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    1. Recibe los items que el usuario quiere comprar.
    2. Calcula el precio TOTAL en el servidor (seguridad).
    3. Pide a Stripe una intención de pago.
    4. Devuelve el 'client_secret' al frontend para que complete el pago.
    """
    total_amount = 0.0

    # 1. Calcular precio real verificando en base de datos
    for item in order.items:
        product = crud.get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")
        
        total_amount += product.price * item.quantity

    # 2. Stripe trabaja en CÉNTIMOS (enteros), no en decimales.
    # Ejemplo: 20.50€ -> 2050 céntimos
    amount_in_cents = int(total_amount * 100)

    try:
        # 3. Crear la intención de pago en Stripe
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="eur",
            automatic_payment_methods={"enabled": True}, # Permite tarjetas, Google Pay, etc.
            metadata={"user_email": current_user.email} # Guardamos info extra
        )

        return {"clientSecret": intent.client_secret}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- ENDPOINTS DE PRODUCTOS (INVENTARIO) ---

@app.post("/products/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(database.get_db),
    # CANDADO DE ORO: Ahora exigimos ser admin usando la nueva función
    current_user: models.User = Depends(get_current_admin) 
):
    # Validar si ya existe el SKU
    db_product = crud.get_product_by_sku(db, sku=product.sku)
    if db_product:
        raise HTTPException(status_code=400, detail="El producto con ese SKU ya existe")
    return crud.create_product(db=db, product=product)

# BORRAR PRODUCTO (Solo Admin)
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_admin) # <--- Solo admin
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    crud.delete_product(db, product_id)
    return {"detail": "Producto eliminado"}

# ACTUALIZAR PRODUCTO (Solo Admin)
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_data: schemas.ProductCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_admin) # <--- Solo admin
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud.update_product(db, product_id, product_data)

@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_product


# --- ENDPOINTS DE PEDIDOS ---

@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(
    order: schemas.OrderCreate, 
    db: Session = Depends(database.get_db),
    # Usamos la dependencia estándar (cualquier usuario registrado puede comprar)
    current_user: models.User = Depends(get_current_user)
):
    # Creamos el pedido usando el ID del usuario que viene del token
    return crud.create_order(db=db, order=order, user_id=current_user.id)

@app.get("/orders/my-orders", response_model=list[schemas.OrderResponse])
def read_my_orders(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Usamos directamente el usuario recuperado por la dependencia
    return crud.get_orders_by_user(db, user_id=current_user.id)

# Endpoint para crear un usuario de prueba en la base de datos
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Verificar si el email ya existe
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # 2. Crear el usuario usando la función del CRUD (que maneja nombre, telefono, etc.)
    return crud.create_user(db=db, user=user)

# Endpoints de exclusividad para el admin
# Endpoint para ver TODOS los pedidos
@app.get("/admin/orders", response_model=list[schemas.OrderResponse])
def read_all_orders(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_admin) # <--- Candado Admin
):
    return crud.get_all_orders(db)

# Endpoint para cambiar estado
@app.patch("/orders/{order_id}/status")
def change_order_status(
    order_id: int,
    status: str, # Recibiremos el string query param (Ej: ?status=ENVIADO)
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_admin)
):
    return crud.update_order_status(db, order_id, new_status=status)