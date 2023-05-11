import ccxt
from dotenv import load_dotenv
from exchange_config.exchange import get_exchange


symbol = 'BTC/USDT'
price = 10

current_price =  get_exchange("binance").fetch_ticker(symbol)["ask"] + get_exchange("binance").fetch_ticker(symbol)["bid"] / 2
amount = price / current_price

order = get_exchange("binance").create_market_buy_order(symbol, amount)
print(order)