"""
Utility functions for running Bot
"""
import ccxt
import json
import requests
from fastapi import HTTPException
from exchange_config.exchange import fetch_balance, get_exchange

async def per_trade_calc(pt_buy, pt_sell):
    calc = pt_sell - pt_buy
    return calc

async def fetch_curr_price(exchange, ticker):
    price = exchange.fetch_ticker(ticker)["ask"] + exchange.fetch_ticker(ticker)["bid"] / 2
    return price

async def getbalance(exchange, ticker):
    balance = await fetch_balance(exchange)
    print(balance)
    return balance[ticker.split("/")[0]]

async def get_price(exchange, ticker, price):
    current_price =  exchange.fetch_ticker(ticker)["ask"] + exchange.fetch_ticker(ticker)["bid"] / 2
    amount = price / current_price
    return amount, exchange

async def withdraw_function(
        response, 
        websocket, 
        uid, 
        total_pnl, 
        exchange, 
        symbol, 
    ):

    """ Withdraw the amount from exchange to any wallet ( Metamask ) """

    try:
        """ get address from the DB """
        address = ""
    
    except Exception as e:
        raise HTTPException(code = 500, detail = "DB error cannot get the withdraw address from database")

    try :
        """
        amount = await getbalance(exchange, symbol)
        order = await exchange.withdraw(
                    code=symbol.split("/")[0],
                    amount=amount,
                    address = address,
                    tag = None,
                    params = {
                        "network" : "ARB"
                    }
                )
        """
        order = "Withdrawed"
        await websocket.send(f"{{status : success, order : {order}}}")

    except ccxt.NetworkError as e:
        raise HTTPException(status_code = 500, detail = f'Network Error : {e}')
    
    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code = 400, detail = f'Network issue {e}')
    
    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code = 400,detail = f'Invalid Order : {e}')
    
    except Exception as err:
        raise HTTPException(status_code = 500, detail = f"{err}")

    await websocket.send(f"{{WITHDRAWED : {response}, uid : {uid}}}")
    await websocket.send(f"{{TOTAL P&L : {total_pnl},uid : {uid}}}")



async def sell_function(
        response = None,
        websocket = None,
        uid = None,
        pt_buy = None,
        pt_sell = None,
        done_number_of_trades = None,
        total_pnl = None,
        exchange = None,
        symbol = None,
        price = None
    ):
    """
    Sell the bought assets ( works on the exchange directly )
    converts the sold asset to the 2nd attribute of ticker
    """

    try :
        # balance = await fetch_balance(exchange)
        # balance = balance[symbol.split("/")[0]]

        balance = await getbalance(exchange, symbol)
        print(balance)
        amount = balance
        current_price = await fetch_curr_price(exchange, symbol)
        sell_price = balance * current_price
        order = exchange.create_order(
                    symbol,
                    "market",
                    "sell",
                    amount
                )
        print(order)
        if order:
            await websocket.send(f"{{SOLD : {amount}, uid : {uid}, order : {order}}}")
        else:
            await websocket.send(f"{{status : failed}}")

    except ccxt.NetworkError as e:
        raise HTTPException(status_code = 500, detail = f'Network Error {e}')

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code = 400, detail = f'Network issue: {e}')
    
    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code = 400,detail = f'Invalid Order : {e}')
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=error)
    

    try:
        pt_sell = sell_price
        total_pnl = total_pnl + (pt_sell - pt_buy)

        pt_pnl = await per_trade_calc(pt_buy = pt_buy, pt_sell = pt_sell)

        """ increase the number of done trades """
        done_number_of_trades += 1
        return done_number_of_trades, total_pnl, amount, sell_price
    
    except Exception as error:
        raise HTTPException(status_code=500, detail = error)


async def buy_function(response, websocket, uid, exchange, symbol, price):
    """ Buys assest from the money present in the exchange """
    try:
        current_price =  exchange.fetch_ticker(symbol)["ask"] + exchange.fetch_ticker(symbol)["bid"] / 2
        amount = price / current_price
        order = exchange.create_order(
                    symbol,
                    "market",
                    "buy",
                    amount,
                )
        
        """
        """
        
        if order:
            await websocket.send(f"{{status : success, order : {order}}}")
            print(order)
            """ 
            Bot Trade start save in DB 
            """
            try:

                url = "http://localhost:8007/database"

                payload = json.dumps({
                    "bot_id": str(uid),
                    "buy_value": response,
                    "sell_value": None,
                    "pnl": None
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                dbresp = requests.request("POST", url, headers=headers, data=payload)
                print(dbresp.text)

            except Exception as error:
                raise Exception(error)
        
        else:
            await websocket.send(f"{{status : Failed, order : {order}}}")

    except ccxt.NetworkError as e:
        raise HTTPException(status_code = 500, detail = f'Network Error : {e}')

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code = 400, detail = f'Network issue : {e}')
    
    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code = 400,detail = f'Invalid Order : {e}')
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=error)
    

    await websocket.send(f"{{BUY : {price}, uid : {uid}}}")




async def sold(
        response, 
        done_number_of_trades, 
        total_number_of_trades, 
        initial_buy,
        last_sell, 
        websocket, 
        uid, 
        pt_buy, 
        pt_sell, 
        total_pnl, 
        exchange, 
        symbol,  
        price,
    ):
    """
    runs sell directly without any check ( to be considered )

    runs withdraw if last sell is None and the number of trades are completed
    thus stopping the bot and the process itself
    """
    done_number_of_trades, total_pnl, amount, sell_price = await sell_function(
        response = response, 
        websocket = websocket, 
        uid = uid, 
        pt_buy = pt_buy, 
        pt_sell= pt_sell, 
        done_number_of_trades = done_number_of_trades, 
        total_pnl = total_pnl, 
        exchange = exchange, 
        symbol = symbol, 
        price = price)


    if last_sell == None and done_number_of_trades == total_number_of_trades:
        last_sell = sell_price
        pnl = last_sell - initial_buy
        """ Bot Trade start save in DB """
        try:

            url = "http://localhost:8007/database"

            payload = json.dumps({
                "bot_id": str(uid),
                "buy_value": None,
                "sell_value": last_sell,
                "pnl": pnl 
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)

        except Exception as error:
            raise Exception(error)
        
        await withdraw_function(
            response, 
            websocket, 
            uid, 
            total_pnl, 
            exchange, 
            symbol, 
        )

    return done_number_of_trades, total_pnl

async def check(response, stop_loss = 0.1, buy = 1023, profit = 0.2):
    """
    Checks if the real time assest value touches our stop loss or profit margin
    """

    stop_loss = buy - ((stop_loss/100) * buy)
    profit_margin = buy + ((profit/100) * buy)

    return stop_loss, profit_margin