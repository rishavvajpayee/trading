"""
Utility functions for running Bot
"""
import ccxt
from fastapi import HTTPException
from exchange_config.exchange import get_exchange


async def per_trade_calc(pt_buy, pt_sell):
    calc = pt_sell - pt_buy
    return calc



async def withdraw_function(response, websocket, uid, last_sell, initial_buy, total_pnl):
    """ Withdraw the amount from exchange to any wallet ( Metamask ) """
    await websocket.send(f"{{WITHDRAWED : {response}, uid : {uid}}}")
    await websocket.send(f"{{TOTAL P&L : {total_pnl},uid : {uid}}}")



async def sell_function(response, websocket, uid, pt_buy, pt_sell, done_number_of_trades, total_pnl, exchange, symbol, amount, price):
    """
    Sell the bought assets ( works on the exchange directly )
    converts the sold asset to the 2nd attribute of ticker
    """

    try :
        order = await get_exchange(exchange).create_limit_sell_order(
                    symbol=symbol,
                    amount=amount,
                    price = price
                )
        await websocket.send(f"{{status : success, order : {order}}}")

    except ccxt.NetworkError as e:
        raise HTTPException(status_code = 500, detail = 'Network Error')

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code = 400, detail = 'Network issue')
    
    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code = 400,detail = 'Invalid Order')
    
    await websocket.send(f"{{SOLD : {response}, uid : {uid}, order : {order}}}")
    

    try:
        pt_sell = response
        total_pnl = total_pnl + (pt_sell - pt_buy)

        pt_pnl = await per_trade_calc(pt_buy = pt_buy, pt_sell = pt_sell)
        await websocket.send(f"{{per_trade_pnl : {pt_pnl}, total_pnl : {total_pnl}, uid : {uid}}}")

        """ increase the number of done trades """
        done_number_of_trades += 1
        return done_number_of_trades, total_pnl
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=error)


async def buy_function(response, websocket, uid, exchange, symbol, amount, price):
    """ Buys assest from the money present in the exchange """
    try:
        order = await get_exchange(exchange).create_limit_buy_order(
                    symbol=symbol,
                    amount=amount,
                    price=price
                )
        
        if order:
            await websocket.send(f"{{status : success, order : {order}}}")
        
        else:
            await websocket.send(f"{{status : Failed, order : {order}}}")

    except ccxt.NetworkError as e:
        raise HTTPException(status_code = 500, detail = 'Network Error')

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code = 400, detail = 'Network issue')
    
    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code = 400,detail = 'Invalid Order')
    

    await websocket.send(f"{{BUY : {response}, uid : {uid}}}")




async def sold(response, done_number_of_trades, number_of_trades, initial_buy, last_sell, websocket, uid, pt_buy, pt_sell, total_pnl, symbol, amount, price):
    """
    runs sell directly without any check ( to be considered )

    runs withdraw if last sell is None and the number of trades are completed
    thus stopping the bot and the process itself
    """
    done_number_of_trades, total_pnl = await sell_function(response, websocket, uid, pt_buy, pt_sell, done_number_of_trades, total_pnl,  symbol, amount, price)
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