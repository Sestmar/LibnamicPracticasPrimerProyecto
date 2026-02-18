<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const token = localStorage.getItem('token')
const userRole = localStorage.getItem('role')
const userName = localStorage.getItem('full_name') || 'Usuario'

// CAMBIO: Variables de entorno
const apiUrl = import.meta.env.VITE_API_URL
const wsUrl = import.meta.env.VITE_WS_URL

if (!token) router.push('/login')

// --- ESTADO ---
const messages = ref([])
const newMessage = ref('')
const chatContainer = ref(null)
const connected = ref(false)
let ws = null

// Para el admin: lista de salas activas
const activeRooms = ref([])
const selectedRoom = ref(null)

// Extraer email del token JWT (payload.sub) como fallback
const getEmailFromToken = () => {
  try {
    const parts = token.split('.')
    let base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    while (base64.length % 4) base64 += '='
    const payload = JSON.parse(atob(base64))
    return payload.sub || 'default'
  } catch (e) { 
    console.error('Error decodificando JWT:', e)
    return 'default' 
  }
}

const userEmail = localStorage.getItem('email') || getEmailFromToken()
const currentRoomId = ref(userRole === 'admin' ? null : userEmail)

// --- CONEXIÓN WEBSOCKET ---
const connectToRoom = (roomId) => {
  if (ws) {
    ws.close()
    messages.value = []
  }
  
  currentRoomId.value = roomId
  selectedRoom.value = roomId
  
  // CAMBIO: Usar variable wsUrl con comillas invertidas
  ws = new WebSocket(`${wsUrl}/ws/chat/${roomId}?token=${token}`)
  
  ws.onopen = () => {
    connected.value = true
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'history') {
      messages.value = data.messages
    } else {
      messages.value.push(data)
    }
    
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
  }
  
  ws.onclose = () => {
    connected.value = false
  }
  
  ws.onerror = () => {
    connected.value = false
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !ws || ws.readyState !== WebSocket.OPEN) return
  ws.send(newMessage.value.trim())
  newMessage.value = ''
}

