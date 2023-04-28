import os
import ccxt
import asyncio
from web3 import Web3
from dotenv import load_dotenv

"loads the environment variables to be accessed by this py file"
load_dotenv()

async def get_exchange(exchange):

    """
    Creates the instance of the Exchange you want to connect to.
    you have to create a .env file and list the credentials there first
    in order to connect with your own exchange 
    """

    exchange_dict = {
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
        exchange = eval(exchange_dict[f"{exchange}"])

    except Exception as error:
        raise Exception(
            "No definition of this exchange found in environment variables"
        )
    
    return exchange

async def fetch_balance(exchange, coin = ""):
    """
    Fetches balance from the exchange for the particular 
    """
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
