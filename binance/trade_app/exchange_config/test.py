import ccxt
import asyncio
from dotenv import load_dotenv
from exchange import get_exchange
from fastapi import HTTPException

symbol = 'BTC/USDT'
price = 1

async def get_price():
    exchange = await get_exchange("binance")
    current_price =  exchange.fetch_ticker(symbol)["ask"] + exchange.fetch_ticker(symbol)["bid"] / 2
    amount = price / current_price
    return amount, exchange

async def place():
    amount, exchange = await get_price()
    try: 
        order = exchange.create_order(symbol, "market", "buy", amount)
        print(order)

    except ccxt.NetworkError as e:
        raise HTTPException(status_code = 500, detail = f'Network Error : {e}')

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code = 400, detail = f'Network issue : {e}')
    
    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code = 400,detail = f'Invalid Order : {e}')
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=error)

asyncio.run(place())