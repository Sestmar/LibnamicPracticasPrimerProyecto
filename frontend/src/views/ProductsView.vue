<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const products = ref([])
const error = ref('')
const router = useRouter()
const token = localStorage.getItem('token')
const userRole = localStorage.getItem('role')

// DEFINIMOS LA URL DE LA API DESDE VARIABLES DE ENTORNO
const apiUrl = import.meta.env.VITE_API_URL

// Estado para el formulario (Crear o Editar)
const isEditing = ref(false)
const editingId = ref(null)
const newProduct = ref({ name: '', description: '', price: 0, stock: 0, sku: '' })

// Estado del buscador predictivo
const searchQuery = ref('')

// Toast notification
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 2500)
}

// Filtrado reactivo
const filteredProducts = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return products.value
  return products.value.filter(product => {
    return product.name.toLowerCase().includes(query)
      || product.sku.toLowerCase().includes(query)
      || (product.description && product.description.toLowerCase().includes(query))
  })
})

if (!token) router.push('/login')

// --- CARGAR PRODUCTOS ---
const fetchProducts = async () => {
  try {
    // CAMBIO: Uso de apiUrl con comillas invertidas
    const response = await fetch(`${apiUrl}/products/`, {
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
  // CAMBIO: Uso de apiUrl en ambas opciones
  const url = isEditing.value 
    ? `${apiUrl}/products/${editingId.value}`
    : `${apiUrl}/products/`
  
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

    showToast(isEditing.value ? 'Producto actualizado' : 'Producto creado')
    cancelEdit()
    fetchProducts()
    
  } catch (e) {
    showToast('Error: ' + e.message, 'error')
  }
}

// --- BORRAR PRODUCTO ---
const deleteProduct = async (id) => {
  if(!confirm('¿Seguro que quieres borrar este producto?')) return
  try {
    // CAMBIO: Uso de apiUrl
    const response = await fetch(`${apiUrl}/products/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      showToast('Producto eliminado')
      fetchProducts()
    } else {
      showToast('Error al borrar', 'error')
    }
  } catch (e) { console.error(e) }
}

// --- PREPARAR FORMULARIO PARA EDITAR ---
const startEdit = (product) => {
  isEditing.value = true
  editingId.value = product.id
  newProduct.value = { ...product } 
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
  let cart = JSON.parse(localStorage.getItem('shopping_cart') || '[]')
  const existingItem = cart.find(item => item.id === product.id)
  
  if (existingItem) {
    if (existingItem.quantity < product.stock) {
      existingItem.quantity++
    } else {
      showToast('No hay más stock disponible', 'error')
      return
    }
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      quantity: 1,
      stock: product.stock
    })
  }

  localStorage.setItem('shopping_cart', JSON.stringify(cart))
  showToast(`${product.name} añadido al carrito`)
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
    <!-- Toast notification -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['toast', toast.type]">
        <span class="toast-icon">{{ toast.type === 'success' ? '✓' : '✕' }}</span>
        {{ toast.message }}
      </div>
    </Transition>

    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-content">
        <div class="logo" @click="router.push('/products')">
          <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
            <rect width="40" height="40" rx="10" fill="url(#navGrad)"/>
            <path d="M12 20L18 26L28 14" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <defs><linearGradient id="navGrad" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6c5ce7"/><stop offset="1" stop-color="#00cec9"/></linearGradient></defs>
          </svg>
          <span>LibnamicShop</span>
        </div>
        <div class="nav-actions">
          <button @click="router.push('/my-orders')" class="nav-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            Pedidos
          </button>
          
          <button 
            v-if="userRole === 'admin'" 
            @click="router.push('/admin')" 
            class="nav-btn admin-nav-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            Panel Admin
          </button>

          <button 
            v-else 
            @click="router.push('/cart')" 
            class="nav-btn cart-nav-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
            Carrito
          </button>

          <button @click="router.push('/chat')" class="nav-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            Chat
          </button>

          <button @click="logout" class="nav-btn nav-btn-danger">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            Salir
          </button>
        </div>
      </div>
    </nav>

    <main class="container">
      <!-- Page Header -->
      <header class="page-header">
        <h1>Catálogo de Productos</h1>
        <p class="subtitle">Gestión de Inventario y Ventas</p>

        <!-- Search bar -->
        <div class="search-wrapper">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Buscar por nombre, SKU o descripción..." 
            class="search-input"
          />
          <span v-if="searchQuery" @click="searchQuery = ''" class="clear-btn">✕</span>
        </div>
      </header>

      <!-- Admin Panel -->
      <div v-if="userRole === 'admin'" class="admin-panel">
        <div class="panel-header">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            {{ isEditing ? 'Editar Producto' : 'Nuevo Producto' }}
          </h2>
          <button v-if="isEditing" @click="cancelEdit" class="cancel-btn">Cancelar</button>
        </div>

        <form @submit.prevent="saveProduct" class="admin-form">
          <div class="form-row">
            <div class="input-group">
              <label>Nombre</label>
              <input v-model="newProduct.name" placeholder="Ej: Monitor 24''" required />
            </div>
            <div class="input-group">
              <label>SKU</label>
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
              <label>Stock</label>
              <input v-model.number="newProduct.stock" type="number" required />
            </div>
            <button type="submit" class="create-btn">
              {{ isEditing ? '💾 Guardar' : '➕ Añadir' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Error state -->
      <div v-if="error" class="error-banner">{{ error }}</div>

      <!-- Empty search -->
      <div v-else-if="filteredProducts.length === 0" class="no-results">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <p>No se encontraron productos para "<strong>{{ searchQuery }}</strong>"</p>
      </div>

      <!-- Product Grid -->
      <div v-else class="product-grid">
        <div 
          v-for="(product, index) in filteredProducts" 
          :key="product.id" 
          class="product-card"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <div class="card-image">
            <div class="card-image-pattern"></div>
            <span class="card-sku-badge">{{ product.sku }}</span>
          </div>

          <div class="card-body">
            <h3>{{ product.name }}</h3>
            <p class="description">{{ product.description || 'Sin descripción' }}</p>
            
            <div class="card-footer">
              <div class="price-row">
                <span class="price">{{ product.price.toFixed(2) }} €</span>
                <span :class="['stock-badge', product.stock < 5 ? 'low' : product.stock === 0 ? 'out' : 'good']">
                  {{ product.stock > 0 ? `${product.stock} en stock` : 'Agotado' }}
                </span>
              </div>
              
              <button 
                v-if="userRole !== 'admin'" 
                @click="addToCart(product)" 
                :disabled="product.stock === 0"
                class="buy-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                {{ product.stock > 0 ? 'Añadir al Carrito' : 'Agotado' }}
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
/* Layout */
.main-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  padding-top: 100px;
}

/* ---- Navbar ---- */
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(10, 10, 20, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-color);
  z-index: 1000;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.8rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.logo span {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.nav-actions {
  display: flex;
  gap: 8px;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.nav-btn:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
  border-color: var(--border-color-hover);
}

.nav-btn svg {
  opacity: 0.7;
}

.admin-nav-btn {
  border-color: rgba(108, 92, 231, 0.3);
  color: var(--color-primary-light);
}

.admin-nav-btn:hover {
  background: rgba(108, 92, 231, 0.1);
  border-color: var(--color-primary);
}

.cart-nav-btn {
  border-color: rgba(0, 206, 201, 0.3);
  color: var(--color-accent);
}

.cart-nav-btn:hover {
  background: rgba(0, 206, 201, 0.1);
  border-color: var(--color-accent);
}

.nav-btn-danger {
  border-color: rgba(255, 118, 117, 0.2);
  color: var(--color-danger);
}

.nav-btn-danger:hover {
  background: rgba(255, 118, 117, 0.1);
  border-color: var(--color-danger);
}

/* ---- Page Header ---- */
.page-header {
  margin-bottom: 2.5rem;
  text-align: center;
  animation: fadeInUp 0.5s ease;
}

.page-header h1 {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-top: 0.3rem;
}

/* ---- Search ---- */
.search-wrapper {
  position: relative;
  max-width: 500px;
  margin: 1.5rem auto 0;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 40px 14px 48px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: all var(--transition-normal);
}

.search-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
  background: var(--bg-surface-hover);
}

.search-input::placeholder { color: var(--text-muted); }

.clear-btn {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--text-muted);
  font-size: 1rem;
  transition: color var(--transition-fast);
  background: none;
  border: none;
  display: flex;
  align-items: center;
}

.clear-btn:hover { color: var(--color-danger); }

/* ---- Admin Panel ---- */
.admin-panel {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--color-warning);
  padding: 2rem;
  border-radius: var(--radius-lg);
  margin-bottom: 2.5rem;
  animation: fadeInUp 0.5s ease;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-size: 1.3rem;
  font-weight: 700;
}

.cancel-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  transition: all var(--transition-fast);
}

.cancel-btn:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.admin-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 180px;
}

.input-group label {
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.input-group input {
  padding: 10px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: all var(--transition-normal);
}

.input-group input:focus {
  border-color: var(--color-warning);
  box-shadow: 0 0 0 3px rgba(253, 203, 110, 0.15);
}

.create-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all var(--transition-normal);
  height: 42px;
  white-space: nowrap;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(243, 156, 18, 0.3);
}

/* ---- Error / No Results ---- */
.error-banner {
  background: rgba(255, 118, 117, 0.1);
  border: 1px solid rgba(255, 118, 117, 0.2);
  color: var(--color-danger);
  padding: 1rem;
  border-radius: var(--radius-md);
  text-align: center;
}

.no-results {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

/* ---- Product Grid ---- */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* ---- Product Card ---- */
.product-card {
  background: var(--bg-glass);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  animation: fadeInUp 0.5s ease backwards;
}

.product-card:hover {
  transform: translateY(-6px);
  border-color: var(--border-color-hover);
  box-shadow: var(--shadow-md), 0 0 30px rgba(108, 92, 231, 0.08);
}

.card-image {
  height: 140px;
  position: relative;
  overflow: hidden;
}

.card-image-pattern {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(108, 92, 231, 0.15) 0%, rgba(0, 206, 201, 0.1) 100%);
}

.card-sku-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  color: var(--text-secondary);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
}

.card-body {
  padding: 1.5rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-body h3 {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.4rem;
}

.description {
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.5;
  margin-bottom: 1.2rem;
  flex-grow: 1;
}

.card-footer {
  margin-top: auto;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.price {
  font-size: 1.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stock-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
}

.stock-badge.good {
  background: rgba(0, 184, 148, 0.15);
  color: var(--color-success);
}

.stock-badge.low {
  background: rgba(255, 118, 117, 0.15);
  color: var(--color-danger);
}

.stock-badge.out {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

/* ---- Buy Button ---- */
.buy-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, var(--color-primary), #8b7cf7);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.buy-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-primary);
}

.buy-btn:disabled {
  background: var(--bg-surface);
  color: var(--text-muted);
  cursor: not-allowed;
  border: 1px solid var(--border-color);
}

/* ---- Admin Actions ---- */
.admin-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all var(--transition-normal);
}

.action-btn.edit {
  background: rgba(52, 152, 219, 0.15);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.action-btn.edit:hover {
  background: rgba(52, 152, 219, 0.25);
}

.action-btn.delete {
  background: rgba(255, 118, 117, 0.15);
  color: var(--color-danger);
  border: 1px solid rgba(255, 118, 117, 0.2);
}

.action-btn.delete:hover {
  background: rgba(255, 118, 117, 0.25);
}

/* ---- Toast ---- */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  padding: 14px 24px;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-md);
}

.toast.success {
  background: rgba(0, 184, 148, 0.15);
  border: 1px solid rgba(0, 184, 148, 0.3);
  color: var(--color-success);
}

.toast.error {
  background: rgba(255, 118, 117, 0.15);
  border: 1px solid rgba(255, 118, 117, 0.3);
  color: var(--color-danger);
}

.toast-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 800;
}

.toast.success .toast-icon { background: rgba(0, 184, 148, 0.2); }
.toast.error .toast-icon { background: rgba(255, 118, 117, 0.2); }

.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastIn 0.3s ease reverse; }

@keyframes toastIn {
  from { opacity: 0; transform: translateX(40px); }
  to   { opacity: 1; transform: translateX(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>