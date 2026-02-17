from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Leo la variable de entorno que puse en Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://libnamic_user:libnamic_password@localhost/inventario_db")


engine = create_engine(DATABASE_URL) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()