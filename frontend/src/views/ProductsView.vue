<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const products = ref([])
const error = ref('')
const router = useRouter()
const token = localStorage.getItem('token')
const userRole = localStorage.getItem('role')

// Estado para el formulario (Crear o Editar)
const isEditing = ref(false)
const editingId = ref(null)

const newProduct = ref({ name: '', description: '', price: 0, stock: 0, sku: '' })

if (!token) router.push('/login')

// --- CARGAR PRODUCTOS ---
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

// --- GUARDAR (CREAR O EDITAR) ---
const saveProduct = async () => {
  const url = isEditing.value 
    ? `http://localhost:8000/products/${editingId.value}`
    : 'http://localhost:8000/products/'
  
  const method = isEditing.value ? 'PUT' : 'POST'

  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(newProduct.value)
    })

    if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail)
    }

    alert(isEditing.value ? '✅ Producto actualizado' : '✅ Producto creado')
    cancelEdit() // Limpia el formulario
    fetchProducts()
    
  } catch (e) {
    alert('❌ Error: ' + e.message)
  }
}

// --- BORRAR PRODUCTO ---
const deleteProduct = async (id) => {
  if(!confirm('¿Seguro que quieres borrar este producto?')) return

  try {
    const response = await fetch(`http://localhost:8000/products/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.ok) {
      fetchProducts()
    } else {
      alert('Error al borrar')
    }
  } catch (e) {
    console.error(e)
  }
}

// --- PREPARAR FORMULARIO PARA EDITAR ---
const startEdit = (product) => {
  isEditing.value = true
  editingId.value = product.id
  // Copiamos los datos del producto al formulario
  newProduct.value = { ...product } 
  // Scroll suave hacia arriba para ver el formulario
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// --- CANCELAR EDICIÓN ---
const cancelEdit = () => {
  isEditing.value = false
  editingId.value = null
  newProduct.value = { name: '', description: '', price: 0, stock: 0, sku: '' }
}

// --- FUNCIÓN CARRITO ---
const addToCart = (product) => {
  // 1. Recuperamos el carrito actual (o creamos uno vacío)
  let cart = JSON.parse(localStorage.getItem('shopping_cart') || '[]')
  
  // 2. Busco si el producto ya estaba para sumar cantidad
  const existingItem = cart.find(item => item.id === product.id)
  
  if (existingItem) {
    if (existingItem.quantity < product.stock) {
      existingItem.quantity++
    } else {
      alert('¡No hay más stock disponible!')
      return
    }
  } else {
    // Si es nuevo, lo añado con cantidad 1
    // Guardo solo lo necesario: id, nombre, precio
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      quantity: 1,
      stock: product.stock // Para validar stock en el carrito
    })
  }

  // 3. Guardamos en LocalStorage
  localStorage.setItem('shopping_cart', JSON.stringify(cart))
  alert('🛒 Producto añadido al carrito')
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('username')
  router.push('/login')
}

onMounted(fetchProducts)
</script>

<template>
  <div class="main-layout">
    <nav class="navbar">
      <div class="nav-content">
        <div class="logo">LibnamicShop</div>
        <div class="nav-actions">
          <button @click="router.push('/my-orders')" class="nav-btn secondary">
            Mis Pedidos
          </button>
          
          <button 
            v-if="userRole === 'admin'" 
            @click="router.push('/admin')" 
            class="nav-btn settings-btn">
            Ajustes
          </button>

          <button 
            v-else 
            @click="router.push('/cart')" 
            class="nav-btn cart-btn">
            🛒 Carrito
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
        <p class="subtitle">Gestión de Inventario y Ventas</p>
      </header>

      <div v-if="userRole === 'admin'" class="admin-panel">
        <div class="panel-header">
          <h2>{{ isEditing ? 'Editar Producto' : 'Nuevo Producto' }}</h2>
          <button v-if="isEditing" @click="cancelEdit" class="cancel-btn">Cancelar Edición</button>
        </div>

        <form @submit.prevent="saveProduct" class="admin-form">
          <div class="form-row">
            <div class="input-group">
              <label>Nombre del Producto</label>
              <input v-model="newProduct.name" placeholder="Ej: Monitor 24''" required />
            </div>
            <div class="input-group">
              <label>Código SKU</label>
              <input v-model="newProduct.sku" placeholder="Ej: MON-001" required />
            </div>
          </div>

          <div class="input-group">
            <label>Descripción</label>
            <input v-model="newProduct.description" placeholder="Detalles del producto..." />
          </div>

          <div class="form-row">
            <div class="input-group">
              <label>Precio (€)</label>
              <input v-model.number="newProduct.price" type="number" step="0.01" required />
            </div>
            <div class="input-group">
              <label>Stock Inicial</label>
              <input v-model.number="newProduct.stock" type="number" required />
            </div>
            
            <button type="submit" class="create-btn">
              {{ isEditing ? 'Guardar Cambios' : '➕ Añadir Producto' }}
            </button>
          </div>
        </form>
      </div>

      <div v-if="error" class="error-banner">{{ error }}</div>

      <div v-else class="product-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="card-image">
            
          </div>

          <div class="card-body">
            <div class="card-header">
              <h3>{{ product.name }}</h3>
              <span class="sku">{{ product.sku }}</span>
            </div>
            <p class="description">{{ product.description }}</p>
            
            <div class="card-footer">
              <div class="price-stock">
                <span class="price">{{ product.price }} €</span>
                <span :class="['stock-badge', product.stock < 5 ? 'low' : 'good']">
                  Stock: {{ product.stock }}
                </span>
              </div>
              
              <button 
                v-if="userRole !== 'admin'" 
                @click="addToCart(product)" 
                :disabled="product.stock === 0"
                class="buy-btn">
                {{ product.stock > 0 ? '🛒 Añadir al Carrito' : 'Agotado' }}
              </button>

              <div v-else class="admin-actions">
                <button @click="startEdit(product)" class="action-btn edit">✏️ Editar</button>
                <button @click="deleteProduct(product.id)" class="action-btn delete">🗑️ Borrar</button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Estilos base */
.main-layout { min-height: 100vh; background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem; padding-top: 100px; }
.navbar { position: fixed; top: 0; width: 100%; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid #eaeaea; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.nav-content { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.5rem; font-weight: 800; color: #2c3e50; }
.nav-actions { display: flex; gap: 1rem; }
.nav-btn { padding: 0.5rem 1rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.nav-btn.secondary { background: #eef2f6; color: #2c3e50; }
.nav-btn.danger { background: #fff0f0; color: #e74c3c; }
.page-header { margin-bottom: 3rem; text-align: center; }
.page-header h1 { font-size: 2.5rem; color: #1a202c; margin-bottom: 0.5rem; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; }

/* PANEL ADMIN MEJORADO */
.admin-panel {
  background: white;
  border: 1px solid #e2e8f0;
  border-left: 5px solid #f39c12; /* Borde naranja a la izquierda */
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 3rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.panel-header h2 { margin: 0; color: #2c3e50; font-size: 1.5rem; }
.cancel-btn { background: transparent; border: 1px solid #ccc; padding: 5px 10px; border-radius: 4px; cursor: pointer; color: #666; }

.admin-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-row { display: flex; gap: 1.5rem; flex-wrap: wrap; }

/* INPUTS CON ETIQUETAS */
.input-group { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; min-width: 200px;}
.input-group label { font-weight: 600; font-size: 0.9rem; color: #4a5568; }
.input-group input { padding: 0.75rem; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 1rem; transition: border-color 0.2s; }
.input-group input:focus { border-color: #f39c12; outline: none; }

.create-btn {
  background: #f39c12; color: white; border: none; padding: 0 2rem; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; align-self: flex-end; height: 46px; /* Ajuste para alinear con inputs */
}
.create-btn:hover { background: #e67e22; }

/* TARJETAS */
.product-card { background: white; border-radius: 16px; overflow: hidden; border: 1px solid #f0f0f0; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; }
.product-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
.card-image { height: 160px; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); display: flex; align-items: center; justify-content: center; }
.emoji-placeholder { font-size: 4rem; }
.card-body { padding: 1.5rem; flex-grow: 1; display: flex; flex-direction: column; }
.card-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem; }
.sku { font-size: 0.75rem; color: #a0aec0; letter-spacing: 0.05em; }
.description { color: #718096; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; flex-grow: 1; }
.card-footer { margin-top: auto; }
.price-stock { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.price { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }
.stock-badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
.stock-badge.good { background: #def7ec; color: #03543f; }
.stock-badge.low { background: #fde8e8; color: #9b1c1c; }

/* BOTONES DE ACCIÓN */
.buy-btn { width: 100%; padding: 0.875rem; background-color: #42b883; color: white; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; }
.buy-btn:hover { background-color: #3aa876; }

.admin-actions { display: flex; gap: 10px; }
.action-btn { flex: 1; padding: 0.8rem; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; color: white; }
.action-btn.edit { background-color: #3498db; }
.action-btn.edit:hover { background-color: #2980b9; }
.action-btn.delete { background-color: #e74c3c; }
.action-btn.delete:hover { background-color: #c0392b; }
</style>