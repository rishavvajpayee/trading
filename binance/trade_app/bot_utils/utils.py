"""
Utility functions for running Bot
"""


async def withdraw_function(process,response, websocket, uid, last_sell, initial_buy):
    """
    Withdraw the amount from exchange to any wallet ( Metamask )
    """
    await websocket.send(f"{{Message : WITHDRAWED : {response}, uid : {uid}}}")
    await websocket.send(f"{{Message : TOTAL P&L : {last_sell - initial_buy},uid : {uid}}}")

async def sell_function(response, websocket, uid):
    """
    Sell the bought assets ( works on the exchange directly )
    converts the sold asset to the 2nd attribute of ticker
    """
    await websocket.send(f"{{Message : SOLD : {response}, uid : {uid}}}")

async def buy_function(response, websocket, uid):
    """
    Buys assest from the money present in the exchange
    """
    await websocket.send(f"{{Message : BUY AT {response}, uid : {uid}}}")

async def sold(process,response, count, number_of_trades, initial_buy, last_sell, websocket, uid):
    """
    runs sell directly without any check ( to be considered )

    runs withdraw if last sell is None and the number of trades are completed
    thus stopping the bot and the process itself
    """
    await sell_function(response, websocket, uid)
    if last_sell == None and count == number_of_trades:
        last_sell = response
        await withdraw_function(process,response, websocket, uid, last_sell, initial_buy)

async def check(response, stop_loss = 0.1, buy = 1023, profit = 0.2):
    """
    Checks if the real time assest value touches our stop loss or profit margin
    """

    stop_loss = buy - ((stop_loss/100) * buy)
    profit_margin = buy + ((profit/100) * buy)

    return stop_loss, profit_margin