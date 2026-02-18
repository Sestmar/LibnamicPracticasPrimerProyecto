from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import models, schemas, crud, database, security

# Creo las tablas (ahora creará 'products' y 'users')
# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

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
    # TRUCO: form_data.username contiene el EMAIL que envía el frontend
    user = crud.get_user_by_email(db, email=form_data.username)
    
    # Verificamos si el usuario existe Y si la contraseña coincide
    if not user or user.hashed_password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token usando el email como identificador
    access_token = security.create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "email": user.email,
        "role": user.role,
        "full_name": f"{user.first_name} {user.last_name}" # Devolvemos el nombre completo
    }

# --- RUTA PROTEGIDA DE PRUEBA ---
@app.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"mensaje": "¡Has entrado en la zona segura!", "usuario": current_user.username, "rol": current_user.role}

# --- NUEVOS ENDPOINTS: PRODUCTOS (INVENTARIO) ---

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