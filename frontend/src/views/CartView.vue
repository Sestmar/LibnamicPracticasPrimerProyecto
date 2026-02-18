<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const cart = ref([])
const router = useRouter()
const token = localStorage.getItem('token')

onMounted(() => {
  cart.value = JSON.parse(localStorage.getItem('shopping_cart') || '[]')
})

const total = computed(() => {
  return cart.value.reduce((acc, item) => acc + (item.price * item.quantity), 0)
})

const totalItems = computed(() => {
  return cart.value.reduce((acc, item) => acc + item.quantity, 0)
})

const updateQuantity = (index, delta) => {
  const item = cart.value[index]
  const newQty = item.quantity + delta
  if (newQty < 1) return
  if (newQty > item.stock) return
  item.quantity = newQty
  localStorage.setItem('shopping_cart', JSON.stringify(cart.value))
}

const removeFromCart = (index) => {
  cart.value.splice(index, 1)
  localStorage.setItem('shopping_cart', JSON.stringify(cart.value))
}

const proceedToPayment = () => {
  if (!token) {
    router.push('/login')
    return
  }
  router.push('/payment')
}
</script>

<template>
  <div class="cart-layout">
    <!-- Header -->
    <header class="cart-header">
      <button @click="router.push('/products')" class="back-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Catálogo
      </button>
      <h1>Tu Cesta</h1>
      <span class="item-count">{{ totalItems }} artículo{{ totalItems !== 1 ? 's' : '' }}</span>
    </header>

    <!-- Empty state -->
    <div v-if="cart.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
      </div>
      <h2>Tu carrito está vacío</h2>
      <p>Explora el catálogo y añade productos</p>
      <button @click="router.push('/products')" class="browse-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Ir al Catálogo
      </button>
    </div>

    <!-- Cart with items -->
    <div v-else class="cart-content">
      <div class="cart-items">
        <TransitionGroup name="list" tag="div">
          <div v-for="(item, index) in cart" :key="item.id" class="item-card">
            <div class="item-image">
              <div class="item-image-pattern"></div>
            </div>
            <div class="item-details">
              <h3>{{ item.name }}</h3>
              <span class="item-price-unit">{{ item.price.toFixed(2) }} € / ud</span>
            </div>
            <div class="item-controls">
              <div class="qty-control">
                <button @click="updateQuantity(index, -1)" :disabled="item.quantity <= 1" class="qty-btn">−</button>
                <span class="qty-value">{{ item.quantity }}</span>
                <button @click="updateQuantity(index, 1)" :disabled="item.quantity >= item.stock" class="qty-btn">+</button>
              </div>
              <span class="item-subtotal">{{ (item.price * item.quantity).toFixed(2) }} €</span>
            </div>
            <button @click="removeFromCart(index)" class="remove-btn" title="Eliminar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </div>
        </TransitionGroup>
      </div>

      <div class="cart-summary">
        <h2>Resumen del Pedido</h2>
        <div class="summary-rows">
          <div class="summary-row">
            <span>Artículos ({{ totalItems }})</span>
            <span>{{ total.toFixed(2) }} €</span>
          </div>
          <div class="summary-row">
            <span>Envío</span>
            <span class="free-shipping">Gratis</span>
          </div>
        </div>
        <div class="summary-total">
          <span>Total</span>
          <span class="total-amount">{{ total.toFixed(2) }} €</span>
        </div>
        <button @click="proceedToPayment" class="checkout-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
          Proceder al Pago
        </button>
        <p class="secure-note">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          Pago 100% seguro con Stripe
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-layout {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Header */
.cart-header {
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

.cart-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
}

.item-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  animation: fadeInUp 0.5s ease;
}

.empty-icon { margin-bottom: 1.5rem; opacity: 0.5; }

.empty-state h2 {
  color: var(--text-primary);
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.browse-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--color-primary), #8b7cf7);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.browse-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-primary);
}

/* Cart content */
.cart-content {
  display: flex;
  gap: 2rem;
  animation: fadeInUp 0.5s ease;
}

.cart-items {
  flex: 2;
}

/* Item card */
.item-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 0.75rem;
  transition: all var(--transition-normal);
}

.item-card:hover {
  border-color: var(--border-color-hover);
  background: var(--bg-surface-hover);
}

.item-image {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.item-image-pattern {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(108, 92, 231, 0.2), rgba(0, 206, 201, 0.15));
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-details h3 {
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 2px;
}

.item-price-unit {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.item-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.qty-control {
  display: flex;
  align-items: center;
  gap: 0;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.qty-btn {
  width: 32px;
  height: 32px;
  background: var(--bg-surface);
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.qty-btn:hover:not(:disabled) {
  background: var(--bg-surface-hover);
}

.qty-btn:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
}

.qty-value {
  width: 36px;
  text-align: center;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-primary);
  background: var(--bg-surface);
  height: 32px;
  line-height: 32px;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.item-subtotal {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-primary-light);
}

.remove-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.remove-btn:hover {
  color: var(--color-danger);
  background: rgba(255, 118, 117, 0.1);
}

/* Summary */
.cart-summary {
  flex: 1;
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 2rem;
}

.cart-summary h2 {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.summary-rows {
  margin-bottom: 1rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.free-shipping {
  color: var(--color-success);
  font-weight: 600;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  padding: 1rem 0;
  border-top: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
}

.summary-total span:first-child {
  color: var(--text-secondary);
  font-weight: 600;
}

.total-amount {
  font-size: 1.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.checkout-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--color-primary), #8b7cf7);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.checkout-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-primary);
}

.secure-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.78rem;
}

/* Transitions */
.list-enter-active { animation: fadeInUp 0.3s ease; }
.list-leave-active { animation: fadeInUp 0.3s ease reverse; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .cart-content { flex-direction: column; }
  .cart-summary { position: static; }
}
</style>