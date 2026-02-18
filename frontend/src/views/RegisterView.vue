<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const form = ref({ first_name: '', last_name: '', email: '', phone: '', password: '' })
const router = useRouter()
const isLoading = ref(false)
const error = ref('')
const success = ref(false)

const register = async () => {
  error.value = ''
  isLoading.value = true
  try {
    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    if (response.ok) {
      success.value = true
      setTimeout(() => router.push('/login'), 2000)
    } else {
      const data = await response.json()
      error.value = data.detail || 'Error al registrar'
    }
  } catch (e) {
    error.value = 'Error de conexión'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="register-wrapper">
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <div class="register-card">
      <div class="brand-header">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none">
            <rect width="40" height="40" rx="12" fill="url(#grad2)"/>
            <path d="M20 12v8m0 0v8m0-8h8m-8 0h-8" stroke="white" stroke-width="3" stroke-linecap="round"/>
            <defs><linearGradient id="grad2" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6c5ce7"/><stop offset="1" stop-color="#00cec9"/></linearGradient></defs>
          </svg>
        </div>
        <h1>Crear Cuenta</h1>
        <p class="subtitle">Únete a LibnamicShop</p>
      </div>

      <!-- Success state -->
      <div v-if="success" class="success-message">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <h3>¡Cuenta creada!</h3>
        <p>Redirigiendo al login...</p>
      </div>

      <!-- Register form -->
      <form v-else @submit.prevent="register" class="register-form">
        <div class="form-row">
          <div class="input-group">
            <div class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <input v-model="form.first_name" placeholder="Nombre" required :disabled="isLoading" />
          </div>
          <div class="input-group">
            <div class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <input v-model="form.last_name" placeholder="Apellidos" required :disabled="isLoading" />
          </div>
        </div>

        <div class="input-group">
          <div class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          </div>
          <input v-model="form.email" type="email" placeholder="Correo electrónico" required :disabled="isLoading" />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          </div>
          <input v-model="form.phone" type="tel" placeholder="Teléfono móvil" required :disabled="isLoading" />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          </div>
          <input v-model="form.password" type="password" placeholder="Contraseña" required :disabled="isLoading" />
        </div>

        <div v-if="error" class="error-message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ error }}
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-if="isLoading">Creando cuenta...</span>
          <span v-else>Registrarse</span>
        </button>
      </form>

      <div v-if="!success" class="login-link">
        <span>¿Ya tienes cuenta?</span>
        <a @click="router.push('/login')">Iniciar sesión</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
  overflow: hidden;
  position: relative;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  pointer-events: none;
}

.orb-1 {
  width: 350px;
  height: 350px;
  background: var(--color-accent);
  top: -80px;
  left: -80px;
  animation: floatOrb 10s ease-in-out infinite;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: var(--color-primary);
  bottom: -60px;
  right: -60px;
  animation: floatOrb 8s ease-in-out infinite reverse;
}

@keyframes floatOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

.register-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  width: 100%;
  max-width: 460px;
  padding: 3rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  animation: fadeInUp 0.6s ease forwards;
  position: relative;
  z-index: 1;
}

.brand-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.brand-header h1 {
  color: var(--text-primary);
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.brand-header .subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-top: 4px;
}

/* Form */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.form-row {
  display: flex;
  gap: 0.85rem;
}

.form-row .input-group {
  flex: 1;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  pointer-events: none;
  transition: color var(--transition-normal);
}

.input-group input {
  width: 100%;
  padding: 13px 14px 13px 44px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: all var(--transition-normal);
}

.input-group input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
  background: var(--bg-surface-hover);
}

.input-group:focus-within .input-icon {
  color: var(--color-primary-light);
}

.input-group input::placeholder {
  color: var(--text-muted);
}

.input-group input:disabled {
  opacity: 0.5;
}

/* Submit */
.submit-btn {
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
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-primary);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 118, 117, 0.1);
  color: var(--color-danger);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 118, 117, 0.2);
  font-size: 0.9rem;
}

/* Success */
.success-message {
  text-align: center;
  padding: 2rem 0;
  animation: fadeInUp 0.5s ease;
}

.success-message h3 {
  color: var(--color-success);
  font-size: 1.3rem;
  margin-top: 1rem;
}

.success-message p {
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

/* Login link */
.login-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.login-link a {
  color: var(--color-primary-light);
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
}

.login-link a:hover {
  color: var(--color-accent);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>