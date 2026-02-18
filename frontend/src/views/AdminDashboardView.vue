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

// CAMBIO: Variable de entorno
const apiUrl = import.meta.env.VITE_API_URL

if (role !== 'admin') router.push('/products')

const fetchAllOrders = async () => {
  try {
    // CAMBIO: Usar apiUrl
    const response = await fetch(`${apiUrl}/admin/orders`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    allOrders.value = await response.json()
  } catch (e) { console.error('Error cargando pedidos:', e) }
}

const fetchStats = async () => {
  try {
    // CAMBIO: Usar apiUrl
    const response = await fetch(`${apiUrl}/admin/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    stats.value = await response.json()
  } catch (e) { console.error('Error cargando estadísticas:', e) }
}

const updateStatus = async (orderId, newStatus) => {
  try {
    // CAMBIO: Usar apiUrl
    await fetch(`${apiUrl}/orders/${orderId}/status?status=${newStatus}`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    fetchAllOrders()
    fetchStats()
  } catch (e) { console.error(e) }
}

const downloadInvoice = async (orderId) => {
  try {
    // CAMBIO: Usar apiUrl
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
  } catch (e) { alert('❌ ' + e.message) }
}

// --- CHART CONFIG (Dark Theme) ---
const darkGridColor = 'rgba(255,255,255,0.06)'
const darkTickColor = 'rgba(255,255,255,0.4)'

const barChartData = computed(() => {
  if (!stats.value || !stats.value.monthly_sales.length) return null
  return {
    labels: stats.value.monthly_sales.map(m => `${MONTH_NAMES[m.month - 1]} ${m.year}`),
    datasets: [{
      label: 'Ingresos (€)',
      data: stats.value.monthly_sales.map(m => m.revenue),
      backgroundColor: 'rgba(108, 92, 231, 0.5)',
      borderColor: '#6c5ce7',
      borderWidth: 2,
      borderRadius: 8
    }]
  }
})

const barChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y.toFixed(2)} €` } }
  },
  scales: {
    y: { beginAtZero: true, ticks: { callback: (v) => v + ' €', color: darkTickColor }, grid: { color: darkGridColor } },
    x: { ticks: { color: darkTickColor }, grid: { display: false } }
  }
}

const doughnutData = computed(() => {
  if (!stats.value || !stats.value.top_products.length) return null
  const colors = ['#6c5ce7', '#00cec9', '#fdcb6e', '#ff7675', '#a29bfe']
  return {
    labels: stats.value.top_products.map(p => p.name),
    datasets: [{
      data: stats.value.top_products.map(p => p.units_sold),
      backgroundColor: colors.slice(0, stats.value.top_products.length),
      borderWidth: 0
    }]
  }
})

const doughnutOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { padding: 15, font: { size: 12 }, color: darkTickColor } } }
}

const lineChartData = computed(() => {
  if (!stats.value || !stats.value.monthly_sales.length) return null
  return {
    labels: stats.value.monthly_sales.map(m => `${MONTH_NAMES[m.month - 1]} ${m.year}`),
    datasets: [{
      label: 'Pedidos',
      data: stats.value.monthly_sales.map(m => m.orders),
      borderColor: '#00cec9',
      backgroundColor: 'rgba(0, 206, 201, 0.08)',
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointBackgroundColor: '#00cec9'
    }]
  }
})

const lineChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1, color: darkTickColor }, grid: { color: darkGridColor } },
    x: { ticks: { color: darkTickColor }, grid: { display: false } }
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(() => { fetchAllOrders(); fetchStats() })
</script>

<template>
  <div class="dashboard-layout">
    <!-- Header -->
    <header class="dash-header">
      <div class="title-group">
        <div class="admin-badge">ADMIN</div>
        <h1>Panel de Gerencia</h1>
        <p class="subtitle">LibnamicShop · Business Intelligence</p>
      </div>
      <button @click="router.push('/products')" class="back-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Catálogo
      </button>
    </header>

    <!-- KPI Cards -->
    <div class="kpi-row" v-if="stats">
      <div class="kpi-card">
        <div class="kpi-icon-wrapper revenue-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="kpi-data">
          <span class="kpi-value">{{ stats.total_revenue.toFixed(2) }} €</span>
          <span class="kpi-label">Ingresos Totales</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon-wrapper orders-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
        </div>
        <div class="kpi-data">
          <span class="kpi-value">{{ stats.total_orders }}</span>
          <span class="kpi-label">Pedidos Totales</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon-wrapper ticket-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
        </div>
        <div class="kpi-data">
          <span class="kpi-value">{{ stats.avg_ticket.toFixed(2) }} €</span>
          <span class="kpi-label">Ticket Medio</span>
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
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

    <!-- Orders Table -->
    <div class="section-header">
      <h2>Gestión de Envíos y Clientes</h2>
      <span class="order-count">{{ allOrders.length }} pedidos</span>
    </div>
    
    <div class="table-wrapper">
      <table class="custom-table">
        <thead>
          <tr>
            <th>Pedido</th>
            <th>Cliente / Contacto</th>
            <th>Fecha</th>
            <th>Importe</th>
            <th>Estado</th>
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
                <span v-if="order.owner.phone" class="client-phone">📞 {{ order.owner.phone }}</span>
              </div>
            </td>
            <td class="date-cell">{{ formatDate(order.created_at) }}</td>
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
                Enviar
              </button>

              <button 
                v-else-if="order.status === 'ENVIADO'"
                @click="updateStatus(order.id, 'ENTREGADO')" 
                class="btn-action complete">
                ✅ Entregado
              </button>

              <span v-if="order.status === 'ENTREGADO'" class="closed-label">
                Cerrado
              </span>

              <button @click="downloadInvoice(order.id)" class="btn-action invoice" title="Descargar factura">
                📄 Exportar PDF
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Header */
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  animation: fadeInUp 0.4s ease;
}

