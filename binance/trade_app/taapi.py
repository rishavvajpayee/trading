import requests

async def api_api():

    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjQzOTE3NTA0OThkNzVkYTM2Zjk3ZTQyIiwiaWF0IjoxNjgxNDYzMjcwLCJleHAiOjMzMTg1OTI3MjcwfQ.nLZddJ0Cmh5AVduesVi2dzrVwMIE-znPZQkbHpW3n1w"

    # data = requests.get(f'https://api.taapi.io/supertrend?secret={key}&exchange=binance&symbol=BTC/USDT&interval=1h')
    # print(data.text)

    indicator = "supertrend"
    
    # Define endpoint 
    endpoint = f"https://api.taapi.io/{indicator}"

    # Define a parameters dict for the parameters to be sent to the API 

    parameters = {
        'secret': key,
        'exchange': 'binance',
        'symbol': 'BTC/USDT',
        'interval': '1h'
    } 
    
    # Send get request and save the response as response object 
    response = requests.get(url = endpoint, params = parameters)
    
    # Extract data in json format 
    result = response.json() 

    # Print result
    return result.get('valueAdvice')



# def call():
#     data = requests.get('http://localhost:8000/bot')
#     print(data.text)

# call()