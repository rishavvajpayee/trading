"""
Main FastAPI endpoints and host
"""
import uvicorn
import uuid
from database.config import get_db, User, Bot
from fastapi import FastAPI, WebSocket, Depends
from bot import generator
from database.model import BotModel, UserModel, Data
from exchange import fetch_balance
# from database.config import get_db, User, Bot

app = FastAPI()

@app.get("/data")
def data(data : Data ,db = Depends(get_db)):
    data.username = "rishav"
    user = db.query(User).filter(User.username == data.username).first()
    # bot = db.query(Bot).filter(Bot.owner_id == 2).all()
    bots = db.query(Bot).join(User).filter(user.id == Bot.owner_id).all()
    return bots


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    websocket endpoint and works as a ping pong server
    """
    # await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echoing back: {message}")

@app.post("/bot")
async def bot(botdata : BotModel,db = Depends(get_db)):
    """
    Workin bot that runs in the background doing auto trades
    """

    loss = botdata.loss
    profit = botdata.profit
    total_number_of_trades = botdata.number_of_trades
    ticker = botdata.ticker
    amount = botdata.amount
    exchange = botdata.exchange
    coin = ticker.split('/')[0]

    user = db.query(User).filter(User.username == "parth", User.password == "test123").first()
    balance = await fetch_balance(exchange = exchange, coin = ticker.split('/')[0])
    if amount > balance[coin]:
        return {
            "message" : "amount exceeds Balance"
        }
    else:
        uid = uuid.uuid4()
        response =  await generator(
            exchange = exchange, 
            loss = loss, 
            profit = profit, 
            total_number_of_trades = total_number_of_trades, 
            uid = uid, 
            ticker = ticker, 
            user = user, 
            db = db
            )
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8007, log_level="info", reload=True)