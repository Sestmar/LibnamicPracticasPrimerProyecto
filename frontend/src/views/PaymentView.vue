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

onMounted(async () => {
  // 1. Recuperar el carrito
  cart.value = JSON.parse(localStorage.getItem('shopping_cart') || '[]')
  
  if (cart.value.length === 0) {
    router.push('/cart')
    return
  }

  // 2. Pedir al Backend la intención de pago (El "permiso" para cobrar)
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

    // 3. Cargar el formulario de Stripe (Elements)
    stripe.value = await stripePromise
    elements.value = stripe.value.elements({ clientSecret: clientSecret.value })
    
    const paymentElement = elements.value.create('payment')
    paymentElement.mount('#payment-element') // Inyectamos el formulario en el DIV
    
  } catch (e) {
    message.value = "Error iniciando el pago: " + e.message
  }
})

const handleSubmit = async () => {
  if (!stripe.value || !elements.value) return // Aún no ha cargado
  
  isLoading.value = true
  
  // 4. Confirmar el pago con Stripe
  const { error } = await stripe.value.confirmPayment({
    elements: elements.value,
    confirmParams: {
      // Truco: No redirigimos, manejamos el éxito aquí mismo si no hay error
      return_url: window.location.origin + '/payment-success',
    },
    redirect: 'if_required' 
  })

  if (error) {
    message.value = error.message
    isLoading.value = false
  } else {
    // 5. ¡ÉXITO! El dinero está en el banco. Ahora creamos el pedido en nuestra DB.
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
      // Limpiamos carrito y celebramos
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
  <div class="payment-container">
    <div class="card">
      <h2>💳 Finalizar Pago Seguro</h2>
      <p class="amount-info">Vas a pagar los productos de tu cesta.</p>
      
      <form @submit.prevent="handleSubmit">
        <div id="payment-element">
            </div>
        
        <div v-if="message" class="error-msg">{{ message }}</div>
        
        <button :disabled="isLoading || !stripe || !elements" id="submit">
          <span v-if="isLoading">Procesando...</span>
          <span v-else>Pagar Ahora</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.payment-container { display: flex; justify-content: center; padding-top: 50px; min-height: 80vh; background: #f8f9fa; }
.card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 500px; }
h2 { text-align: center; color: #2c3e50; margin-bottom: 20px; }
.amount-info { text-align: center; margin-bottom: 30px; color: #7f8c8d; }
#payment-element { margin-bottom: 24px; }
button { background: #5469d4; color: #ffffff; border-radius: 4px; border: 0; padding: 12px 16px; font-size: 16px; font-weight: 600; cursor: pointer; display: block; width: 100%; transition: all 0.2s ease; }
button:hover { filter: contrast(115%); }
button:disabled { opacity: 0.5; cursor: default; }
.error-msg { color: #df1b41; margin-top: 10px; text-align: center; }
</style>