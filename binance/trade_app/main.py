"""
Main FastAPI endpoints and host
"""
import logging
import uvicorn
import uuid
from fastapi import FastAPI, WebSocket
from web import generator
from database.model import Bot
from app import fetch_balance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI app")

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    websocket endpoint and works as a ping pong server
    """
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echoing back: {message}")

@app.post("/bot")
async def bot(bot : Bot):
    """
    Workin bot that runs in the background doing auto trades
    """
    loss = bot.loss
    profit = bot.profit
    number_of_trades = bot.number_of_trades
    ticker = bot.ticker
    amount = bot.amount
    exchange = bot.exchange
    coin = ticker.split('/')[0]

    balance = await fetch_balance(exchange = exchange, coin = ticker.split('/')[0])
    if amount > balance[coin]:
        return {
            "message" : "amount exceeds Balance"
        }
    else:
        uid = uuid.uuid4()
        response =  await generator(exchange = exchange, loss = loss, profit = profit, number_of_trades = number_of_trades, uid = uid, ticker = ticker)
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8007, log_level="info", reload=True)

