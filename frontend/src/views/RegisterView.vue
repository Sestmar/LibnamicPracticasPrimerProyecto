<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const form = ref({ first_name: '', last_name: '', email: '', phone: '', password: '' })
const router = useRouter()

const register = async () => {
  try {
    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    if (response.ok) {
      alert('✅ Registro exitoso. Ahora inicia sesión.')
      router.push('/login')
    } else {
      alert('Error al registrar')
    }
  } catch (e) { console.error(e) }
}
</script>

<template>
  <div class="auth-container">
    <div class="card">
      <h2>📝 Crear Cuenta</h2>
      <form @submit.prevent="register">
        <div class="row">
            <input v-model="form.first_name" placeholder="Nombre" required />
            <input v-model="form.last_name" placeholder="Apellidos" required />
        </div>
        <input v-model="form.email" type="email" placeholder="Correo Electrónico" required />
        <input v-model="form.phone" type="tel" placeholder="Teléfono Móvil" required />
        <input v-model="form.password" type="password" placeholder="Contraseña" required />
        <button type="submit">Registrarse</button>
      </form>
      <p>¿Ya tienes cuenta? <a @click="$router.push('/login')">Entrar</a></p>
    </div>
  </div>
</template>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f6f9; }
.card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
.row { display: flex; gap: 10px; }
input { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 6px; }
button { width: 100%; padding: 10px; background: #3498db; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
a { color: #3498db; cursor: pointer; text-decoration: underline; }
</style>