// Admin: cargar salas activas
const fetchActiveRooms = async () => {
  try {
    // CAMBIO: Usar apiUrl
    const response = await fetch(`${apiUrl}/admin/chat-rooms`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    activeRooms.value = await response.json()
  } catch (e) {
    console.error('Error cargando salas:', e)
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  if (userRole === 'admin') {
    fetchActiveRooms()
    const interval = setInterval(fetchActiveRooms, 5000)
    onUnmounted(() => clearInterval(interval))
  } else {
    connectToRoom(userEmail)
  }
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>

<template>
  <div class="chat-layout">
    <!-- SIDEBAR (Solo Admin) -->
    <aside v-if="userRole === 'admin'" class="sidebar">
      <div class="sidebar-header">
        <h2>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          Conversaciones
        </h2>
        <button @click="router.push('/admin')" class="back-mini">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
          Panel
        </button>
      </div>
      
      <div v-if="activeRooms.length === 0" class="no-rooms">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <p>Sin conversaciones activas</p>
        <span class="hint">Los clientes iniciarán el chat desde su cuenta</span>
      </div>
      
      <div 
        v-for="room in activeRooms" 
        :key="room.room_id"
        @click="connectToRoom(room.room_id)"
        :class="['room-item', { active: selectedRoom === room.room_id }]"
      >
        <div class="room-avatar">{{ room.client_email.charAt(0).toUpperCase() }}</div>
        <div class="room-info">
          <span class="room-email">{{ room.client_email }}</span>
          <span class="room-meta">{{ room.message_count }} msgs · {{ room.active_connections }} online</span>
        </div>
      </div>
    </aside>

    <!-- ÁREA DE CHAT -->
    <main class="chat-area">
      <header class="chat-header">
        <div class="header-left">
          <button v-if="userRole !== 'admin'" @click="router.push('/products')" class="back-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
          </button>
          <h3>
            {{ userRole === 'admin' 
              ? (selectedRoom ? `Chat con ${selectedRoom}` : 'Selecciona una conversación') 
              : 'Chat con Soporte' }}
          </h3>
        </div>
        <span :class="['status-dot', connected ? 'online' : 'offline']">
          {{ connected ? 'Conectado' : 'Desconectado' }}
        </span>
      </header>

      <!-- Mensajes -->
      <div class="messages-container" ref="chatContainer">
        <div v-if="!currentRoomId && userRole === 'admin'" class="empty-state">
          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <p>Selecciona una conversación de la barra lateral</p>
        </div>

        <div 
          v-for="(msg, i) in messages" 
          :key="i"
          :class="['message-bubble', msg.type === 'system' ? 'system' : (msg.sender_role === 'admin' ? 'admin' : 'client')]"
        >
          <template v-if="msg.type === 'system'">
            <span class="system-text">{{ msg.content }}</span>
          </template>
          <template v-else>
            <div class="bubble-header">
              <span class="sender-name">{{ msg.sender }}</span>
              <span v-if="msg.sender_role === 'admin'" class="admin-tag">ADMIN</span>
            </div>
            <p class="bubble-content">{{ msg.content }}</p>
            <span class="bubble-time">{{ formatTime(msg.timestamp) }}</span>
          </template>
        </div>
      </div>

      <!-- Input -->
      <div class="input-area" v-if="currentRoomId">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage"
          placeholder="Escribe un mensaje..."
          :disabled="!connected"
          class="chat-input"
        />
        <button @click="sendMessage" :disabled="!connected || !newMessage.trim()" class="send-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* LAYOUT */
.chat-layout {
  display: flex;
  height: 100vh;
  font-family: 'Inter', sans-serif;
  background: var(--bg-primary);
}

/* SIDEBAR */
.sidebar {
  width: 320px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
}

.back-mini {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: 1px solid var(--border-color);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  transition: all var(--transition-fast);
}

.back-mini:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
}

.no-rooms {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.no-rooms p { margin: 0; font-size: 0.9rem; }

.hint {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.room-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background var(--transition-fast);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.room-item:hover {
  background: var(--bg-surface-hover);
}

.room-item.active {
  background: rgba(108, 92, 231, 0.1);
  border-left: 3px solid var(--color-primary);
}

.room-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.room-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.room-email {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.room-meta {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* CHAT AREA */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: rgba(10, 10, 20, 0.6);
  backdrop-filter: blur(12px);
  padding: 14px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-header h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 600;
}

.back-btn {
  background: none;
  border: 1px solid var(--border-color);
  padding: 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.back-btn:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
}

.status-dot {
  font-size: 0.78rem;
  font-weight: 600;
}

.status-dot.online {
  color: var(--color-success);
}

.status-dot.online::before { content: '● '; }

.status-dot.offline {
  color: var(--color-danger);
}

.status-dot.offline::before { content: '● '; }

/* MESSAGES */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  gap: 12px;
}

.empty-state p { font-size: 0.9rem; }

/* BUBBLES */
.message-bubble {
  max-width: 70%;
  padding: 10px 16px;
  border-radius: 16px;
  position: relative;
  animation: fadeIn 0.2s ease;
}

.message-bubble.client {
  align-self: flex-start;
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 4px;
}

.message-bubble.admin {
  align-self: flex-end;
  background: linear-gradient(135deg, var(--color-primary), #8b7cf7);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-bubble.system {
  align-self: center;
  background: none;
  padding: 4px 12px;
}

.system-text {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-style: italic;
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.sender-name {
  font-weight: 600;
  font-size: 0.78rem;
}

.client .sender-name { color: var(--color-primary-light); }

.admin-tag {
  background: rgba(255,255,255,0.25);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.bubble-content {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.45;
  word-wrap: break-word;
}

.client .bubble-content { color: var(--text-primary); }

.bubble-time {
  font-size: 0.68rem;
  opacity: 0.6;
  display: block;
  text-align: right;
  margin-top: 4px;
}

/* INPUT */
.input-area {
  background: var(--bg-secondary);
  padding: 14px 24px;
  border-top: 1px solid var(--border-color);L
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
  padding: 12px 18px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  color: var(--text-primary);
  font-size: 0.92rem;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: all var(--transition-normal);
}

.chat-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-glow);
}

.chat-input::placeholder { color: var(--text-muted); }

.chat-input:disabled { opacity: 0.5; }

.send-btn {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--color-primary), #8b7cf7);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-normal);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: var(--shadow-glow-primary);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
