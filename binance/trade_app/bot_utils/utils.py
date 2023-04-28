"""
Utility functions for running Bot
"""


async def per_trade_calc(pt_buy, pt_sell):
    calc = pt_sell - pt_buy
    return calc



async def withdraw_function(response, websocket, uid, last_sell, initial_buy, total_pnl):
    """ Withdraw the amount from exchange to any wallet ( Metamask ) """
    await websocket.send(f"{{WITHDRAWED : {response}, uid : {uid}}}")
    await websocket.send(f"{{TOTAL P&L : {total_pnl},uid : {uid}}}")



async def sell_function(response, websocket, uid, pt_buy, pt_sell, done_number_of_trades, total_pnl):
    """
    Sell the bought assets ( works on the exchange directly )
    converts the sold asset to the 2nd attribute of ticker
    """
    await websocket.send(f"{{SOLD : {response}, uid : {uid}}}")
    pt_sell = response
    total_pnl = total_pnl + (pt_sell - pt_buy)
    pt_pnl = await per_trade_calc(pt_buy = pt_buy, pt_sell = pt_sell)
    await websocket.send(f"{{per_trade_pnl : {pt_pnl}, total_pnl : {total_pnl}, uid : {uid}}}")
    done_number_of_trades += 1
    return done_number_of_trades, total_pnl



async def buy_function(response, websocket, uid):
    """ Buys assest from the money present in the exchange """

    await websocket.send(f"{{BUY : {response}, uid : {uid}}}")




async def sold(response, done_number_of_trades, number_of_trades, initial_buy, last_sell, websocket, uid, pt_buy, pt_sell, total_pnl):
    """
    runs sell directly without any check ( to be considered )

    runs withdraw if last sell is None and the number of trades are completed
    thus stopping the bot and the process itself
    """
    done_number_of_trades, total_pnl = await sell_function(response, websocket, uid, pt_buy, pt_sell, done_number_of_trades, total_pnl)
    if last_sell == None and done_number_of_trades == number_of_trades:
        last_sell = response
        await withdraw_function(response, websocket, uid, last_sell, initial_buy, total_pnl)

    return done_number_of_trades, total_pnl




async def check(response, stop_loss = 0.1, buy = 1023, profit = 0.2):
    """
    Checks if the real time assest value touches our stop loss or profit margin
    """

    stop_loss = buy - ((stop_loss/100) * buy)
    profit_margin = buy + ((profit/100) * buy)

    return stop_loss, profit_margin