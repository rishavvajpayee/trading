import time
import asyncio
import websockets

# async def websocket_client():
#     async with websockets.connect("ws://localhost:8000/ws") as websocket:
#         for i in range(200):
#             time.sleep(0.1)
#             await websocket.send(f"{i}")
#             message = await rec_function(websocket)
#             print(message)

async def rec_function(websocket):
    message = await websocket.recv()
    print("Recieved in Rec function",message)
    return message

# asyncio.get_event_loop().run_until_complete(websocket_client())