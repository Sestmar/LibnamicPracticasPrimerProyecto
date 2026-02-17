from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

# CLAVE SECRETA (En producción esto va en variables de entorno, NUNCA en código)
SECRET_KEY = "esto_es_un_secreto_super_seguro_libnamic"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración para hashear passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Función para verificar password (Login)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 2. Función para encriptar password (Registro)
def get_password_hash(password):
    return pwd_context.hash(password)

# 3. Función para crear el Token JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt