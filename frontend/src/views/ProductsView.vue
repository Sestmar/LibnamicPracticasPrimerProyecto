<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const products = ref([])
const error = ref('')
const router = useRouter()
const token = localStorage.getItem('token')

if (!token) router.push('/login')

const fetchProducts = async () => {
  try {
    const response = await fetch('http://localhost:8000/products/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('Error al cargar productos')
    products.value = await response.json()
  } catch (e) {
    error.value = e.message
  }
}

const buyProduct = async (productId) => {
  try {
    const response = await fetch('http://localhost:8000/orders/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ items: [{ product_id: productId, quantity: 1 }] })
    })

    if (response.ok) {
      // Feedback visual
      alert('✅ Pedido realizado')
      fetchProducts()
    } else {
      const err = await response.json()
      alert('❌ Error: ' + err.detail)
    }
  } catch (e) {
    console.error(e)
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(fetchProducts)
</script>

<template>
  <div class="main-layout">
    
    <nav class="navbar">
      <div class="nav-content">
        <div class="logo">
             LibnamicShop
        </div>
        <div class="nav-actions">
          <button @click="router.push('/my-orders')" class="nav-btn secondary">
            Mis Pedidos
          </button>
          <button @click="logout" class="nav-btn danger">
            Salir
          </button>
        </div>
      </div>
    </nav>

    <main class="container">
      <header class="page-header">
        <h1>Catálogo de Productos</h1>
        <p class="subtitle">Explora nuestro hardware de última generación</p>
      </header>

      <div v-if="error" class="error-banner">
         {{ error }}
      </div>

      <div v-else class="product-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          
          <div class="card-image">
            <span class="emoji-placeholder">💻</span>
          </div>

          <div class="card-body">
            <div class="card-header">
              <h3>{{ product.name }}</h3>
              <span class="sku">SKU: {{ product.sku }}</span>
            </div>
            
            <p class="description">{{ product.description }}</p>
            
            <div class="card-footer">
              <div class="price-stock">
                <span class="price">{{ product.price }} €</span>
                <span :class="['stock-badge', product.stock < 5 ? 'low' : 'good']">
                  {{ product.stock }} en stock
                </span>
              </div>
              
              <button 
                @click="buyProduct(product.id)" 
                :disabled="product.stock === 0"
                class="buy-btn">
                {{ product.stock > 0 ? 'Añadir al Carrito' : 'Agotado' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* --- 1. Estructura General --- */
.main-layout {
  min-height: 100vh;
  background-color: #f8f9fa; /* Gris muy suave, típico de dashboards modernos */
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  padding-top: 100px; /* Espacio para que la navbar no tape el contenido */
}

/* --- 2. Navbar --- */
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px); /* Efecto cristal */
  border-bottom: 1px solid #eaeaea;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn.secondary { background: #eef2f6; color: #2c3e50; }
.nav-btn.secondary:hover { background: #dfe4ea; }
.nav-btn.danger { background: #fff0f0; color: #e74c3c; }
.nav-btn.danger:hover { background: #fee2e2; }

/* --- 3. Cabecera de Página --- */
.page-header {
  margin-bottom: 3rem;
  text-align: center;
}
.page-header h1 { font-size: 2.5rem; color: #1a202c; margin-bottom: 0.5rem; }
.subtitle { color: #718096; font-size: 1.1rem; }

/* --- 4. Grid de Productos --- */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Responsive automático */
  gap: 2rem;
}

/* --- 5. Tarjeta de Producto (Card) --- */
.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.card-image {
  height: 160px;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); /* Gradiente moderno */
  display: flex;
  align-items: center;
  justify-content: center;
}
.emoji-placeholder { font-size: 4rem; }

.card-body {
  padding: 1.5rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.5rem;
}
.card-header h3 { margin: 0; font-size: 1.25rem; color: #2d3748; }
.sku { font-size: 0.75rem; color: #a0aec0; letter-spacing: 0.05em; }

.description {
  color: #718096;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}

/* --- 6. Footer de la Tarjeta --- */
.card-footer {
  margin-top: auto;
}

.price-stock {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.price { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }

.stock-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}
.stock-badge.good { background: #def7ec; color: #03543f; }
.stock-badge.low { background: #fde8e8; color: #9b1c1c; }

.buy-btn {
  width: 100%;
  padding: 0.875rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.buy-btn:hover:not(:disabled) { background-color: #3aa876; }
.buy-btn:disabled { background-color: #cbd5e0; cursor: not-allowed; }
</style>