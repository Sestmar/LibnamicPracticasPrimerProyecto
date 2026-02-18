<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  ArcElement, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js'

// Registramos los componentes de Chart.js que vamos a usar
ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  ArcElement, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
)

const MONTH_NAMES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

const allOrders = ref([])
const stats = ref(null)
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
    allOrders.value = await response.json()
  } catch (e) {
    console.error('Error cargando pedidos:', e)
  }
}

const fetchStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/admin/stats', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    stats.value = await response.json()
  } catch (e) {
    console.error('Error cargando estadísticas:', e)
  }
}

// --- ACTUALIZAR ESTADO DE PEDIDO ---
const updateStatus = async (orderId, newStatus) => {
  try {
    await fetch(`http://localhost:8000/orders/${orderId}/status?status=${newStatus}`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    fetchAllOrders()
    fetchStats() // Refrescamos métricas tras cambiar estado
  } catch (e) {
    console.error(e)
  }
}

// --- DESCARGAR FACTURA PDF ---
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

// --- CONFIGURACIÓN DE GRÁFICOS ---

// Gráfico de barras: Ingresos por mes
const barChartData = computed(() => {
  if (!stats.value || !stats.value.monthly_sales.length) return null
  return {
    labels: stats.value.monthly_sales.map(m => `${MONTH_NAMES[m.month - 1]} ${m.year}`),
    datasets: [{
      label: 'Ingresos (€)',
      data: stats.value.monthly_sales.map(m => m.revenue),
      backgroundColor: 'rgba(52, 152, 219, 0.7)',
      borderColor: '#3498db',
      borderWidth: 2,
      borderRadius: 6
    }]
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: { label: (ctx) => `${ctx.parsed.y.toFixed(2)} €` }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (v) => v + ' €' }
    }
  }
}

// Gráfico de dona: Top 5 productos
const doughnutData = computed(() => {
  if (!stats.value || !stats.value.top_products.length) return null
  const colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
  return {
    labels: stats.value.top_products.map(p => p.name),
    datasets: [{
      data: stats.value.top_products.map(p => p.units_sold),
      backgroundColor: colors.slice(0, stats.value.top_products.length),
      borderWidth: 2,
      borderColor: '#fff'
    }]
  }
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { padding: 15, font: { size: 12 } } }
  }
}

