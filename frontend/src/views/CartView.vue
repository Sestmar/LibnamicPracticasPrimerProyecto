<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const cart = ref([])
const router = useRouter()
const token = localStorage.getItem('token')

// Cargar carrito al entrar
onMounted(() => {
  cart.value = JSON.parse(localStorage.getItem('shopping_cart') || '[]')
})

// Calcular total dinámicamente
const total = computed(() => {
  return cart.value.reduce((acc, item) => acc + (item.price * item.quantity), 0)
})

// Eliminar un item
const removeFromCart = (index) => {
  cart.value.splice(index, 1)
  localStorage.setItem('shopping_cart', JSON.stringify(cart.value))
}

// --- CAMBIO CLAVE: PROCESAR PAGO ---
// Ya no llamamos al backend aquí. Redirigimos a la vista de pago.
const proceedToPayment = () => {
  if (!token) {
    // Si no está logueado, al login
    router.push('/login')
    return
  }
  
  // Si hay token, nos vamos a la pasarela de pago (PaymentView.vue)
  // Allí es donde se hará la conexión con Stripe
  router.push('/payment')
}
</script>

<template>
  <div class="container">
    <h1>🛒 Tu Cesta</h1>
    
    <div v-if="cart.length === 0" class="empty-cart">
      <p>Tu carrito está vacío.</p>
      <button @click="router.push('/products')">Volver al Catálogo</button>
    </div>

    <div v-else class="cart-content">
      <div class="cart-items">
        <div v-for="(item, index) in cart" :key="item.id" class="item-row">
          <div class="info">
            <h3>{{ item.name }}</h3>
            <p>Precio: {{ item.price }} €</p>
          </div>
          <div class="controls">
            <span>Cant: {{ item.quantity }}</span>
            <button @click="removeFromCart(index)" class="delete-btn">🗑️</button>
          </div>
        </div>
      </div>

      <div class="cart-summary">
        <h2>Resumen</h2>
        <div class="total">
          <span>Total a pagar:</span>
          <strong>{{ total.toFixed(2) }} €</strong>
        </div>
        <button @click="proceedToPayment" class="checkout-btn">💳 Proceder al Pago</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container { max-width: 800px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif; }
.empty-cart { text-align: center; margin-top: 50px; }
.cart-content { display: flex; gap: 20px; flex-wrap: wrap; }
.cart-items { flex: 2; min-width: 300px; }
.item-row { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #eee; }
.cart-summary { flex: 1; background: #f8f9fa; padding: 20px; border-radius: 8px; height: fit-content; }
.total { display: flex; justify-content: space-between; font-size: 1.2rem; margin-bottom: 20px; border-top: 1px solid #ddd; padding-top: 10px; }
.checkout-btn { width: 100%; background: #42b883; color: white; padding: 10px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
.checkout-btn:hover { background: #3aa876; }
.delete-btn { background: transparent; border: none; cursor: pointer; font-size: 1.2rem; }
</style>