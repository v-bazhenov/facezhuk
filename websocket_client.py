import asyncio

import websockets

url = 'ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NzIyODI2NDYsImV4cCI6MTY3MjM3MjY0NiwidXNlciI6eyJlbWFpbCI6ImpvbkBleGFtcGxlLmNvbSIsInVzZXJuYW1lIjoiam9uIn19.17jwwJvG62Zt6BLULf82f4vKgdrqxHcWUD_2LS1P3po'

async def listen():
    async with websockets.connect(url) as websocket:
        while True:
            message = await websocket.recv()
            print(f"< {message}")

asyncio.get_event_loop().run_until_complete(listen())
