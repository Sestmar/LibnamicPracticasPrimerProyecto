# 📦 Backend de Gestión de Inventario (ERP Core)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)

## 📖 Descripción del Proyecto

Este proyecto es una **API RESTful** diseñada para la gestión de inventario y pedidos empresariales. Ha sido desarrollada como parte del periodo de prácticas en **Libnamic**, replicando la lógica de negocio y arquitectura de sistemas ERP modernos (como Odoo).

El objetivo es construir un backend escalable, seguro y contenerizado, migrando de soluciones locales (SQLite) a una infraestructura robusta orientada a microservicios.

## 🚀 Stack Tecnológico

La arquitectura está desacoplada utilizando contenedores Docker:

* **Lenguaje:** Python 3.11+
* **Framework Web:** FastAPI (Alto rendimiento, asíncrono y autodocumentado).
* **Base de Datos:** PostgreSQL 15 (Persistencia mediante Docker Volumes).
* **ORM:** SQLAlchemy (Mapeo Objeto-Relacional).
* **Validación:** Pydantic (Esquemas y tipado fuerte).
* **Seguridad:** OAuth2 con Password Flow + JWT (JSON Web Tokens).
* **Infraestructura:** Docker & Docker Compose.

## 📂 Estructura del Proyecto

El código sigue una arquitectura modular para facilitar el mantenimiento:

backend-libnamic/
├── app/
│   ├── crud.py          # Capa de Acceso a Datos (Repository Pattern)
│   ├── database.py      # Configuración de conexión a PostgreSQL
│   ├── main.py          # Controladores y Endpoints (Entrypoint)
│   ├── models.py        # Modelos de Base de Datos (SQLAlchemy Entities)
│   ├── schemas.py       # DTOs y Validación de Datos (Pydantic Models)
│   └── security.py      # Lógica de Hashing (Bcrypt) y Generación de JWT
├── docker-compose.yml   # Orquestación de servicios (Web + DB)
├── Dockerfile           # Construcción de la imagen de la API
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Documentación


🛠️ Instalación y Despliegue
Este proyecto está 100% Dockerizado, por lo que no es necesario instalar Python ni PostgreSQL localmente.

Prerrequisitos
Tener instalado Docker Desktop y Git.

Pasos para levantar el entorno
Clonar el repositorio:

git clone <url-de-tu-repo>
cd backend-libnamic

Construir y levantar los contenedores:
docker compose up --build
Este comando descargará la imagen de Postgres, instalará las dependencias de Python y levantará el servidor Uvicorn.

Verificar estado:
Una vez finalizado, la API estará disponible en el puerto 8000 y la base de datos en el 5432.

⚡ Uso de la API (Documentación Interactiva)
FastAPI genera documentación automática con Swagger UI.

Abre tu navegador en: http://localhost:8000/docs

Verás todos los endpoints disponibles para probarlos en tiempo real.

🔐 Autenticación y Seguridad
El sistema implementa seguridad mediante JWT. Ciertos endpoints (como Crear Producto) están protegidos.

Cómo autenticarse en Swagger:

Haz clic en el botón verde Authorize (candado arriba a la derecha).

Utiliza las credenciales de prueba (Hardcoded para entorno DEV):

Username: admin (o cualquier string)

Password: admin

Haz clic en Login.

El candado se cerrará 🔒. Ahora puedes realizar peticiones a las rutas protegidas.

Endpoints Principales
POST /token: Genera el Token de acceso.

GET /products/: Lista el inventario público.

POST /products/: Crea un nuevo producto (Requiere Auth).

Validación: Impide crear productos con SKU duplicado.

GET /users/me: Valida el token actual.

🛣️ Roadmap (Próximos Pasos)
[x] Dockerización completa (App + DB).

[x] Migración a PostgreSQL.

[x] Sistema de Autenticación JWT.

[ ] Implementación de Alembic para migraciones de base de datos.

[ ] Tests unitarios y de integración con Pytest.

[ ] Relación de tablas (Usuarios -> Pedidos -> Productos).

Desarrollado por: Sergio Estudillo Marabot

Carpeta app: 
database.py: Configura la conexión. Usa SQLAlchemy (un ORM) para no tener que escribir código SQL a mano, sino trabajar con objetos Python.

models.py: Define la estructura de la base de datos. Aquí se ha creado las tablas users, products, orders y order_items con sus relaciones (un usuario tiene muchos pedidos, un pedido tiene muchos productos).

schemas.py: Son los contratos de datos (Pydantic). Definen qué datos permites que entren (ej: un nombre de producto) y qué datos devuelves (ej: no devolver nunca la contraseña del usuario).

crud.py: Es el cerebro de la lógica de negocio. Aquí es donde ocurre la magia: cuando se hace un pedido, el código busca el precio, verifica que haya stock suficiente, lo resta y guarda el total.

main.py: Es el punto de entrada. Define las rutas (endpoints) que ves en Swagger y gestiona la seguridad.