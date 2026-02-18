<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const orders = ref([])
const error = ref('')
const router = useRouter()
const token = localStorage.getItem('token')

if (!token) { router.push('/login') }

const fetchOrders = async () => {
  try {
    // Llamo al endpoint
    const response = await fetch('http://localhost:8000/orders/my-orders', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) throw new Error('Error al cargar pedidos')
    
    // Guardp la lista de pedidos
    orders.value = await response.json()
    // Invierto el orden para ver los más nuevos primero
    orders.value.reverse()
    
  } catch (e) {
    error.value = e.message
  }
}

// Función auxiliar para formatear la fecha fea que viene del backend
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const goBack = () => router.push('/products')

const downloadInvoice = async (orderId) => {
  try {
    const response = await fetch(`http://localhost:8000/orders/${orderId}/invoice`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('Error al descargar factura')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `factura_${orderId}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    alert('❌ ' + e.message)
  }
}

onMounted(fetchOrders)
</script>

<template>
  <div class="container">
    <header>
      <h1>📜 Mis Pedidos</h1>
      <button @click="goBack" class="back-btn">⬅ Volver al Catálogo</button>
    </header>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-else class="orders-list">
      <div v-if="orders.length === 0" class="no-orders">
        Aún no has hecho ningún pedido.
      </div>

      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="order-id">Pedido #{{ order.id }}</span>
          <span class="order-date">{{ formatDate(order.created_at) }}</span>
          <span class="order-status status-completed">{{ order.status }}</span>
        </div>
        
        <div class="order-items">
          <div v-for="item in order.items" :key="item.product_id" class="item-row">
             <span>Producto ID: <strong>{{ item.product_id }}</strong></span>
            <span>Cant: {{ item.quantity }}</span>
            <span>Precio ud: {{ item.unit_price }} €</span>
          </div>
        </div>

        <div class="order-footer">
          <span class="order-total">Total Pagado: <strong>{{ order.total_price.toFixed(2) }} €</strong></span>
          <button @click="downloadInvoice(order.id)" class="invoice-btn">📄 Descargar Factura</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container { max-width: 800px; margin: 0 auto; padding: 20px; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.back-btn { background: #666; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
.order-card { border: 1px solid #eee; border-radius: 8px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.order-header { background: #f8f9fa; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; }
.order-id { font-weight: bold; }
.order-date { color: #666; font-size: 0.9em; }
.order-status { padding: 4px 8px; border-radius: 12px; font-size: 0.8em; text-transform: uppercase; }
.status-completed { background: #d4edda; color: #155724; }
.order-items { padding: 15px; }
.item-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #eee; }
.order-total { padding: 15px; background: #fafafa; text-align: right; font-size: 1.1em; }
.no-orders { text-align: center; padding: 40px; color: #999; font-size: 1.2em; }
.order-footer { display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #fafafa; border-top: 1px solid #eee; }
.order-footer .order-total { padding: 0; background: none; }
.invoice-btn { background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: background 0.2s; }
.invoice-btn:hover { background: #2980b9; }
</style>