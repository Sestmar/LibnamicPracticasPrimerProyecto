<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const orders = ref([])
const error = ref('')
const router = useRouter()
const token = localStorage.getItem('token')

// CAMBIO: Definir la variable de entorno
const apiUrl = import.meta.env.VITE_API_URL

if (!token) { router.push('/login') }

const fetchOrders = async () => {
  try {
    // CAMBIO: Usar ${apiUrl} con comillas invertidas
    const response = await fetch(`${apiUrl}/orders/my-orders`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('Error al cargar pedidos')
    orders.value = await response.json()
    orders.value.reverse()
  } catch (e) {
    error.value = e.message
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const goBack = () => router.push('/products')

const downloadInvoice = async (orderId) => {
  try {
    // CAMBIO: Usar ${apiUrl} con comillas invertidas
    const response = await fetch(`${apiUrl}/orders/${orderId}/invoice`, {
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

const statusConfig = {
  'PENDIENTE': { color: '#fdcb6e', bg: 'rgba(253, 203, 110, 0.12)', icon: '⏳', step: 1 },
  'ENVIADO': { color: '#6c5ce7', bg: 'rgba(108, 92, 231, 0.12)', icon: '📦', step: 2 },
  'ENTREGADO': { color: '#00b894', bg: 'rgba(0, 184, 148, 0.12)', icon: '✓', step: 3 }
}

const getStatusConfig = (status) => statusConfig[status] || statusConfig['PENDIENTE']

onMounted(fetchOrders)
</script>

<template>
  <div class="orders-layout">
    <header class="orders-header">
      <button @click="goBack" class="back-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Catálogo
      </button>
      <h1>Mis Pedidos</h1>
      <span class="order-count">{{ orders.length }} pedido{{ orders.length !== 1 ? 's' : '' }}</span>
    </header>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <div v-else-if="orders.length === 0" class="empty-state">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <h2>Sin pedidos todavía</h2>
      <p>Cuando realices compras, aparecerán aquí</p>
    </div>

    <div v-else class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <!-- Order header -->
        <div class="order-header">
          <div class="order-id-group">
            <span class="order-id">#{{ order.id }}</span>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
          </div>
          <span class="status-badge" :style="{ color: getStatusConfig(order.status).color, background: getStatusConfig(order.status).bg }">
            {{ getStatusConfig(order.status).icon }} {{ order.status }}
          </span>
        </div>

        <!-- Timeline -->
        <div class="timeline">
          <div :class="['timeline-step', { active: getStatusConfig(order.status).step >= 1 }]">
            <div class="step-dot"></div>
            <span>Pendiente</span>
          </div>
          <div class="timeline-line" :class="{ filled: getStatusConfig(order.status).step >= 2 }"></div>
          <div :class="['timeline-step', { active: getStatusConfig(order.status).step >= 2 }]">
            <div class="step-dot"></div>
            <span>Enviado</span>
          </div>
          <div class="timeline-line" :class="{ filled: getStatusConfig(order.status).step >= 3 }"></div>
          <div :class="['timeline-step', { active: getStatusConfig(order.status).step >= 3 }]">
            <div class="step-dot"></div>
            <span>Entregado</span>
          </div>
        </div>

        <!-- Items -->
        <div class="order-items">
          <div v-for="item in order.items" :key="item.product_id" class="item-row">
            <span class="item-name">Producto #{{ item.product_id }}</span>
            <span class="item-qty">× {{ item.quantity }}</span>
            <span class="item-price">{{ item.unit_price.toFixed(2) }} €</span>
          </div>
        </div>

        <!-- Footer -->
        <div class="order-footer">
          <span class="order-total">
            Total: <strong>{{ order.total_price.toFixed(2) }} €</strong>
          </span>
          <button @click="downloadInvoice(order.id)" class="invoice-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            Factura PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.orders-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  animation: fadeInUp 0.4s ease;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.back-btn:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
}

.orders-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
}

.order-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Empty */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  animation: fadeInUp 0.5s ease;
}

.empty-state h2 { color: var(--text-primary); margin-top: 1rem; }
.empty-state p { color: var(--text-secondary); margin-top: 0.5rem; }

/* Error */
.error-banner {
  background: rgba(255, 118, 117, 0.1);
  border: 1px solid rgba(255, 118, 117, 0.2);
  color: var(--color-danger);
  padding: 1rem;
  border-radius: var(--radius-md);
  text-align: center;
}

/* Order card */
.order-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  margin-bottom: 1rem;
  overflow: hidden;
  transition: all var(--transition-normal);
  animation: fadeInUp 0.5s ease backwards;
}

.order-card:hover {
  border-color: var(--border-color-hover);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.order-id-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.order-id {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 1rem;
}

.order-date {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.status-badge {
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

/* Timeline */
.timeline {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  gap: 0;
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.step-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--border-color);
  transition: all var(--transition-normal);
}

.timeline-step.active .step-dot {
  background: var(--color-primary-light);
  box-shadow: 0 0 8px var(--color-primary-glow);
}

.timeline-step span {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 500;
}

.timeline-step.active span {
  color: var(--text-secondary);
}

.timeline-line {
  flex: 1;
  height: 2px;
  background: var(--border-color);
  margin: 0 4px;
  margin-bottom: 20px;
  transition: background var(--transition-normal);
}

.timeline-line.filled {
  background: var(--color-primary);
}

/* Items */
.order-items {
  padding: 1rem 1.5rem;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}

.item-row:last-child { border-bottom: none; }

.item-name { color: var(--text-secondary); font-size: 0.9rem; flex: 1; }
.item-qty { color: var(--text-muted); font-size: 0.85rem; margin: 0 1rem; }
.item-price { color: var(--text-primary); font-weight: 600; font-size: 0.9rem; }

/* Footer */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  background: rgba(255,255,255,0.02);
}

.order-total {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.order-total strong {
  color: var(--text-primary);
  font-size: 1.1rem;
}

.invoice-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(108, 92, 231, 0.12);
  color: var(--color-primary-light);
  border: 1px solid rgba(108, 92, 231, 0.2);
  border-radius: var(--radius-sm);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.invoice-btn:hover {
  background: rgba(108, 92, 231, 0.2);
  border-color: var(--color-primary);
  transform: translateY(-1px);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>