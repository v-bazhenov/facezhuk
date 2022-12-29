import asyncio

import websockets

url = 'ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NzIxNTg0OTQsImV4cCI6MTY3MjI0ODQ5NCwidXNlciI6eyJlbWFpbCI6Im1pa2VAZXhhbXBsZS5jb20iLCJ1c2VybmFtZSI6Im1pa2UifX0.hoPZVFH0kTU3ne4WP-yn34zDuWAivg6TYumLpBzyVb0'

async def listen():
    async with websockets.connect(url) as websocket:
        while True:
            message = await websocket.recv()
            print(f"< {message}")

asyncio.get_event_loop().run_until_complete(listen())
