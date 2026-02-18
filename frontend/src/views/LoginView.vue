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
    
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('full_name', data.full_name)
    localStorage.setItem('email', data.email)

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
    <!-- Background animated orbs -->
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>

    <div class="login-card">
      <div class="brand-header">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none">
            <rect width="40" height="40" rx="12" fill="url(#grad)"/>
            <path d="M12 20L18 26L28 14" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <defs><linearGradient id="grad" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6c5ce7"/><stop offset="1" stop-color="#00cec9"/></linearGradient></defs>
          </svg>
        </div>
        <h1>LibnamicShop</h1>
        <p class="subtitle">Plataforma de Gestión Empresarial</p>
      </div>

      <form @submit.prevent="login" class="login-form">
        <div class="input-group">
          <div class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          </div>
          <input 
            v-model="email" 
            type="text" 
            placeholder="Correo electrónico"
            required 
            :disabled="isLoading"
            autocomplete="email"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          </div>
          <input 
            v-model="password" 
            type="password" 
            placeholder="Contraseña"
            required 
            :disabled="isLoading"
            autocomplete="current-password"
          />
        </div>

        <div v-if="error" class="error-message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ error }}
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span v-if="isLoading">Entrando...</span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>

      <div class="register-link">
        <span>¿No tienes cuenta?</span>
        <a @click="router.push('/register')">Crear cuenta</a>
      </div>
    </div>
    
    <footer class="login-footer">
      © 2026 LibnamicShop · Enterprise Platform
    </footer>
  </div>
</template>

<style scoped>
.login-wrapper {
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

/* Animated background orbs */
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  pointer-events: none;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: var(--color-primary);
  top: -100px;
  right: -100px;
  animation: floatOrb 8s ease-in-out infinite;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: var(--color-accent);
  bottom: -50px;
  left: -80px;
  animation: floatOrb 10s ease-in-out infinite reverse;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: var(--color-primary-light);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: floatOrb 12s ease-in-out infinite;
}

@keyframes floatOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

/* Login Card */
.login-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  width: 100%;
  max-width: 420px;
  padding: 3rem;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  animation: fadeInUp 0.6s ease forwards;
  position: relative;
  z-index: 1;
}

/* Brand Header */
.brand-header {
  text-align: center;
  margin-bottom: 2.5rem;
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
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.brand-header .subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-top: 4px;
  font-weight: 400;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
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
  padding: 14px 16px 14px 48px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: all var(--transition-normal);
}

.input-group input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
  background: var(--bg-surface-hover);
}

.input-group input:focus + .input-icon,
.input-group:focus-within .input-icon {
  color: var(--color-primary-light);
}

.input-group input::placeholder {
  color: var(--text-muted);
}

.input-group input:disabled {
  opacity: 0.5;
}

/* Submit Button */
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

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Spinner */
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
  animation: fadeInUp 0.3s ease;
}

/* Register link */
.register-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.register-link a {
  color: var(--color-primary-light);
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
  transition: color var(--transition-fast);
}

.register-link a:hover {
  color: var(--color-accent);
}

/* Footer */
.login-footer {
  margin-top: 2rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  position: relative;
  z-index: 1;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>