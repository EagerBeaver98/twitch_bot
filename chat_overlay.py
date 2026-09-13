import asyncio
import json
from collections import deque
from pathlib import Path
from aiohttp import web

BASE_DIR = Path(__file__).parent
STATIC_CHAT_DIR = BASE_DIR / "chat_overlay"

HISTORY_SIZE = 20  # How many past messages a newly connected overlay sees right away.


class ChatOverlayServer:

    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()  # Holds every connected OBS browser source.
        self.history = deque(maxlen=HISTORY_SIZE)  # Recent messages, for late-joining clients.
        self.runner = None

        self.app = web.Application()
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/ws", self.handle_ws)
        self.app.router.add_static("/static/", path=STATIC_CHAT_DIR, name="static")

    async def handle_index(self, request):
        return web.FileResponse(STATIC_CHAT_DIR / "chat-overlay.html")

    async def handle_ws(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.clients.add(ws)
        print(f"Overlay connected. Total: {len(self.clients)}")

        # Catch the new client up, so a page refresh does not show a blank screen.
        for payload in self.history:
            await ws.send_str(payload)

        try:
            async for _ in ws:
                pass  # The page does not send anything back. We only listen for disconnect.
        finally:
            self.clients.discard(ws)
            print(f"Overlay disconnected. Total: {len(self.clients)}")
        return ws

    async def broadcast(self, username: str, text: str):
        """Send one chat message to every connected overlay page."""
        payload = json.dumps({"username": username, "text": text})
        self.history.append(payload)
        dead_clients = set()
        for ws in self.clients:
            try:
                await ws.send_str(payload)
            except ConnectionResetError:
                dead_clients.add(ws)
        self.clients -= dead_clients

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        print(f"Overlay server ready at http://{self.host}:{self.port}/")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()


if __name__ == "__main__":
    async def demo():
        chat_server = ChatOverlayServer()
        await chat_server.start()
        print("Open the page now. A test message sends every 3 seconds.")
        count = 0
        while True:
            count += 1
            await chat_server.broadcast("test_user", f"Hello, overlay! ({count})")
            await asyncio.sleep(3)
    asyncio.run(demo())