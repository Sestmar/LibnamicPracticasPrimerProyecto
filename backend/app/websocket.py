"""
Módulo de WebSocket para chat en tiempo real.
Cada cliente tiene su sala PRIVADA (room_id = email del cliente).
Los administradores pueden unirse a cualquier sala desde el panel.
"""
import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List


class ChatRoom:
    """Sala de chat privada entre un cliente y soporte."""
    def __init__(self, room_id: str, client_email: str):
        self.room_id = room_id
        self.client_email = client_email
        self.connections: List[WebSocket] = []
        self.messages: List[dict] = []       # Solo mensajes reales
        self.created_at = datetime.utcnow().isoformat()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        # Enviar historial al nuevo participante
        if self.messages:
            await websocket.send_json({"type": "history", "messages": self.messages})

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Envía un mensaje a todos los conectados. Solo guarda mensajes reales."""
        # Solo guardamos mensajes tipo 'message', NO los de tipo 'system'
        if message.get("type") == "message":
            self.messages.append(message)

        dead = []
        for conn in self.connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.connections.remove(d)


class ChatManager:
    """Gestiona todas las salas de chat."""
    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}

    def get_or_create_room(self, room_id: str, client_email: str = "") -> ChatRoom:
        if room_id not in self.rooms:
            self.rooms[room_id] = ChatRoom(room_id, client_email or room_id)
        return self.rooms[room_id]

    def get_active_rooms(self) -> list:
        """Devuelve salas que tienen mensajes reales (para el panel admin)."""
        return [
            {
                "room_id": room.room_id,
                "client_email": room.client_email,
                "message_count": len(room.messages),
                "active_connections": len(room.connections),
                "created_at": room.created_at
            }
            for room in self.rooms.values()
            if room.messages  # Solo salas con mensajes reales
        ]


# Instancia global
chat_manager = ChatManager()
