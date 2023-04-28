"""
PYTHON WEBSOCKET SERVER FOR ASYNC REQUEST RESPONSE
"""

import asyncio
import websockets

connected = set()
async def handler(websocket):
    """
    handles the message in the websocket sent by client
    """
    connected.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            print("Message : ", message)
            for client in connected:
                await client.send(message)

    except Exception as error:
        raise Exception(error)
     
    finally:
        connected.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("running ...")
        await asyncio.Future()

""" Runs the instance forever """
asyncio.run(main())