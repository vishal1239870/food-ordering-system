from typing import Dict, List
from fastapi import WebSocket
import json

class ConnectionManager:
    """Manages WebSocket connections for real-time order updates"""
    
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store connections by role (kitchen, waiter)
        self.role_connections: Dict[str, List[WebSocket]] = {
            "kitchen": [],
            "waiter": [],
            "admin": []
        }
    
    async def connect(self, websocket: WebSocket, user_id: int = None, role: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        
        if role in self.role_connections:
            self.role_connections[role].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int = None, role: str = None):
        """Remove a WebSocket connection"""
        if user_id and user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        if role in self.role_connections:
            if websocket in self.role_connections[role]:
                self.role_connections[role].remove(websocket)
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def send_to_role(self, message: dict, role: str):
        """Send message to all users with specific role"""
        if role in self.role_connections:
            dead_connections = []
            for connection in self.role_connections[role]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for connection in dead_connections:
                if connection in self.role_connections[role]:
                    self.role_connections[role].remove(connection)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        # Broadcast to user connections
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except:
                    pass
        
        # Broadcast to role connections
        for role_connections in self.role_connections.values():
            for connection in role_connections:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def notify_order_update(self, order_id: int, user_id: int, status: str, order_data: dict):
        """Notify about order status update"""
        message = {
            "type": "order_update",
            "order_id": order_id,
            "status": status,
            "data": order_data
        }
        
        # Notify customer
        await self.send_personal_message(message, user_id)
        
        # Notify kitchen if order is placed
        if status == "Placed":
            await self.send_to_role(message, "kitchen")
        
        # Notify waiter if ready to serve
        if status == "Ready to Serve":
            await self.send_to_role(message, "waiter")
        
        # Notify admin
        await self.send_to_role(message, "admin")

# Global manager instance
manager = ConnectionManager()