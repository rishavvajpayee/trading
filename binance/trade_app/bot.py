import asyncio
import websockets
from multiprocessing import Process, Value, Array
from taapi import api_api
from exchange import get_exchange
from database.config import Bot

async def withdraw_function(process,response, websocket, uid, last_sell, initial_buy):
    await websocket.send(f"{{Message : WITHDRAWED AT {response}, uid : {uid}}}")
    msg =await websocket.recv()
    print(msg)

    await websocket.send(f"{{Message : TOTAL P&L : {last_sell - initial_buy},uid : {uid}}}")
    msg =await websocket.recv()
    print(msg)

    return

async def sell_function(response, websocket, uid):
    await websocket.send(f"{{Message : SOLD AT {response}, uid : {uid}}}")
    msg =await websocket.recv()
    print(msg)

    return f"SOLD AT {response}"

async def buy_function(response, websocket, uid):
    await websocket.send(f"{{Message : BUY AT {response}, uid : {uid}}}")
    msg =await websocket.recv()
    print(msg)
    return f"BUY AT {response}"

"""
TRADING BOT THAT RUNS ALL THE TIME
"""
class BotClass:
    async def test(self, exchange = None, loss = 0.00001, profit = 0.000001, number_of_trades = 2, uid = "123", ticker = "BTC/USDT"): 
        exchange = await get_exchange(exchange)
        bot = True
        buyed = None
        count = 0
        initial_buy = None
        last_sell = None

        while bot and count <= number_of_trades:
            async with websockets.connect("ws://localhost:8765/") as websocket:
                flag = True
                try:
                    response = exchange.fetch_ticker(ticker)
                    response = response["last"]
                    """
                    VIVEK'S API
                    """
                    """
                    Api to be called to get the buy sell indication
                    """
                    api_resp = await api_api()
                    if api_resp == None:
                        if buyed:
                            pass
                        else:
                            message = await buy_function(response, websocket, uid)
                            if initial_buy == None:
                                initial_buy = response
                            buyprice = response
                            buyed = True

                    elif api_resp == "sell":
                        if buyed:
                            sold(response, count, number_of_trades, initial_buy, last_sell, websocket, uid)
                            count += 1
                            flag = False
                            buyed = False
        
                except Exception as e:
                    flag = False
                
                if flag and buyed:
                    stop_loss, profit_margin = await check(response, stop_loss = loss, buy = buyprice, profit = profit)
                    if response > stop_loss and response < profit_margin:
                        pass
                    else:
                        await sold(self, response, count, number_of_trades, initial_buy, last_sell, websocket, uid)
                        count += 1
                        flag = False
                        buyed = False
                        print("Trade Complete : ", count)

        if not bot:
            ...
    
    def process(self,exchange, loss, profit, number_of_trades, uid, ticker):
        asyncio.run(self.test(exchange, loss, profit, number_of_trades, uid, ticker))



async def sold(process,response, count, number_of_trades, initial_buy, last_sell, websocket, uid):
    await sell_function(response, websocket, uid)
    if last_sell == None and count == number_of_trades:
        last_sell = response
        await withdraw_function(process,response, websocket, uid, last_sell, initial_buy)

async def check(response, stop_loss = 0.1, buy = 1023, profit = 0.2):
    stop_loss = buy - ((stop_loss/100) * buy)
    profit_margin = buy + ((profit/100) * buy)
    return stop_loss, profit_margin

async def generator(exchange = None, loss = 0.00001, profit = 0.00001, number_of_trades = 2, uid = "123", ticker = "BTC/USDT", user = None, db = None ):
    
    p = Process(target=BotClass().process, args=(exchange ,loss, profit, number_of_trades, uid, ticker))
    p.start()
    bot = Bot(name=ticker, bot_ids=uid, owner=user)
    user.bots.append(bot)
    db.add(user)
    db.commit()
    return {
        "uid" : uid,
        "status" : "running successfully",
        "user_id" : user.id,
        "username" : user.username,
    }