.title-group { display: flex; flex-direction: column; gap: 2px; }

.admin-badge {
  display: inline-block;
  width: fit-content;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.dash-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.back-btn:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
}

/* KPI Cards */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all var(--transition-normal);
  animation: fadeInUp 0.5s ease backwards;
}

.kpi-card:nth-child(1) { animation-delay: 0s; }
.kpi-card:nth-child(2) { animation-delay: 0.1s; }
.kpi-card:nth-child(3) { animation-delay: 0.2s; }

.kpi-card:hover {
  border-color: var(--border-color-hover);
  transform: translateY(-2px);
}

.kpi-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.revenue-icon {
  background: rgba(0, 184, 148, 0.12);
  color: var(--color-success);
}

.orders-icon {
  background: rgba(108, 92, 231, 0.12);
  color: var(--color-primary-light);
}

.ticket-icon {
  background: rgba(253, 203, 110, 0.12);
  color: var(--color-warning);
}

.kpi-data { display: flex; flex-direction: column; }

.kpi-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
}

.kpi-label {
  font-size: 0.78rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

/* Charts */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.chart-card {
  background: var(--bg-glass);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  animation: fadeInUp 0.5s ease backwards;
}

.chart-card.wide { grid-column: 1 / -1; }

.chart-card h3 {
  margin: 0 0 1rem;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 700;
}

.chart-wrapper {
  height: 250px;
  position: relative;
}

.no-data {
  text-align: center;
  color: var(--text-muted);
  padding-top: 80px;
}

/* Section header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
}

.order-count {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* Table */
.table-wrapper {
  background: var(--bg-glass);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow-x: auto;
  animation: fadeInUp 0.5s ease;
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.custom-table th {
  background: rgba(255,255,255,0.03);
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
}

.custom-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  vertical-align: middle;
  color: var(--text-secondary);
}

.custom-table tbody tr {
  transition: background var(--transition-fast);
}

.custom-table tbody tr:hover {
  background: var(--bg-surface-hover);
}

.id-cell {
  font-weight: 700;
  color: var(--text-primary);
}

.client-info { display: flex; flex-direction: column; gap: 2px; }
.client-name { font-weight: 600; color: var(--text-primary); font-size: 0.9rem; }
.client-email { font-size: 0.78rem; color: var(--text-muted); }
.client-phone { font-size: 0.78rem; color: var(--text-muted); }
.date-cell { font-size: 0.85rem; }
.price-cell { font-weight: 700; color: var(--text-primary); font-size: 1rem; }

/* Status pills */
.status-pill {
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-pill.pendiente {
  background: rgba(253, 203, 110, 0.12);
  color: var(--color-warning);
}

.status-pill.enviado {
  background: rgba(108, 92, 231, 0.12);
  color: var(--color-primary-light);
}

.status-pill.entregado {
  background: rgba(0, 184, 148, 0.12);
  color: var(--color-success);
}

/* Action buttons */
.actions-cell {
  display: flex;
  gap: 6px;
  align-items: center;
}

.btn-action {
  padding: 6px 14px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  font-size: 0.8rem;
  transition: all var(--transition-normal);
}

.ship {
  background: rgba(108, 92, 231, 0.15);
  color: var(--color-primary-light);
  border: 1px solid rgba(108, 92, 231, 0.2);
}

.ship:hover {
  background: rgba(108, 92, 231, 0.25);
}

.complete {
  background: rgba(0, 184, 148, 0.15);
  color: var(--color-success);
  border: 1px solid rgba(0, 184, 148, 0.2);
}

.complete:hover {
  background: rgba(0, 184, 148, 0.25);
}

.invoice {
  background: rgba(162, 155, 254, 0.12);
  color: var(--color-primary-light);
  border: 1px solid rgba(162, 155, 254, 0.2);
}

.invoice:hover {
  background: rgba(162, 155, 254, 0.22);
}

.closed-label {
  color: var(--text-muted);
  font-size: 0.8rem;
  font-style: italic;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>