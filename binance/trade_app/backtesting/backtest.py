import uuid
import asyncio
import websockets
from multiprocessing import Process
from exchange_config.exchange import get_exchange
from machine_learning.ml_api import vivek_api


async def withdraw_function(response, websocket, uid, last_sell, initial_buy):
    await websocket.send(f"{{Message : WITHDRAWED AT {response}, uid : {uid}}}")

    await websocket.send(f"{{Message : TOTAL P&L : {last_sell - initial_buy}, uid : {uid}}}")
    return f"WITHDRAWED AT {response}"

async def sell_function(response, websocket, uid):
    await websocket.send(f"{{Message : SOLD AT {response}, uid : {uid}}}")
    return f"SOLD AT {response}"

async def buy_function(response, websocket, uid):
    await websocket.send(f"{{Message : BUY AT {response}, uid : {uid}}}")
    return f"BUY AT {response}"

async def sold(response, count, number_of_trades, initial_buy, last_sell, websocket, uid):
    await sell_function(response, websocket, uid)
    if last_sell == None and count == number_of_trades:
        last_sell = response
        await withdraw_function(response, websocket, uid, last_sell, initial_buy)

async def check(stop_loss = None, buy = None, profit = None):
    stop_loss = buy - ((stop_loss/100) * buy)
    profit_margin = buy + ((profit/100) * buy)
    return stop_loss, profit_margin

""" 
TRADING BOT THAT RUNS ALL THE TIME
"""
class TestBot:
    async def test(self, loss = None, profit = None, number_of_trades = None, uid = None,ticker = None): 
        exchange = await get_exchange("binance")
        bot = True
        buyed = None
        count = 0
        initial_buy = None
        last_sell = None

        while bot and count <= number_of_trades:
            async with websockets.connect("ws://localhost:8765") as websocket:
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
                    api_resp = await vivek_api()
                    if api_resp == None:
                        if buyed:
                            pass
                        else:
                            await buy_function(response, websocket, uid)
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
                    stop_loss, profit_margin = await check(stop_loss = loss, buy = buyprice, profit = profit)
                    if response > stop_loss and response < profit_margin:
                        pass
                    else:
                        await sold(response, count, number_of_trades, initial_buy, last_sell, websocket, uid)
                        count += 1
                        flag = False
                        buyed = False
                        print("socket closed")
    
    def process(self, loss, profit, number_of_trades, uid, ticker):
        asyncio.run(self.test(loss, profit, number_of_trades, uid, ticker))



async def generator(exchange = None, loss = None, profit = None, total_number_of_trades = None, uid = None, ticker = None, user = None, db = None ):
    """
    Takes in user values and start a bot Sub-Process.
    """
    try :
        Process(target=TestBot().process, args=(exchange ,loss, profit, total_number_of_trades, uid, ticker)).start()
    
    except Exception as error:
        return {
            "status" : "Bot process start failed"
        }
    """ 
    Once Done return values 
    """

    return {
        "uid" : uid,
        "status" : "running successfully",
    }