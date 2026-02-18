<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const allOrders = ref([])
const router = useRouter()
const token = localStorage.getItem('token')
const role = localStorage.getItem('role')

if (role !== 'admin') router.push('/products')

// --- CARGAR DATOS ---
const fetchAllOrders = async () => {
  try {
    const response = await fetch('http://localhost:8000/admin/orders', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      allOrders.value = await response.json()
      allOrders.value.reverse() // Más recientes arriba
    }
  } catch (e) {
    console.error(e)
  }
}

// --- ACTUALIZAR ESTADO ---
const updateStatus = async (orderId, newStatus) => {
  try {
    const response = await fetch(`http://localhost:8000/orders/${orderId}/status?status=${newStatus}`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const order = allOrders.value.find(o => o.id === orderId)
      if (order) order.status = newStatus
      // No alertamos para que sea más rápido trabajar
    }
  } catch (e) {
    alert('Error al conectar')
  }
}

// --- LÓGICA DEL GRÁFICO (Ingresos por Estado) ---
const chartData = computed(() => {
  const data = {
    'PENDIENTE': 0,
    'ENVIADO': 0,
    'ENTREGADO': 0
  }
  
  allOrders.value.forEach(order => {
    // Si el estado existe en nuestro objeto, sumamos el total
    if (data[order.status]) {
      data[order.status] += order.total_price
    } else {
      // Por si hay estados antiguos o raros
      data[order.status] = (data[order.status] || 0) + order.total_price
    }
  })
  
  // Encontrar el valor máximo para escalar las barras (100% de altura)
  const maxVal = Math.max(...Object.values(data)) || 1 
  
  return Object.keys(data).map(key => ({
    label: key,
    value: data[key],
    height: (data[key] / maxVal) * 100 + '%'
  }))
})

