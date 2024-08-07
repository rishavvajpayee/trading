"""
Main FastAPI endpoints and host
"""
import uuid
import uvicorn
from datetime import datetime
from starlette.middleware.sessions import SessionMiddleware
from database.model import BotModel, UserLogin, UserCreate, Verify, Database
from fastapi import FastAPI, HTTPException, WebSocket, Depends, Request
from database.config import get_db, User, Bot, Trade
from trading_bot.bot import generator
from exchange_config.exchange import fetch_balance
from authentication.login import logincheck
from authentication.signup import create_user
from authentication.verify import verify
from authentication import logout
from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.orm import joinedload
from fastapi.middleware.cors import CORSMiddleware

""" FastAPI app instance """
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(SessionMiddleware, secret_key="12345", max_age=60 * 60)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
connected = set()
""" Project secret key for creating session """


@app.post("/database")
def database(database: Database, request: Request, db=Depends(get_db)):
    uid = database.bot_id
    buy_value = database.buy_value
    sell_value = database.sell_value
    pnl = database.pnl

    session = request.session

    NOW = datetime.now()
    dbbot = db.query(Bot).filter(Bot.bot_ids == uid).first()

    if buy_value:
        trade = Trade(
            bot_id=uid, buy_value=buy_value, timestamp=NOW.strftime("%d/%m/%Y %H:%M:%S")
        )

        """
        TRY DB UPDATE
        """
        try:
            dbbot.trades.append(trade)
            db.add(dbbot)
            db.commit()
            db.refresh(dbbot)

        except Exception as error:
            print(error)

    elif sell_value:
        try:
            trade = db.query(Trade).filter(Trade.bot_id == dbbot.id).first()
            trade.sell_value = sell_value
            trade.pnl = pnl
            db.commit()

        except Exception as error:
            raise Exception(error)

    else:
        raise Exception("cannot find a valid sell_value or buy_value")


@app.get("/data")
def data(request: Request, db=Depends(get_db)):
    session = request.session
    print(session)
    user = db.query(User).filter(User.email == session.get("email")).first()

    """
    NEEDED FOR TESTING PURPOSE ONLY

    bots_with_trades = db.query(Bot).options(joinedload(Bot.trades)).all()
    for bot in bots_with_trades:
        pass
        for trade in bot.trades:
            pass
    """

    if user:
        bots = (
            db.query(Bot)
            .options(joinedload(Bot.trades))
            .join(User)
            .filter(user.id == Bot.owner_id)
            .all()
        )
        return {
            "user_id": user.id,
            "user": session.get("email"),
            "bots": bots,
        }

    else:
        return {"message": "not Logged in"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    websocket endpoint and works as a ping pong server
    """

    await websocket.accept()
    connected.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            for client in websocket:
                await client.send_text(f"Echoing back: {message}")

    except Exception as error:
        raise HTTPException(error)

    finally:
        connected.remove(websocket)


@app.post("/login")
async def login(user: UserLogin, request: Request, db=Depends(get_db)):
    """
    Login url for users
    """
    try:
        sess = request.session
        email = sess.get("email", "")
        db_user = db.query(User).filter_by(email=user.email).first()

        if email != "" and email != None and db_user:
            if email == db_user.email:
                return {"message": "already logged in"}
        else:
            user = logincheck(db, user, db_user)
            sess["email"] = user.email
            return sess

    except Exception as e:
        return {"message": "Verification Failed"}


@app.post("/signup")
async def sign_up(user: UserCreate, db=Depends(get_db)):
    """
    sign up function to add to the database
    """
    db_user = db.query(User).filter_by(email=user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    result = create_user(db, user)
    return result


@app.post("/verify")
def verify_otp(user: Verify, db=Depends(get_db)):
    """
    Verify the user and checks for the valid otp
    """
    try:
        result = verify(db, user)

    except Exception as error:
        return HTTPException(status_code=400, detail=f"{error}")

    return result


@app.post("/logout")
async def logout_user(request: Request):
    logout.logout(request)


@app.delete("/delete")
async def delete(request: Request, db=Depends(get_db)):
    """
    Delete the current active User
    """

    session = request.session
    user = db.query(User).filter(User.email == session.get("email")).first()
    print(session.get("email"))
    print(user)
    if user:
        db.delete(user)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": "Account Deleted"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in"
        )


@app.post("/bot")
async def bot(botdata: BotModel, request: Request, db=Depends(get_db)):
    """
    Working bot that runs in the background doing auto trades
    """

    loss = botdata.loss
    profit = botdata.profit
    total_number_of_trades = botdata.number_of_trades
    ticker = botdata.ticker
    exchange = botdata.exchange
    price = botdata.price
    coin = ticker.split("/")[1]

    session = request.session
    email = session.get("email", "")
    user = db.query(User).filter(User.email == email).first()
    if user:
        balance = await fetch_balance(exchange=exchange, coin=ticker.split("/")[1])
        if price > balance[coin]:
            return {"message": "amount exceeds Balance"}
        else:
            uid = uuid.uuid4()
            response = await generator(
                exchange=exchange,
                loss=loss,
                profit=profit,
                total_number_of_trades=total_number_of_trades,
                uid=uid,
                ticker=ticker,
                user=user,
                price=price,
                db=db,
            )
        return response
    else:
        return {"message": "not logged in"}


if __name__ == "__main__":
    print(app)
    uvicorn.run("main:app", host="localhost", port=8007, log_level="info", reload=False)
