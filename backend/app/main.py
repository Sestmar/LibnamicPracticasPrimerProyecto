from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import models, schemas, crud, database, security

# Crea las tablas (ahora creará 'products' y 'users')
# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURIDAD ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- RUTA PROTEGIDA DE PRUEBA ---
@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"mensaje": "¡Has entrado en la zona segura!", "token_actual": token}

# --- NUEVOS ENDPOINTS: PRODUCTOS (INVENTARIO) ---

@app.post("/products/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme) # CANDADO: Solo logueados
):
    # Validar si ya existe el SKU
    db_product = crud.get_product_by_sku(db, sku=product.sku)
    if db_product:
        raise HTTPException(status_code=400, detail="El producto con ese SKU ya existe")
    return crud.create_product(db=db, product=product)

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
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # Buscamos al usuario en la DB
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Creamos el pedido
    return crud.create_order(db=db, order=order, user_id=user.id)

@app.get("/orders/my-orders", response_model=list[schemas.OrderResponse])
def read_my_orders(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # --- BUSCAR AL USUARIO EN LA DB ---
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Ahora sí, 'user' existe y podemos usar user.id
    return crud.get_orders_by_user(db, user_id=user.id)

# Endpoint para crear un usuario de prueba en la base de datos
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Guardamos la contraseña tal cual para probar rápido
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=user.password # <--- Sin encriptar solo por ahora
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user