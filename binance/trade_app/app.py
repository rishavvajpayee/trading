import os
import ccxt
import asyncio
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

async def get_exchange(exchange):
    test_dict = {
        "binance" :f"""ccxt.binance({{
            'apiKey': "{os.environ.get("BINANCE_API_KEY")}",
            'secret': "{os.environ.get("BINANCE_API_SECRET")}",
        }})""",

        "whitebit" : f"""ccxt.whitebit({{
            'apiKey': "{os.environ.get("BINANCE_API_KEY")}",
            'secret': "{os.environ.get("BINANCE_API_SECRET")}",
        }})""",

        "xyx" :f"""ccxt.xyz({{
            'apiKey': "{os.environ.get("XYZ_API_KEY")}",
            'secret': "{os.environ.get("XYZ_API_SECRET")}",
        }})""",
    }
    try :
        exchange = eval(test_dict[f"{exchange}"])
    except Exception as error:
        raise Exception("No definition of this exchange found in .env")
    return exchange

async def fetch_balance(exchange, coin = ""):
    exchange = await get_exchange(exchange)
    balance = exchange.fetch_balance()
    account = {}
    if coin == "":
        for coin in balance["total"]:
            if balance["total"][f"{coin}"] == 0:
                pass
            else:
                account[f"{coin}"] = balance["total"][f"{coin}"]
    else:
        account[f"{coin}"] = balance["total"][f"{coin}"]
    return account

async def tick(exchange):
    price = exchange.fetch_ticker("BTC/USDT")
    return price



async def ticker(exchange):
    exchange = await get_exchange(exchange)
    price = await tick(exchange)
    return price


if __name__ == "__main__":
    asyncio.run(ticker("binance"))


