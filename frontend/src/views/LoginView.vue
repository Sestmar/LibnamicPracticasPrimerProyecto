<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const router = useRouter()
const error = ref('')
const isLoading = ref(false)

// 1. AÑADIMOS LA VARIABLE DE ENTORNO
const apiUrl = import.meta.env.VITE_API_URL

const login = async () => {
  error.value = ''
  isLoading.value = true
  
  const formData = new URLSearchParams()
  formData.append('username', email.value) 
  formData.append('password', password.value)

  try {
    // 2. Apuntamos a la variable de render
    const response = await fetch(`${apiUrl}/token`, {
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
  <div class="login-split">
    <!-- ===== LEFT PANEL — Branding ===== -->
    <div class="brand-panel">
      <div class="brand-bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>

      <div class="brand-content">
        <div class="brand-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        </div>

        <h1>Gestiona tu negocio sin límites.</h1>
        <p class="brand-desc">
          Optimiza tus recursos, controla tu inventario y escala tus ventas con la plataforma empresarial más robusta del mercado.
        </p>

        <div class="social-proof">
          <div class="avatars">
            <span class="avatar" style="background: linear-gradient(135deg, #6c5ce7, #a29bfe);">S</span>
            <span class="avatar" style="background: linear-gradient(135deg, #00cec9, #81ecec);">M</span>
            <span class="avatar" style="background: linear-gradient(135deg, #fdcb6e, #f39c12);">A</span>
          </div>
          <span class="proof-text">⭐ Confían más de 10,000 empresas</span>
        </div>
      </div>
    </div>

    <!-- ===== RIGHT PANEL — Login Form ===== -->
    <div class="form-panel">
      <div class="form-wrapper">
        <!-- Logo -->
        <div class="form-header">
          <div class="logo-icon">
            <svg viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="12" fill="url(#grad)"/>
              <path d="M12 20L18 26L28 14" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              <defs><linearGradient id="grad" x1="0" y1="0" x2="40" y2="40"><stop stop-color="#6c5ce7"/><stop offset="1" stop-color="#00cec9"/></linearGradient></defs>
            </svg>
          </div>
          <h2>LibnamicShop</h2>
          <p class="subtitle">Plataforma de Gestión Empresarial</p>
        </div>

        <form @submit.prevent="login" class="login-form">
          <!-- Email -->
          <div class="field">
            <label for="email">Correo Electrónico</label>
            <div class="input-wrap">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <input 
                id="email"
                v-model="email" 
                type="text" 
                placeholder="sergio@test.com"
                required 
                :disabled="isLoading"
                autocomplete="email"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="field">
            <label for="password">Contraseña</label>
            <div class="input-wrap">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <input 
                id="password"
                v-model="password" 
                type="password" 
                placeholder="••••••••••"
                required 
                :disabled="isLoading"
                autocomplete="current-password"
              />
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="error-message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            {{ error }}
          </div>

          <!-- Submit -->
          <button type="submit" class="submit-btn" :disabled="isLoading">
            <svg v-if="!isLoading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Entrando...' : 'Entrar' }}
          </button>
        </form>

        <div class="register-link">
          ¿No tienes cuenta? <a @click="router.push('/register')">Crear cuenta</a>
        </div>

        <footer class="form-footer">
          © 2026 LibnamicShop · Enterprise Platform
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== SPLIT LAYOUT ===== */
.login-split {
  display: flex;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

/* ===== LEFT — BRAND PANEL ===== */
.brand-panel {
  flex: 1;
  background: linear-gradient(160deg, #1a1040 0%, #2d1b69 40%, #6c5ce7 100%);
  display: flex;
  align-items: flex-end;
  justify-content: flex-start;
  padding: 4rem;
  position: relative;
  overflow: hidden;
}

/* Decorative 3D-like shapes */
.brand-bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  border-radius: 999px;
}

.shape-1 {
  width: 220px;
  height: 400px;
  background: linear-gradient(180deg, rgba(108, 92, 231, 0.6) 0%, rgba(45, 27, 105, 0.9) 100%);
  top: 10%;
  right: 15%;
  border-radius: 110px;
  transform: rotate(-10deg);
  box-shadow: 
    -20px 0 40px rgba(108, 92, 231, 0.3),
    inset 20px 0 40px rgba(162, 155, 254, 0.2);
}

.shape-2 {
  width: 180px;
  height: 350px;
  background: linear-gradient(180deg, rgba(162, 155, 254, 0.5) 0%, rgba(45, 27, 105, 0.8) 100%);
  top: 15%;
  right: 30%;
  border-radius: 90px;
  transform: rotate(-5deg);
  box-shadow: 
    -15px 0 30px rgba(108, 92, 231, 0.2),
    inset 15px 0 30px rgba(162, 155, 254, 0.15);
}

.shape-3 {
  width: 140px;
  height: 280px;
  background: linear-gradient(180deg, rgba(0, 206, 201, 0.3) 0%, rgba(45, 27, 105, 0.7) 100%);
  top: 20%;
  right: 5%;
  border-radius: 70px;
  transform: rotate(-15deg);
  box-shadow: 
    -10px 0 25px rgba(0, 206, 201, 0.2),
    inset 10px 0 20px rgba(0, 206, 201, 0.1);
}

/* Animate shapes subtly */
.shape-1 { animation: floatShape 8s ease-in-out infinite; }
.shape-2 { animation: floatShape 10s ease-in-out infinite 1s; }
.shape-3 { animation: floatShape 12s ease-in-out infinite 2s; }

@keyframes floatShape {
  0%, 100% { transform: rotate(-10deg) translateY(0); }
  50%      { transform: rotate(-10deg) translateY(-15px); }
}

/* Brand content */
.brand-content {
  position: relative;
  z-index: 2;
  max-width: 450px;
  animation: fadeInUp 0.7s ease;
}

.brand-icon {
  width: 52px;
  height: 52px;
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(8px);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  border: 1px solid rgba(255,255,255,0.1);
}

.brand-content h1 {
  font-size: 2.4rem;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  letter-spacing: -0.03em;
  margin-bottom: 1rem;
}

.brand-desc {
  font-size: 1.05rem;
  color: rgba(255,255,255,0.65);
  line-height: 1.7;
  margin-bottom: 2.5rem;
}

/* Social proof */
.social-proof {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatars {
  display: flex;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.8rem;
  border: 2px solid rgba(26, 16, 64, 0.8);
  margin-right: -10px;
}

.proof-text {
  color: rgba(255,255,255,0.7);
  font-size: 0.88rem;
  font-weight: 500;
  margin-left: 6px;
}

/* ===== RIGHT — FORM PANEL ===== */
.form-panel {
  flex: 1;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
  animation: fadeInUp 0.6s ease 0.15s backwards;
}

/* Header */
.form-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 1rem;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.form-header h2 {
  color: var(--text-primary);
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.form-header .subtitle {
  color: var(--text-secondary);
  font-size: 0.88rem;
  margin-top: 4px;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.input-wrap {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
  transition: color var(--transition-normal);
}

.input-wrap input {
  width: 100%;
  padding: 13px 14px 13px 46px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: all var(--transition-normal);
}

.input-wrap input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
  background: var(--bg-surface-hover);
}

.input-wrap:focus-within .input-icon {
  color: var(--color-primary-light);
}

.input-wrap input::placeholder {
  color: var(--text-muted);
}

.input-wrap input:disabled {
  opacity: 0.5;
}

/* Submit */
.submit-btn {
  width: 100%;
  padding: 13px;
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
  font-size: 0.88rem;
  animation: fadeInUp 0.3s ease;
}

/* Register link */
.register-link {
  text-align: center;
  margin-top: 1.75rem;
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.register-link a {
  color: var(--color-primary-light);
  font-weight: 600;
  cursor: pointer;
  margin-left: 2px;
  transition: color var(--transition-fast);
}

.register-link a:hover {
  color: var(--color-accent);
}

/* Footer */
.form-footer {
  text-align: center;
  margin-top: 3rem;
  color: var(--text-muted);
  font-size: 0.78rem;
}

/* ===== ANIMATIONS ===== */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 900px) {
  .login-split {
    flex-direction: column;
  }
  
  .brand-panel {
    min-height: 300px;
    padding: 2rem;
    align-items: center;
    justify-content: center;
  }
  
  .brand-content h1 {
    font-size: 1.8rem;
  }
  
  .shape-1, .shape-2, .shape-3 {
    transform: scale(0.6);
  }
}
</style>