const formatDate = (dateString) => {
  const d = new Date(dateString)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

onMounted(fetchAllOrders)
</script>

<template>
  <div class="dashboard-container">
    
    <header class="header">
      <div class="title-group">
        <h1>Panel de Gerencia</h1>
        <p class="subtitle">Libnamic ERP System v2.0</p>
      </div>
      <button @click="router.push('/products')" class="nav-btn">⬅ Volver al Catálogo</button>
    </header>

    <div class="metrics-grid">
      
      <div class="card kpi-card">
        <h3>Resumen Financiero</h3>
        <div class="kpi-row">
          <div class="kpi">
            <span>Ingresos Totales</span>
            <strong>{{ allOrders.reduce((sum, o) => sum + o.total_price, 0).toFixed(2) }} €</strong>
          </div>
          <div class="kpi">
            <span>Pedidos Activos</span>
            <strong style="color: #f39c12">
              {{ allOrders.filter(o => o.status !== 'ENTREGADO').length }}
            </strong>
          </div>
        </div>
      </div>

      <div class="card chart-card">
        <h3>Flujo de Caja por Estado</h3>
        <div class="chart-container">
          <div v-for="bar in chartData" :key="bar.label" class="bar-group">
            <div class="bar-value">{{ bar.value.toFixed(0) }}€</div>
            <div class="bar" :style="{ height: bar.height, background: bar.label === 'ENTREGADO' ? '#27ae60' : '#3498db' }"></div>
            <div class="bar-label">{{ bar.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <h2 class="section-title">Gestión de Envíos y Clientes</h2>
    
    <div class="table-wrapper">
      <table class="custom-table">
        <thead>
          <tr>
            <th>Pedido</th>
            <th>Cliente / Contacto</th> <th>Fecha Compra</th>
            <th>Importe</th>
            <th>Estado Logístico</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in allOrders" :key="order.id">
            <td class="id-cell">#{{ order.id }}</td>
            
            <td>
              <div class="client-info">
                <span class="client-name">👤 {{ order.owner.first_name }} {{ order.owner.last_name }}</span>
                <span class="client-phone">📞 {{ order.owner.phone || 'Sin teléfono' }}</span>
                <span class="client-email">✉️ {{ order.owner.email }}</span>
              </div>
            </td>

            <td>{{ formatDate(order.created_at) }}</td>
            <td class="price-cell">{{ order.total_price }} €</td>
            
            <td>
              <span :class="['status-pill', order.status.toLowerCase()]">
                {{ order.status }}
              </span>
            </td>
            
            <td class="actions-cell">
              <button 
                v-if="order.status === 'PENDIENTE'"
                @click="updateStatus(order.id, 'ENVIADO')" 
                class="btn-action ship">
                Marcar Enviado
              </button>

              <button 
                v-if="order.status === 'ENVIADO'"
                @click="updateStatus(order.id, 'ENTREGADO')" 
                class="btn-action complete">
                ✅ Confirmar Entrega
              </button>

              <span v-if="order.status === 'ENTREGADO'" class="text-muted">
                Ciclo cerrado
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* GENERAL */
.dashboard-container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; font-family: 'Segoe UI', sans-serif; background-color: #f4f6f9; min-height: 100vh; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.title-group h1 { margin: 0; color: #2c3e50; font-size: 1.8rem; }
.subtitle { margin: 5px 0 0; color: #7f8c8d; }
.nav-btn { background: white; border: 1px solid #ccc; padding: 10px 20px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
.nav-btn:hover { background: #e2e6ea; }

/* METRICS GRID */
.metrics-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 40px; }
.card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.card h3 { margin-top: 0; color: #7f8c8d; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }

/* KPI CARD */
.kpi-row { display: flex; flex-direction: column; gap: 20px; margin-top: 20px; }
.kpi span { display: block; font-size: 0.9rem; color: #666; margin-bottom: 5px; }
.kpi strong { font-size: 1.8rem; color: #2c3e50; }

/* CHART CSS (Simple bars) */
.chart-container { display: flex; justify-content: space-around; align-items: flex-end; height: 150px; margin-top: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
.bar-group { display: flex; flex-direction: column; align-items: center; width: 30%; height: 100%; justify-content: flex-end; }
.bar { width: 40px; border-radius: 4px 4px 0 0; transition: height 0.5s ease; min-height: 4px; }
.bar-value { font-size: 0.8rem; font-weight: bold; margin-bottom: 5px; color: #2c3e50; }
.bar-label { margin-top: 10px; font-size: 0.8rem; color: #7f8c8d; font-weight: 600; }

/* TABLE */
.section-title { color: #2c3e50; margin-bottom: 20px; font-size: 1.4rem; }
.table-wrapper { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.custom-table { width: 100%; border-collapse: collapse; text-align: left; }
.custom-table th { background: #f8f9fa; padding: 18px; color: #555; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; }
.custom-table td { padding: 18px; border-bottom: 1px solid #eee; vertical-align: middle; }

/* CLIENT INFO */
.client-info { display: flex; flex-direction: column; gap: 2px; }
.client-name { font-weight: bold; color: #2c3e50; }
.client-phone { font-size: 0.85rem; color: #e67e22; font-weight: 600; }
.client-email { font-size: 0.8rem; color: #95a5a6; }

/* STATUS PILLS */
.status-pill { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.status-pill.pendiente { background: #fff3cd; color: #856404; }
.status-pill.enviado { background: #dbeafe; color: #1e40af; }
.status-pill.entregado { background: #d1fae5; color: #065f46; }

/* BUTTONS */
.btn-action { border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600; color: white; transition: transform 0.1s; }
.btn-action:active { transform: scale(0.95); }
.ship { background: #3498db; box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3); }
.ship:hover { background: #2980b9; }
.complete { background: #27ae60; box-shadow: 0 2px 5px rgba(39, 174, 96, 0.3); }
.complete:hover { background: #219150; }
.text-muted { color: #bdc3c7; font-style: italic; font-size: 0.9rem; }
.price-cell { font-weight: bold; font-size: 1.1rem; }
</style>