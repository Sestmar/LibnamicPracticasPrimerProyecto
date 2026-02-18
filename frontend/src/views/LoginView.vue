<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const router = useRouter()
const error = ref('')
const isLoading = ref(false)

const login = async () => {
  error.value = ''
  isLoading.value = true
  
  const formData = new URLSearchParams()
  formData.append('username', email.value) 
  formData.append('password', password.value)

  try {
    const response = await fetch('http://localhost:8000/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })

    if (!response.ok) throw new Error('Credenciales incorrectas')

    const data = await response.json()
    
    // Guardo el token Y el rol y el nombre completo
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('full_name', data.full_name)
    // -------------------------

    router.push('/products')
    
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="brand-header">
        <span class="logo"></span>
        <h1>LibnamicShop</h1>
        <p>Gestión de Inventario</p>
      </div>

      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label>Correo Electrónico</label>
          <input 
            v-model="email" 
            type="text" 
            placeholder="example@example.com" 
            required 
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••" 
            required 
            :disabled="isLoading"
          />
        </div>

        <div v-if="error" class="error-message">
           {{ error }}
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading">Entrando...</span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>
    </div>
    
    <footer class="login-footer">
      &copy; 2026 Libnamic Backend Training
    </footer>
  </div>
</template>

<style scoped>
/* Contenedor de pantalla completa */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

/* Tarjeta Central */
.login-card {
  background: white;
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  transition: transform 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.1);
}

/* Cabecera con Logo */
.brand-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
}

.brand-header h1 {
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.brand-header p {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: 5px;
}

/* Formulario */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #34495e;
  font-weight: 600;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
  outline: none;
}

.form-group input:focus {
  border-color: #42b883;
}

/* Botón */
.submit-btn {
  width: 100%;
  padding: 1rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #3aa876;
}

.submit-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

/* Mensajes */
.error-message {
  background-color: #fee2e2;
  color: #c0392b;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
}

.login-footer {
  margin-top: 2rem;
  color: #7f8c8d;
  font-size: 0.8rem;
}
</style>