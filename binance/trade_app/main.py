"""
Main FastAPI endpoints and host
"""
import uvicorn
import uuid
import secrets
from starlette.middleware.sessions import SessionMiddleware
from database.model import BotModel, UserLogin, UserCreate, Verify
from fastapi import FastAPI, HTTPException ,WebSocket, Depends, Request
from database.config import get_db, User, Bot
from trading_bot.bot import generator
from exchange_config.exchange import get_exchange
from exchange_config.exchange import fetch_balance
from authentication.login import logincheck
from authentication.signup import create_user
from authentication.verify import verify

""" FastAPI app instance """
app = FastAPI()

""" Project secret key for creating session """
secret_key = secrets.token_hex(16)
app.add_middleware(SessionMiddleware, secret_key=secret_key, max_age=1800)

@app.get("/data")
def data(request: Request,db = Depends(get_db)):
    session = request.session
    user = db.query(User).filter(User.email == session.get("email")).first()
    if user:
        bots = db.query(Bot).join(User).filter(user.id == Bot.owner_id).all()
        return {
            "user_id" : user.id,
            "user" : session.get("email"),
            "bots" : bots
        }
    else:
        return {
            "message" : "not Logged in"
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    websocket endpoint and works as a ping pong server
    """
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echoing back: {message}")

@app.post("/login")
async def login(user: UserLogin, request : Request, db = Depends(get_db)):
    """
    Login url for users
    """
    try:
        session = request.session
        email = session.get("email", "")
        db_user = db.query(User).filter_by(email=user.email).first()

        if email != "" and db_user:
            if email == db_user.email:
                return {
                    'message': 'already logged in'
                }
        else:
            user = logincheck(db, user, db_user)
            session = request.session
            session["email"] = user.email
            return session
         
    
    except Exception as e:
        return {
            'message': 'Verification Failed'
        }

@app.post("/signup")
async def sign_up(user: UserCreate, db = Depends(get_db)):
    """
    sign up function to add to the database
    """
    db_user = db.query(User).filter_by(email=user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    result = create_user(db, user)
    return result

@app.post("/verify")
def verify_otp(user: Verify, db = Depends(get_db)):
    """
    Verify the user and checks for the valid otp
    """
    try:
        result = verify(db, user)

    except Exception as error:
        return HTTPException(status_code = 400, detail = f"{error}")
    
    return result

@app.post("/bot")
async def bot(botdata : BotModel, request : Request,db = Depends(get_db)):
    """
    Working bot that runs in the background doing auto trades
    """

    loss = botdata.loss
    profit = botdata.profit
    total_number_of_trades = botdata.number_of_trades
    ticker = botdata.ticker
    exchange = botdata.exchange
    price = botdata.price
    coin = ticker.split('/')[1]

    session = request.session
    email = session.get("email", "")
    user = db.query(User).filter(User.email == email).first()
    if user:
        balance = await fetch_balance(exchange = exchange, coin = ticker.split('/')[1])
        if price > balance[coin]:
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
                db = db,
                price = price
            )
        return response
    else:
        return {
            "message" : "not logged in"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8007, log_level="info", reload = True)