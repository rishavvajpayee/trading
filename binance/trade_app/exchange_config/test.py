import ccxt
import asyncio
from exchange import get_exchange, fetch_balance
from fastapi import HTTPException

symbol = "ARB/USDT"
price = 20


async def fetch_curr_price():
    """
    fetch current price of the left side of the ticker
    """


async def get_price():
    """
    get current price of the ticker
    """
    exchange = await get_exchange("binance")
    current_price = (
        exchange.fetch_ticker(symbol)["ask"] + exchange.fetch_ticker(symbol)["bid"] / 2
    )
    amount = price / current_price
    return amount, exchange


async def getbalance():
    exchange = await get_exchange("binance")
    balance = await fetch_balance(exchange)
    print(balance)
    return balance


async def place():
    amount, exchange = await get_price()
    try:
        order = exchange.create_order(symbol, "market", "buy", amount)
        print(order)

    except ccxt.NetworkError as e:
        raise HTTPException(status_code=500, detail=f"Network Error : {e}")

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code=400, detail=f"Network issue : {e}")

    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code=400, detail=f"Invalid Order : {e}")

    except Exception as error:
        raise HTTPException(status_code=500, detail=f" Exception : {error}")


async def sell():
    balance = await getbalance()
    amount = balance[symbol.split("/")[0]]
    print(amount)
    exchange = await get_exchange("binance")

    try:
        order = exchange.create_order(symbol, "market", "sell", amount)

        print(order)

    except ccxt.NetworkError as e:
        raise HTTPException(status_code=500, detail=f"Network Error : {e}")

    except ccxt.InsufficientFunds as e:
        raise HTTPException(status_code=400, detail=f"Network issue : {e}")

    except ccxt.InvalidOrder as e:
        raise HTTPException(status_code=400, detail=f"Invalid Order : {e}")

    except Exception as error:
        raise HTTPException(status_code=500, detail=error)


asyncio.run(getbalance())
