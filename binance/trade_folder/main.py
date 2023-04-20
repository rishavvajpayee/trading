# backend/app/main.py
import asyncio
import logging
import uvicorn
import websockets
import websocket
import time
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from web import generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI app")

app = FastAPI()

# Define a WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echoing back: {message}")

@app.get("/bot")
async def main():
    time.sleep(2)
    response =  await generator()
    print(response)
    return response



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True)

