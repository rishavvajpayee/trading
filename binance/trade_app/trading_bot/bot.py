import os
import asyncio
import websockets
from multiprocessing import Process
from machine_learning.ml_api import vivek_api
from exchange_config.exchange import get_exchange
from database.config import Bot, Trade
from bot_utils.utils import buy_function, sold, check, getbalance, fetch_curr_price
from dotenv import load_dotenv

""" loads the environment """
load_dotenv()

"""
TRADING BOT THAT RUNS ALL THE TIME
"""


class BotClass:
    """
    BOT CLASS
    """

    async def runbot(
        self,
        price=None,
        exchange=None,
        loss=None,
        profit=None,
        total_number_of_trades=None,
        uid=None,
        ticker=None,
    ):
        """
        Runs the bot instance in a subprocess
        """
        exchange = await get_exchange(exchange)
        bot = True
        buyed = False
        done_number_of_trades = 0
        initial_buy = None
        last_sell = None
        pt_buy = None
        pt_sell = None
        total_pnl = 0
        symbol = ticker

        while bot and done_number_of_trades < total_number_of_trades:
            """
            Connect to the websocket server running on other port
            to communicate real time with any client that connects to
            this server.
            """
            try:
                async with websockets.connect(
                    os.environ.get("LOCAL_WEBSOCKET_URL")
                ) as websocket:
                    flag = True

                    """ 
                    Exception handling for any Exceptions 
                    """
                    try:
                        response = price
                        """
                        i need to add the Trade DB setup here to update the
                        bot trading data.
                        """

                        """
                        Api to be called to get the buy sell indication
                        """
                        api_resp = await vivek_api()

                        if api_resp == None:
                            if buyed:
                                pass
                            else:
                                await buy_function(
                                    response, websocket, uid, exchange, symbol, price
                                )
                                if initial_buy == None:
                                    initial_buy = response

                                pt_buy = response
                                buyprice = response
                                buyed = True

                        elif api_resp == "sell":
                            if buyed:
                                done_number_of_trades, total_pnl = await sold(
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
                                )
                                done_number_of_trades += 1
                                flag = False
                                buyed = False
                                print(
                                    f"{{trade complete : {done_number_of_trades}, uid : {uid}}}"
                                )

                        else:
                            continue

                    except Exception as error:
                        flag = False
                        raise Exception(f"{error}")

                    try:
                        if flag and buyed:
                            stop_loss, profit_margin = await check(
                                response, stop_loss=loss, buy=buyprice, profit=profit
                            )
                            balance = await getbalance(exchange, ticker)
                            print(balance)
                            current_price = await fetch_curr_price(exchange, ticker)

                            current_price = balance * current_price
                            print(
                                f"Current price : {current_price} , stop_loss : {stop_loss}, profit_margin : {profit_margin}"
                            )

                            if (
                                current_price > stop_loss
                                and current_price < profit_margin
                            ):
                                pass
                            else:
                                done_number_of_trades, total_pnl = await sold(
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
                                )
                                flag = False
                                buyed = False
                                print(
                                    f"{{trade complete : {done_number_of_trades}, uid : {uid}}}"
                                )
                                break

                    except Exception as error:
                        raise Exception(f"{error}")

            except Exception as error:
                raise Exception(f"{error}")

    """
    Process Function that call the main bot asynchronously
    """

    def process(
        self,
        price,
        exchange,
        loss,
        profit,
        total_number_of_trades,
        uid,
        ticker,
    ):
        """async process"""
        asyncio.run(
            self.runbot(
                price,
                exchange,
                loss,
                profit,
                total_number_of_trades,
                uid,
                ticker,
            )
        )


async def generator(
    exchange=None,
    loss=None,
    profit=None,
    total_number_of_trades=None,
    uid=None,
    ticker=None,
    user=None,
    price=None,
    db=None,
):
    """
    Takes in user values and start a bot Sub-Process.
    """
    try:
        Process(
            target=BotClass().process,
            args=(
                price,
                exchange,
                loss,
                profit,
                total_number_of_trades,
                uid,
                ticker,
            ),
        ).start()

        bot = Bot(name=ticker, bot_ids=uid, owner=user)

    except Exception as error:
        return {"status": f"Bot process start failed : {error}"}

    """ Update values in Database """
    try:
        user.bots.append(bot)
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception as error:
        return {"status": f"Database updation failed : {error}"}

    """ 
    Once Done return values 
    """

    return {
        "uid": uid,
        "status": "running successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "name": ticker,
    }
