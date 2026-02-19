<div align="center">

# 🏢 LibnamicShop — Plataforma de Gestión Empresarial

**Sistema Full Stack de gestión de inventario, pedidos, pagos y logística con panel analítico en tiempo real.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=for-the-badge&logo=stripe&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white)

<br />

[🌐 **Demo en Producción**](https://libnamicpracticasprimerproyecto-1.onrender.com) · [📖 Documentación API (Swagger)](https://libnamicpracticasprimerproyecto-1.onrender.com/docs) · [🎬 Video Demo](#-video-demo)

</div>

---

## 📋 Descripción del Proyecto

**LibnamicShop** es una plataforma de gestión empresarial completa desarrollada durante el periodo de prácticas en [Libnamic](https://libnamic.com). Replica la lógica de negocio de un ERP moderno, cubriendo desde la gestión del catálogo de productos hasta el procesamiento de pagos en línea, la logística de envíos y la atención al cliente en tiempo real.

### Funcionalidades principales

| Módulo | Descripción |
|--------|-------------|
| 🔐 **Autenticación** | Registro/login con OAuth2 y JWT. Control de acceso por roles (`user` / `admin`) |
| 📦 **Inventario** | CRUD de productos con SKU único, control de stock y búsqueda reactiva en catálogo |
| 🛒 **Carrito de Compra** | Gestión local de carrito con controles de cantidad, resumen y persistencia en `localStorage` |
| 📑 **Pedidos** | Creación de pedidos con validación de stock, precio congelado y generación automática de **factura PDF** |
| 💳 **Pasarela de Pago** | Integración con **Stripe** (modo test) para simulación de pagos con tarjeta |
| 📧 **Notificaciones** | Envío automático de correos de confirmación de pedido vía **SMTP** (Mailtrap en dev) |
| 💬 **Chat en Tiempo Real** | Soporte técnico Admin ↔ Cliente mediante **WebSockets**, con historial de mensajes y salas individuales |
| 📊 **Panel Administrativo (BI)** | Dashboard con KPIs, gráficas de ingresos mensuales, productos más vendidos, evolución de pedidos y gestión logística |

---

## 🏗️ Arquitectura del Sistema

```mermaid
graph TB
    subgraph "☁️ Render Cloud"
        direction TB
        FE["🖥️ Frontend<br/>Vue 3 + Vite<br/>Static Site"]
        API["⚙️ Backend API<br/>FastAPI + Uvicorn<br/>Web Service"]
        DB["🗄️ PostgreSQL<br/>Managed Database"]
    end

    subgraph "🔌 Servicios Externos"
        STRIPE["💳 Stripe API"]
        MAILTRAP["📧 SMTP<br/>Mailtrap"]
    end

    U["👤 Usuario"] -->|HTTPS| FE
    FE -->|REST API| API
    FE <-->|WebSocket| API
    API -->|SQLAlchemy ORM| DB
    API -->|Payment Intent| STRIPE
    API -->|SMTP| MAILTRAP
```

### Separación por capas del Backend

La API sigue un patrón de **Layered Architecture** donde cada módulo tiene una responsabilidad única:

```mermaid
graph TD
    REQ["🌐 Petición HTTP / WebSocket"] --> MAIN["main.py<br/>Controlador · Router · CORS"]
    MAIN --> SCHEMAS["schemas.py<br/>Validación Pydantic (DTOs)"]
    MAIN --> SECURITY["security.py<br/>JWT · Bcrypt · OAuth2"]
    MAIN --> WS["websocket.py<br/>Chat Manager"]
    SCHEMAS --> CRUD["crud.py<br/>Lógica de Negocio"]
    CRUD --> MODELS["models.py<br/>Entidades SQLAlchemy"]
    MODELS --> DATABASE["database.py<br/>Sesión · Engine"]
    MAIN --> INVOICE["invoice.py<br/>Generación PDF"]
    MAIN --> EMAIL["email_service.py<br/>SMTP Integration"]
```

| Archivo | Capa | Responsabilidad |
|---------|------|-----------------|
| `database.py` | Infraestructura | Engine SQLAlchemy, gestión de sesiones y generador `get_db()` |
| `models.py` | Dominio | 4 tablas: `users`, `products`, `orders`, `order_items` con relaciones |
| `schemas.py` | Contrato (DTO) | Esquemas Pydantic para request/response. El password nunca se expone |
| `crud.py` | Negocio | Lógica de pedidos, verificación de stock, cálculo de precios |
| `security.py` | Transversal | Tokens JWT (HS256, 30 min), hashing Bcrypt, validación de roles |
| `main.py` | Presentación | Endpoints REST, middleware CORS, inyección de dependencias |
| `websocket.py` | Real-time | Gestión de salas de chat, broadcast, historial de mensajes |
| `invoice.py` | Utilidad | Generación de facturas PDF con datos del pedido |
| `email_service.py` | Utilidad | Envío de correos de confirmación con plantilla HTML |

---

## 🗄️ Modelo de Datos

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string first_name
        string last_name
        string phone
        string hashed_password
        string role "user | admin"
    }

    PRODUCTS {
        int id PK
        string name
        string description
        float price
        int stock
        string sku UK
    }

    ORDERS {
        int id PK
        int user_id FK
        string status "PENDIENTE | ENVIADO | ENTREGADO"
        float total_price
        datetime created_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float unit_price "Precio congelado"
    }

    USERS ||--o{ ORDERS : "realiza"
    ORDERS ||--|{ ORDER_ITEMS : "contiene"
    PRODUCTS ||--o{ ORDER_ITEMS : "referencia"
```

> **Decisión de diseño:** `unit_price` se persiste en `order_items` en el momento de la compra para «congelar» el precio. Si el producto cambia de precio después, los pedidos históricos mantienen el valor original.

---

## 🔄 Flujos de Aplicación

### Flujo de Autenticación (JWT + OAuth2)

```mermaid
sequenceDiagram
    participant U as 👤 Usuario
    participant FE as 🖥️ Frontend
    participant API as ⚙️ FastAPI
    participant SEC as 🔐 security.py
    participant DB as 🗄️ PostgreSQL

    U->>FE: Introduce email + password
    FE->>API: POST /token (form-urlencoded)
    API->>DB: Buscar usuario por email
    API->>SEC: verify_password(plain, hashed)
    SEC-->>API: ✅ Válido
    API->>SEC: create_access_token(email)
    SEC-->>API: Token JWT (HS256, 30 min)
    API-->>FE: {access_token, role, full_name, email}
    FE->>FE: Guardar en localStorage
    
    Note over U,DB: En peticiones protegidas...
    
    FE->>API: GET /orders/my-orders (Bearer token)
    API->>SEC: jwt.decode(token) → email
    API->>DB: Buscar usuario
    API-->>FE: 200 OK + datos
```

### Flujo de Pedido Completo (Pago → Factura → Email)

```mermaid
sequenceDiagram
    participant U as 👤 Cliente
    participant FE as 🖥️ Frontend
    participant API as ⚙️ Backend
    participant S as 💳 Stripe
    participant DB as 🗄️ PostgreSQL
    participant PDF as 📄 Invoice
    participant MAIL as 📧 SMTP

    U->>FE: Añadir productos al carrito
    U->>FE: Confirmar compra
    FE->>API: POST /create-payment-intent (items)
    API->>DB: Calcular precio total en servidor
    API->>S: stripe.PaymentIntent.create(amount)
    S-->>API: client_secret
    API-->>FE: {client_secret}
    FE->>S: confirmCardPayment(client_secret)
    S-->>FE: ✅ Pago exitoso

    FE->>API: POST /orders/ (items + token)
    
    loop Para cada item
        API->>DB: Buscar producto, verificar stock
        API->>DB: Restar stock
        API->>DB: Crear OrderItem (precio congelado)
    end
    
    API->>DB: Crear Order (total_price, PENDIENTE)
    API->>DB: COMMIT (transacción atómica)
    API->>MAIL: send_order_confirmation(email, order)
    API-->>FE: 200 OK + OrderResponse
    
    Note over U,MAIL: El admin descarga la factura...

    U->>FE: Descargar factura PDF
    FE->>API: GET /orders/{id}/invoice
    API->>PDF: generate_invoice_pdf(order)
    API-->>FE: PDF binario
```

### Flujo del Chat en Tiempo Real

```mermaid
sequenceDiagram
    participant C as 👤 Cliente
    participant FE as 🖥️ Frontend
    participant WS as 🔌 WebSocket
    participant A as 👔 Admin

    C->>WS: Conectar → ws://host/ws/chat/{email}?token=jwt
    WS->>WS: Validar token, unir a sala
    WS-->>C: Historial de mensajes previos

    C->>WS: "Hola, tengo un problema"
    WS->>A: Broadcast mensaje a la sala
    A->>WS: "Hola, te ayudo"
    WS->>C: Broadcast respuesta

    Note over C,A: Cada cliente tiene su sala individual (room_id = email)
```

---

## 🌐 Despliegue en Producción (Render)

La aplicación está completamente desplegada en **Render** con tres servicios independientes:

| Servicio | Tipo | URL |
|----------|------|-----|
| **Frontend** | Static Site | [libnamicpracticasprimerproyecto-1.onrender.com](https://libnamicpracticasprimerproyecto-1.onrender.com) |
| **Backend** | Web Service | Backend URL interna (conectado vía env vars) |
| **PostgreSQL** | Managed Database | Render PostgreSQL (cloud) |

### 🔀 Variables de Entorno: «Mundos Paralelos»

Un aspecto fundamental del despliegue es entender cómo las **variables de entorno** permiten que la misma base de código funcione en ambos contextos sin modificar ni una línea:

```mermaid
graph LR
    subgraph "🖥️ Desarrollo Local"
        direction TB
        LC["Código fuente<br/>VITE_API_URL=http://localhost:8000"]
        LC --> LA["Backend local :8000"]
        LA --> LD["PostgreSQL local :5432"]
    end

    subgraph "☁️ Producción (Render)"
        direction TB
        RC["Mismo código fuente<br/>VITE_API_URL=https://api.render.com"]
        RC --> RA["Backend Render"]
        RA --> RD["PostgreSQL Render (cloud)"]
    end

    LC -.->|"git push"| RC
```

**¿Cómo funciona?** El código fuente referencia `import.meta.env.VITE_API_URL` en el frontend. Esta variable apunta a `http://localhost:8000` en el `.env` local, pero en Render se configura como la URL real del backend desplegado. Así, **el mismo código vive en "mundos paralelos"** que nunca se mezclan:

| Variable | Local (`.env`) | Producción (Render) |
|----------|---------------|---------------------|
| `VITE_API_URL` | `http://localhost:8000` | `https://[backend].onrender.com` |
| `DATABASE_URL` | `postgresql://user:pass@localhost/db` | `postgresql://user:pass@[render-host]/db` |
| `SECRET_KEY` | Valor de desarrollo | Secreto real de producción |
| `STRIPE_SECRET_KEY` | `sk_test_...` | `sk_test_...` (o producción) |
| `SMTP_HOST` | `sandbox.smtp.mailtrap.io` | Servidor SMTP real |

### SPA Routing: Rewrites en Static Sites

Para que las rutas de Vue Router funcionen correctamente en producción (evitando errores 404 al recargar), se configuran **Rewrites** en Render:

```
Regla: /* → /index.html (Status 200)
```

Esto garantiza que cualquier ruta (`/products`, `/admin`, `/chat`, etc.) sea servida por `index.html`, dejando que Vue Router gestione la navegación del lado del cliente.

---

## 📡 Endpoints de la API (Swagger)

La documentación interactiva completa está disponible en [`/docs`](https://libnamicpracticasprimerproyecto-1.onrender.com/docs) (Swagger UI).

### 🔐 Autenticación

| Método | Ruta | Descripción | Auth | Rol |
|--------|------|-------------|------|-----|
| `POST` | `/token` | Genera token JWT (OAuth2 Password Flow) | ❌ | — |
| `POST` | `/register` | Registro de nuevo usuario | ❌ | — |
| `GET` | `/users/me` | Perfil del usuario autenticado | ✅ | any |

### 👥 Usuarios

| Método | Ruta | Descripción | Auth | Rol |
|--------|------|-------------|------|-----|
| `GET` | `/users/` | Lista todos los usuarios | ✅ | any |

### 📦 Productos (Inventario)

| Método | Ruta | Descripción | Auth | Rol |
|--------|------|-------------|------|-----|
| `GET` | `/products/` | Lista todos los productos (paginado) | ❌ | — |
| `GET` | `/products/{id}` | Detalle de un producto | ❌ | — |
| `POST` | `/products/` | Crear producto (valida SKU único) | ✅ | 🔒 admin |
| `PUT` | `/products/{id}` | Actualizar producto | ✅ | 🔒 admin |
| `DELETE` | `/products/{id}` | Eliminar producto | ✅ | 🔒 admin |

### 🛒 Pedidos

| Método | Ruta | Descripción | Auth | Rol |
|--------|------|-------------|------|-----|
| `POST` | `/orders/` | Crear pedido (valida stock, resta inventario) | ✅ | any |
| `GET` | `/orders/my-orders` | Pedidos del usuario autenticado | ✅ | any |
| `GET` | `/orders/{id}/invoice` | Descargar factura PDF | ✅ | any |

### 💳 Pasarela de Pago

| Método | Ruta | Descripción | Auth | Rol |
|--------|------|-------------|------|-----|
| `POST` | `/create-payment-intent` | Crea intención de pago en Stripe | ✅ | any |

### 👔 Administración

| Método | Ruta | Descripción | Auth | Rol |
|--------|------|-------------|------|-----|
| `GET` | `/admin/orders` | Todos los pedidos del sistema | ✅ | 🔒 admin |
| `PATCH` | `/orders/{id}/status` | Cambiar estado logístico | ✅ | 🔒 admin |
| `GET` | `/admin/stats` | KPIs y estadísticas del dashboard | ✅ | 🔒 admin |
| `GET` | `/admin/chat-rooms` | Salas de chat activas | ✅ | 🔒 admin |

### 💬 WebSocket

| Protocolo | Ruta | Descripción |
|-----------|------|-------------|
| `WS` | `/ws/chat/{room_id}?token=jwt` | Canal de chat bidireccional por sala |

### Cómo autenticarse en Swagger

1. Hacer clic en el botón **Authorize** 🔒 (esquina superior derecha)
2. Introducir las credenciales (email y contraseña)
3. El token JWT se incluirá automáticamente en todas las peticiones protegidas
4. El token expira a los **30 minutos**

---

## 🖥️ Frontend — Vistas

La interfaz está construida con **Vue 3** (Composition API) y un sistema de diseño oscuro premium.

| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/login` | `LoginView` | Pantalla de acceso con diseño split-panel y branding corporativo |
| `/register` | `RegisterView` | Formulario de registro con validación |
| `/products` | `ProductsView` | Catálogo con búsqueda reactiva, carrito y gestión CRUD (admin) |
| `/cart` | `CartView` | Carrito de compra con control de cantidades y resumen |
| `/payment` | `PaymentView` | Pasarela de pago con Stripe Elements |
| `/my-orders` | `MyOrdersView` | Historial de pedidos del usuario con estados |
| `/admin` | `AdminDashboardView` | Panel BI con gráficas Chart.js y gestión de envíos |
| `/chat` | `ChatView` | Chat en tiempo real con WebSockets |

> La ruta raíz (`/`) redirige automáticamente a `/login`.

---

## 🛠️ Stack Tecnológico Completo

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Frontend** | Vue 3, Vite, Vue Router | SPA con Composition API y enrutamiento |
| **Gráficas** | Chart.js, vue-chartjs | Visualizaciones del dashboard (Bar, Doughnut, Line) |
| **Pagos** | Stripe.js, `@stripe/stripe-js` | Integración de pagos con tarjeta |
| **Backend** | FastAPI, Uvicorn, Python 3.11 | API REST asíncrona y autodocumentada |
| **ORM** | SQLAlchemy | Mapeo objeto-relacional |
| **Validación** | Pydantic | Esquemas de datos y tipado fuerte |
| **Base de Datos** | PostgreSQL 15 | Persistencia relacional |
| **Migraciones** | Alembic | Versionado del esquema de BD |
| **Seguridad** | OAuth2 + JWT (HS256), Bcrypt | Autenticación y hashing |
| **Real-time** | WebSockets (FastAPI) | Chat bidireccional |
| **PDF** | ReportLab / FPDF | Generación de facturas |
| **Email** | SMTP (Mailtrap) | Notificaciones de pedido |
| **Infraestructura** | Docker, Docker Compose | Contenedorización local |
| **Producción** | Render (Static + Web Service + DB) | Despliegue cloud |

---

## 🚀 Instalación y Despliegue Local

### Prerrequisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución
- [Git](https://git-scm.com/)

### Con Docker Compose (recomendado)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd backend_libnamic

# 2. Configurar variables de entorno
#    Crear un archivo .env en la raíz con:
cp .env.example .env   # o crear manualmente

# 3. Construir y arrancar los 3 contenedores
docker compose up --build

# 4. Acceder:
#    Frontend:  http://localhost:5173
#    API Docs:  http://localhost:8000/docs
```

### Variables de entorno necesarias (`.env`)

```env
# Stripe (modo test)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Seguridad
SECRET_KEY=clave_secreta_para_jwt

# Email (SMTP)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=tu_usuario_mailtrap
SMTP_PASS=tu_password_mailtrap
MAIL_FROM=noreply@libnamicshop.com

# Frontend (Vite)
VITE_API_URL=http://localhost:8000
```

### Comandos útiles

| Acción | Comando |
|--------|---------|
| Arrancar (primera vez) | `docker compose up --build` |
| Arrancar (sin reconstruir) | `docker compose up` |
| Detener contenedores | `docker compose down` |
| Eliminar todo (incluidos datos) | `docker compose down -v` |
| Ver migraciones de BD | `docker compose exec web alembic history` |
| Aplicar migraciones pendientes | `docker compose exec web alembic upgrade head` |
| Generar nueva migración | `docker compose exec web alembic revision --autogenerate -m "descripcion"` |

> Los datos de PostgreSQL persisten entre reinicios gracias al volumen `postgres_data`.

---

## 📁 Estructura del Proyecto

```
backend_libnamic/
├── docker-compose.yml                # Orquestación de 3 servicios
├── .env                              # Variables de entorno (no versionado)
│
├── backend/
│   ├── Dockerfile                    # Imagen Python 3.11-slim
│   ├── requirements.txt              # Dependencias del backend
│   ├── alembic.ini                   # Configuración de Alembic
│   ├── alembic/
│   │   └── versions/                 # Historial de migraciones
│   └── app/
│       ├── main.py                   # Endpoints REST + WebSocket + CORS
│       ├── models.py                 # Entidades SQLAlchemy (4 tablas)
│       ├── schemas.py                # DTOs Pydantic (request/response)
│       ├── crud.py                   # Lógica de negocio y acceso a datos
│       ├── database.py               # Conexión y sesión PostgreSQL
│       ├── security.py               # JWT + Bcrypt
│       ├── websocket.py              # Chat Manager (salas, broadcast)
│       ├── invoice.py                # Generación de facturas PDF
│       └── email_service.py          # Envío de correos SMTP
│
└── frontend/
    ├── Dockerfile                    # Imagen Node 20-slim
    ├── package.json                  # Dependencias del frontend
    ├── vite.config.js                # Configuración de Vite
    ├── demoproyectolibnamic.mp4      # Video demo del proyecto
    └── src/
        ├── App.vue                   # Root component
        ├── router/index.js           # Configuración de rutas SPA
        ├── assets/
        │   ├── base.css              # Design tokens (colores, sombras)
        │   └── main.css              # Reset, utilidades, animaciones
        └── views/
            ├── LoginView.vue         # Login con diseño split-panel
            ├── RegisterView.vue      # Registro de usuario
            ├── ProductsView.vue      # Catálogo + CRUD admin
            ├── CartView.vue          # Carrito de compra
            ├── PaymentView.vue       # Pasarela Stripe
            ├── MyOrdersView.vue      # Historial de pedidos
            ├── AdminDashboardView.vue# Dashboard BI con Chart.js
            └── ChatView.vue          # Chat WebSocket
```

---

## 🧪 Probar la Aplicación en Producción

### URL de acceso

```
https://libnamicpracticasprimerproyecto-1.onrender.com
```

### Flujo de prueba recomendado

1. **Registrar un usuario** — Ir a `/register` y crear cuenta
2. **Iniciar sesión** — Acceder con las credenciales
3. **Explorar el catálogo** — Navegar por `/products`, usar la búsqueda
4. **Añadir al carrito** — Agregar productos y acceder a `/cart`
5. **Realizar un pago** — Proceder al checkout con tarjeta de prueba Stripe:
   - Número: `4242 4242 4242 4242`
   - Fecha: Cualquier fecha futura
   - CVC: Cualquier 3 dígitos
6. **Ver pedidos** — Consultar el historial en `/my-orders`
7. **Chat de soporte** — Acceder a `/chat` para enviar mensajes

> ⚠️ **Nota:** Al usar el tier gratuito de Render, el backend puede tardar ~30 segundos en «despertar» tras un periodo de inactividad (cold start).

---

## 🗂️ Migraciones de Base de Datos (Alembic)

El esquema se gestiona con **Alembic**, permitiendo evolucionar las tablas sin perder datos:

| Revisión | Descripción |
|----------|-------------|
| `38c00a3fe111` | Inicialización de tablas `users` y `products` |
| `896bade5855d` | Creación de tabla `orders` |
| `b1b55b4582bc` | Creación de tabla `order_items` con relaciones FK |

---

## 🧠 Decisiones de Diseño Destacables

1. **Arquitectura por capas** — Models, Schemas, CRUD y Router están aislados. Añadir una nueva entidad sigue siempre el mismo patrón: modelo → esquema → CRUD → endpoint.

2. **Integridad transaccional** — El sistema de pedidos verifica stock y usa transacciones de BD. No hay posibilidad de vender un producto sin stock disponible.

3. **Precio congelado** — `unit_price` en `OrderItem` captura el precio en el momento de compra. Los pedidos históricos son inmutables ante cambios futuros en el catálogo.

4. **Variables de entorno desacopladas** — El mismo código funciona en local y producción gracias a `import.meta.env` (Vite) y `os.getenv()` (Python). Cada entorno tiene sus propias variables sin modificar el código.

5. **Cálculo de precio en servidor** — El precio total del pedido se calcula en el backend (no se confía en el frontend), garantizando la integridad del cobro.

6. **WebSockets con salas** — Cada cliente tiene su propia sala de chat (`room_id = email`), lo que permite al admin atender múltiples clientes simultáneamente.

7. **Generación de PDF bajo demanda** — Las facturas se generan dinámicamente para cada descarga, asegurando datos siempre actualizados.

---

## 🎬 Video Demo

Una demostración completa del funcionamiento de la aplicación está disponible en el repositorio:

https://github.com/Sestmar/LibnamicPracticasPrimerProyecto/raw/main/frontend/demoproyectolibnamic.mp4

> El video muestra el flujo completo: registro, login, navegación por el catálogo, compra con pago Stripe, historial de pedidos, panel administrativo con gráficas y chat en tiempo real.

---

<div align="center">

**Desarrollado por:** Sergio Estudillo Marabot · Prácticas en [Libnamic](https://libnamic.com)

*© 2026 LibnamicShop · Plataforma de Gestión Empresarial*

</div>
