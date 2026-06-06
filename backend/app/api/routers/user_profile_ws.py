import asyncio
import json
import random
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

async def generate_mock_data():
    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
    genders = ["Male", "Female", "Other"]
    tags_pool = ["developer", "gamer", "reader", "traveler", "foodie", "fitness", "music"]
    regions = ["North", "South", "East", "West"]

    return {
        "user_id": f"u_{random.randint(1000, 9999)}",
        "age_group": random.choice(age_groups),
        "gender": random.choice(genders),
        "active_tags": random.sample(tags_pool, k=random.randint(1, 4)),
        "purchase_trend": [random.randint(50, 200) for _ in range(6)], # e.g., last 6 months
        "region": random.choice(regions)
    }

@router.websocket("/user-profile")
async def websocket_user_profile(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Generate and send mock data every 2 seconds
            data = await generate_mock_data()
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
