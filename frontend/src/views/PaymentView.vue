<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loadStripe } from '@stripe/stripe-js'

const router = useRouter()
const stripePromise = loadStripe('pk_test_51T2BSjCg7aB3krx8ZujcpTSWZMnCmIjyCMIw8duCMrmkBppwrqRG98LOtOQL2xGOGknucoh93INU4UO1DGKU7F3J00SczNV1zG')

const clientSecret = ref('')
const stripe = ref(null)
const elements = ref(null)
const message = ref('')
const isLoading = ref(false)
const cart = ref([])
const total = ref(0)

onMounted(async () => {
  cart.value = JSON.parse(localStorage.getItem('shopping_cart') || '[]')
  total.value = cart.value.reduce((acc, item) => acc + (item.price * item.quantity), 0)
  
  if (cart.value.length === 0) {
    router.push('/cart')
    return
  }

  try {
    const token = localStorage.getItem('token')
    const orderItems = cart.value.map(item => ({ product_id: item.id, quantity: item.quantity }))

    const response = await fetch('http://localhost:8000/create-payment-intent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ items: orderItems })
    })

    const data = await response.json()
    clientSecret.value = data.clientSecret

    stripe.value = await stripePromise
    elements.value = stripe.value.elements({ 
      clientSecret: clientSecret.value,
      appearance: {
        theme: 'night',
        variables: {
          colorPrimary: '#6c5ce7',
          colorBackground: '#1a1a2e',
          colorText: '#f0f0f5',
          colorDanger: '#ff7675',
          fontFamily: 'Inter, sans-serif',
          borderRadius: '12px',
          spacingUnit: '4px'
        }
      }
    })
    
    const paymentElement = elements.value.create('payment')
    paymentElement.mount('#payment-element')
    
  } catch (e) {
    message.value = "Error iniciando el pago: " + e.message
  }
})

const handleSubmit = async () => {
  if (!stripe.value || !elements.value) return
  isLoading.value = true
  
  const { error } = await stripe.value.confirmPayment({
    elements: elements.value,
    confirmParams: {
      return_url: window.location.origin + '/payment-success',
    },
    redirect: 'if_required' 
  })

  if (error) {
    message.value = error.message
    isLoading.value = false
  } else {
    await createOrderInBackend()
  }
}

const createOrderInBackend = async () => {
  try {
    const token = localStorage.getItem('token')
    const orderItems = cart.value.map(item => ({ product_id: item.id, quantity: item.quantity }))

    const response = await fetch('http://localhost:8000/orders/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ items: orderItems })
    })

    if (response.ok) {
      localStorage.removeItem('shopping_cart')
      alert('✅ ¡PAGO ACEPTADO! Tu pedido se ha procesado correctamente.')
      router.push('/my-orders')
    }
  } catch (e) {
    message.value = "Pago realizado, pero error al guardar pedido. Contacta soporte."
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="payment-layout">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <div class="payment-card">
      <!-- Header -->
      <div class="payment-header">
        <button @click="router.push('/cart')" class="back-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
          Volver
        </button>
        <div class="secure-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          Pago Seguro
        </div>
      </div>

      <h1>Finalizar Pago</h1>

      <!-- Order summary -->
      <div class="order-summary">
        <div v-for="item in cart" :key="item.id" class="summary-item">
          <span>{{ item.name }} × {{ item.quantity }}</span>
          <span>{{ (item.price * item.quantity).toFixed(2) }} €</span>
        </div>
        <div class="summary-total-row">
          <span>Total a pagar</span>
          <span class="total-value">{{ total.toFixed(2) }} €</span>
        </div>
      </div>

      <!-- Stripe form -->
      <form @submit.prevent="handleSubmit">
        <div id="payment-element"></div>
        
        <div v-if="message" class="error-msg">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ message }}
        </div>
        
        <button :disabled="isLoading || !stripe || !elements" class="pay-btn">
          <span v-if="isLoading" class="spinner"></span>
          <span v-if="isLoading">Procesando...</span>
          <span v-else>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            Pagar {{ total.toFixed(2) }} €
          </span>
        </button>
      </form>

      <div class="powered-by">
        Powered by <strong>Stripe</strong> · Cifrado SSL/TLS
      </div>
    </div>
  </div>
</template>

<style scoped>
.payment-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.25;
  pointer-events: none;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: var(--color-primary);
  top: 10%;
  right: -50px;
}

.orb-2 {
  width: 250px;
  height: 250px;
  background: var(--color-accent);
  bottom: 10%;
  left: -50px;
}

.payment-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 2.5rem;
  width: 100%;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
  animation: fadeInUp 0.5s ease;
  position: relative;
  z-index: 1;
}

.payment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.back-link:hover { color: var(--text-primary); }

.secure-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--color-success);
  font-weight: 600;
  background: rgba(0, 184, 148, 0.1);
  padding: 4px 12px;
  border-radius: var(--radius-full);
}

h1 {
  color: var(--text-primary);
  font-size: 1.6rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
}

/* Order summary */
.order-summary {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: 0.88rem;
  padding: 4px 0;
}

.summary-total-row {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--border-color);
  margin-top: 8px;
  padding-top: 10px;
}

.summary-total-row span:first-child {
  color: var(--text-secondary);
  font-weight: 600;
}

.total-value {
  font-weight: 800;
  font-size: 1.1rem;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Stripe element */
#payment-element {
  margin-bottom: 1.5rem;
}

/* Pay button */
.pay-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--color-primary), #8b7cf7);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.pay-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-primary);
}

.pay-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pay-btn span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.error-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 118, 117, 0.1);
  color: var(--color-danger);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 118, 117, 0.2);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.powered-by {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: 1.5rem;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>