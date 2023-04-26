import requests

async def api_api():
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjQzOTE3NTA0OThkNzVkYTM2Zjk3ZTQyIiwiaWF0IjoxNjgxNDYzMjcwLCJleHAiOjMzMTg1OTI3MjcwfQ.nLZddJ0Cmh5AVduesVi2dzrVwMIE-znPZQkbHpW3n1w"
    indicator = "supertrend"
    endpoint = f"https://api.taapi.io/{indicator}"
    parameters = {
        'secret': key,
        'exchange': 'binance',
        'symbol': 'BTC/USDT',
        'interval': '1h'
    } 
    response = requests.get(url = endpoint, params = parameters)
    result = response.json() 
    return result.get('valueAdvice')