"""
API CALL FOR BUY SELL DATA
"""

import requests

async def vivek_api():
    """
    An api that gives in response similar to Supertrend API DATA
    """
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjQzOTE3NTA0OThkNzVkYTM2Zjk3ZTQyIiwiaWF0IjoxNjgxNDYzMjcwLCJleHAiOjMzMTg1OTI3MjcwfQ.nLZddJ0Cmh5AVduesVi2dzrVwMIE-znPZQkbHpW3n1w"
    indicator = "supertrend"
    endpoint = f"https://api.taapi.io/{indicator}"
    parameters = {
        'secret': key,
        'exchange': 'binance',
        'symbol': 'ARB/USDT',
        'interval': '1h'
    } 
    
    response = requests.get(url = endpoint, params = parameters)
    result = response.json() 

    return result.get('valueAdvice')