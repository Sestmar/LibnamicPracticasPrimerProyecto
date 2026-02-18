<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const token = localStorage.getItem('token')
const userRole = localStorage.getItem('role')
const userName = localStorage.getItem('full_name') || 'Usuario'

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
    // JWT usa base64url, hay que convertir a base64 estándar para atob()
    let base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    // Añadir padding si falta
    while (base64.length % 4) base64 += '='
    const payload = JSON.parse(atob(base64))
    return payload.sub || 'default'
  } catch (e) { 
    console.error('Error decodificando JWT:', e)
    return 'default' 
  }
}

// El ID de sala del cliente es su email (cada cliente tiene su sala propia)
const userEmail = localStorage.getItem('email') || getEmailFromToken()
const currentRoomId = ref(userRole === 'admin' ? null : userEmail)

// --- CONEXIÓN WEBSOCKET ---
const connectToRoom = (roomId) => {
  // Si ya hay una conexión, la cerramos
  if (ws) {
    ws.close()
    messages.value = []
  }
  
  currentRoomId.value = roomId
  selectedRoom.value = roomId
  
  ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}?token=${token}`)
  
  ws.onopen = () => {
    connected.value = true
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'history') {
      // Recibimos el historial de mensajes
      messages.value = data.messages
    } else {
      messages.value.push(data)
    }
    
    // Scroll automático al último mensaje
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
    const response = await fetch('http://localhost:8000/admin/chat-rooms', {
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
    // Refresca la lista de salas cada 5 segundos
    const interval = setInterval(fetchActiveRooms, 5000)
    onUnmounted(() => clearInterval(interval))
  } else {
    // Los clientes se conectan directamente a su sala
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
        <h2>💬 Conversaciones</h2>
        <button @click="router.push('/admin')" class="back-mini">← Panel</button>
      </div>
      
      <div v-if="activeRooms.length === 0" class="no-rooms">
        <p>No hay conversaciones activas</p>
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
          <span class="room-meta">{{ room.message_count }} mensajes · {{ room.active_connections }} online</span>
        </div>
      </div>
    </aside>

    <!-- ÁREA DE CHAT -->
    <main class="chat-area">
      <header class="chat-header">
        <div class="header-left">
          <button v-if="userRole !== 'admin'" @click="router.push('/products')" class="back-btn">←</button>
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
          <span class="empty-icon">💬</span>
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
              <span v-if="msg.sender_role === 'admin'" class="admin-badge">ADMIN</span>
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
          Enviar
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* LAYOUT */
.chat-layout { display: flex; height: 100vh; font-family: 'Segoe UI', sans-serif; background: #f0f2f5; }

/* SIDEBAR */
.sidebar { width: 320px; background: white; border-right: 1px solid #e5e7eb; display: flex; flex-direction: column; }
.sidebar-header { padding: 16px 20px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
.sidebar-header h2 { margin: 0; font-size: 1.2rem; }
.back-mini { background: none; border: 1px solid #e5e7eb; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; color: #666; }
.no-rooms { padding: 40px 20px; text-align: center; color: #a0aec0; }
.hint { font-size: 0.8rem; display: block; margin-top: 8px; }
.room-item { display: flex; align-items: center; gap: 12px; padding: 14px 20px; cursor: pointer; transition: background 0.15s; border-bottom: 1px solid #f5f5f5; }
.room-item:hover { background: #f7fafc; }
.room-item.active { background: #edf2f7; border-left: 3px solid #3498db; }
.room-avatar { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #3498db, #2ecc71); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; flex-shrink: 0; }
.room-info { display: flex; flex-direction: column; overflow: hidden; }
.room-email { font-weight: 600; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.room-meta { font-size: 0.75rem; color: #a0aec0; }

/* CHAT AREA */
.chat-area { flex: 1; display: flex; flex-direction: column; }
.chat-header { background: white; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 12px; }
.chat-header h3 { margin: 0; font-size: 1.1rem; color: #2c3e50; }
.back-btn { background: none; border: 1px solid #e5e7eb; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 1rem; }
.status-dot { font-size: 0.8rem; font-weight: 600; }
.status-dot.online { color: #27ae60; }
.status-dot.online::before { content: '● '; }
.status-dot.offline { color: #e74c3c; }
.status-dot.offline::before { content: '● '; }

/* MESSAGES */
.messages-container { flex: 1; overflow-y: auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 10px; }
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #a0aec0; }
.empty-icon { font-size: 4rem; margin-bottom: 12px; }

/* BUBBLES */
.message-bubble { max-width: 70%; padding: 10px 16px; border-radius: 16px; position: relative; }
.message-bubble.client { align-self: flex-start; background: white; border: 1px solid #e5e7eb; border-bottom-left-radius: 4px; }
.message-bubble.admin { align-self: flex-end; background: #3498db; color: white; border-bottom-right-radius: 4px; }
.message-bubble.system { align-self: center; background: none; padding: 4px 12px; }
.system-text { font-size: 0.8rem; color: #a0aec0; font-style: italic; }
.bubble-header { display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
.sender-name { font-weight: 600; font-size: 0.8rem; }
.admin-badge { background: rgba(255,255,255,0.3); padding: 1px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
.bubble-content { margin: 0; font-size: 0.95rem; line-height: 1.4; word-wrap: break-word; }
.bubble-time { font-size: 0.7rem; opacity: 0.7; display: block; text-align: right; margin-top: 4px; }

/* INPUT */
.input-area { background: white; padding: 16px 24px; border-top: 1px solid #e5e7eb; display: flex; gap: 12px; }
.chat-input { flex: 1; padding: 12px 16px; border: 2px solid #e5e7eb; border-radius: 24px; font-size: 0.95rem; outline: none; transition: border-color 0.2s; }
.chat-input:focus { border-color: #3498db; }
.send-btn { background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 24px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.send-btn:hover { background: #2980b9; }
.send-btn:disabled { background: #cbd5e0; cursor: not-allowed; }
</style>
