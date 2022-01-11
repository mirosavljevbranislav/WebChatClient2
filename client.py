import asyncio
import websockets


async def hello():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        await websocket.send("Hello world!")
        print(await websocket.recv())

asyncio.run(hello())