// Gráfico de línea: Evolución de pedidos por mes
const lineChartData = computed(() => {
  if (!stats.value || !stats.value.monthly_sales.length) return null
  return {
    labels: stats.value.monthly_sales.map(m => `${MONTH_NAMES[m.month - 1]} ${m.year}`),
    datasets: [{
      label: 'Pedidos',
      data: stats.value.monthly_sales.map(m => m.orders),
      borderColor: '#2ecc71',
      backgroundColor: 'rgba(46, 204, 113, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointBackgroundColor: '#2ecc71'
    }]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1 } }
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(() => {
  fetchAllOrders()
  fetchStats()
})
</script>

<template>
  <div class="dashboard-container">
    
    <header class="header">
      <div class="title-group">
        <h1>Panel de Gerencia</h1>
        <p class="subtitle">Libnamic ERP System v2.0</p>
      </div>
      <button @click="router.push('/products')" class="back-btn">← Volver al Catálogo</button>
    </header>

    <!-- KPI CARDS -->
    <div class="kpi-row" v-if="stats">
      <div class="kpi-card revenue">
        <span class="kpi-icon">💰</span>
        <div class="kpi-data">
          <span class="kpi-value">{{ stats.total_revenue.toFixed(2) }} €</span>
          <span class="kpi-label">Ingresos Totales</span>
        </div>
      </div>
      <div class="kpi-card orders">
        <span class="kpi-icon">📦</span>
        <div class="kpi-data">
          <span class="kpi-value">{{ stats.total_orders }}</span>
          <span class="kpi-label">Pedidos Totales</span>
        </div>
      </div>
      <div class="kpi-card ticket">
        <span class="kpi-icon">🎫</span>
        <div class="kpi-data">
          <span class="kpi-value">{{ stats.avg_ticket.toFixed(2) }} €</span>
          <span class="kpi-label">Ticket Medio</span>
        </div>
      </div>
    </div>

    <!-- GRÁFICOS -->
    <div class="charts-grid" v-if="stats">
      <div class="chart-card wide">
        <h3>Ingresos Mensuales</h3>
        <div class="chart-wrapper">
          <Bar v-if="barChartData" :data="barChartData" :options="barChartOptions" />
          <p v-else class="no-data">Aún no hay datos de ventas</p>
        </div>
      </div>

      <div class="chart-card">
        <h3>Productos Más Vendidos</h3>
        <div class="chart-wrapper">
          <Doughnut v-if="doughnutData" :data="doughnutData" :options="doughnutOptions" />
          <p v-else class="no-data">Aún no hay ventas registradas</p>
        </div>
      </div>

      <div class="chart-card">
        <h3>Evolución de Pedidos</h3>
        <div class="chart-wrapper">
          <Line v-if="lineChartData" :data="lineChartData" :options="lineChartOptions" />
          <p v-else class="no-data">Aún no hay datos de pedidos</p>
        </div>
      </div>
    </div>

    <!-- TABLA DE GESTIÓN DE PEDIDOS -->
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
                <span class="client-name">{{ order.owner.first_name }} {{ order.owner.last_name }}</span>
                <span class="client-email">{{ order.owner.email }}</span>
                <span v-if="order.owner.phone" class="client-email">📞 {{ order.owner.phone }}</span>
              </div>
            </td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td class="price-cell">{{ order.total_price.toFixed(2) }} €</td>
            
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
                v-else-if="order.status === 'ENVIADO'"
                @click="updateStatus(order.id, 'ENTREGADO')" 
                class="btn-action complete">
                ✅ Confirmar Entrega
              </button>

              <span v-if="order.status === 'ENTREGADO'" class="text-muted">
                Ciclo cerrado
              </span>

              <button @click="downloadInvoice(order.id)" class="btn-action invoice" title="Descargar factura">
                📄 PDF
              </button>
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

/* HEADER */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.title-group h1 { font-size: 2rem; color: #1a202c; margin: 0; }
.subtitle { color: #718096; margin: 0; }
.back-btn { background: white; border: 1px solid #e2e8f0; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
.back-btn:hover { background: #f7fafc; border-color: #cbd5e0; }

/* KPI CARDS */
.kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border-left: 4px solid;
}
.kpi-card.revenue { border-color: #2ecc71; }
.kpi-card.orders { border-color: #3498db; }
.kpi-card.ticket { border-color: #f39c12; }
.kpi-icon { font-size: 2rem; }
.kpi-data { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.75rem; font-weight: 800; color: #1a202c; }
.kpi-label { font-size: 0.85rem; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }

/* CHARTS GRID */
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 3rem; }
.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.chart-card.wide { grid-column: 1 / -1; }
.chart-card h3 { margin: 0 0 1rem; color: #2c3e50; font-size: 1.1rem; }
.chart-wrapper { height: 250px; position: relative; }
.no-data { text-align: center; color: #a0aec0; padding-top: 80px; }

/* TABLE */
.section-title { font-size: 1.5rem; color: #2c3e50; margin-bottom: 1.5rem; margin-top: 1rem; }
.table-wrapper { background: white; border-radius: 12px; overflow-x: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.custom-table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.custom-table th { background: #f8f9fa; padding: 14px 16px; text-align: left; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; color: #718096; border-bottom: 2px solid #edf2f7; }
.custom-table td { padding: 14px 16px; border-bottom: 1px solid #f0f4f8; vertical-align: middle; }
.id-cell { font-weight: bold; color: #2c3e50; }

/* CLIENT INFO */
.client-info { display: flex; flex-direction: column; gap: 2px; }
.client-name { font-weight: 600; color: #2d3748; }
.client-email { font-size: 0.8rem; color: #95a5a6; }

/* STATUS PILLS */
.status-pill { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.status-pill.pendiente { background: #fff3cd; color: #856404; }
.status-pill.enviado { background: #dbeafe; color: #1e40af; }
.status-pill.entregado { background: #d1fae5; color: #065f46; }

/* BUTTONS */
.btn-action { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; color: white; font-size: 0.85rem; transition: all 0.2s; }
.ship { background: #3498db; box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3); }
.ship:hover { background: #2980b9; }
.complete { background: #27ae60; box-shadow: 0 2px 5px rgba(39, 174, 96, 0.3); }
.complete:hover { background: #219150; }
.text-muted { color: #bdc3c7; font-style: italic; font-size: 0.9rem; }
.price-cell { font-weight: bold; font-size: 1.1rem; }
.invoice { background: #8e44ad; box-shadow: 0 2px 5px rgba(142, 68, 173, 0.3); }
.invoice:hover { background: #7d389e; }
.actions-cell { display: flex; gap: 8px; align-items: center; }
</style>