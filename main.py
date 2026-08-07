from dotenv import load_dotenv
import os
from pathlib import Path
import twitchio
from twitchio import eventsub
from twitchio.ext import commands
import json
from datetime import datetime, timedelta
import tts
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

cooldown_tracker = {}

TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
TWITCH_NICK = os.getenv("TWITCH_NICK")
TTS_COOLDOWN_SECONDS = 300
TTS_FOLDER = Path("./audio")

TTS_FOLDER.mkdir(exist_ok=True)


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            # token=TWITCH_TOKEN,
            prefix='!',
            # initial_channels=[TWITCH_CHANNEL],
            # nick=os.getenv("TWITCH_NICK"),
            owner_id=os.getenv("TWITCH_OWNER_ID"),
            client_id=os.getenv("TWITCH_CLIENT_ID"),
            client_secret=os.getenv("TWITCH_CLIENT_SECRET"),
            bot_id=os.getenv("TWITCH_BOT_ID")
        )
        print(f"Bot initialized with channel: {TWITCH_CHANNEL}")

    
    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload):
        # Called when a user completes the OAuth flow in their browser.
        # We store the token and subscribe to chat on their channel.
        await self.add_token(payload.access_token, payload.refresh_token)
        await self.join_channels([TWITCH_CHANNEL])

    async def setup_hook(self) -> None:

        payload = eventsub.ChatMessageSubscription(
            broadcaster_user_id=os.getenv("TWITCH_OWNER_ID"),
            user_id=os.getenv("TWITCH_BOT_ID"),
        )
        # subscribe_websocket opens a WebSocket connection to Twitch EventSub.

        await self.subscribe_websocket(payload=payload)
        logging.info("Subscribed to chat messages for channel %s", os.getenv("TWITCH_OWNER_ID"))

        await self.add_component(TTSHandler(self))


    async def event_ready(self):
        print(f"Bot logged in as: {os.getenv('TWITCH_BOT_ID')}")
        print(f"Connected to channel: {TWITCH_CHANNEL}")
        print("Listening for messages...")


class TTSHandler(commands.Component):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tts')
    async def tts_command(self, ctx: commands.Context) -> None:
        user = ctx.author.name
        now = datetime.now()

        if user in cooldown_tracker:
            last_time = cooldown_tracker[user]
            if now - last_time < timedelta(seconds=TTS_COOLDOWN_SECONDS):
                remaining = TTS_COOLDOWN_SECONDS - (now - last_time).seconds
                await ctx.send(f"@{user}, please wait {remaining} seconds before using TTS again.")
                return
        text = ctx.message.text[len("!tts "):].strip()

        if not text:
            await ctx.send(f"@{user}, please provide text for TTS.")
            return


        await tts.edgeTTS(text)

        

        cooldown_tracker[user] = now

    @commands.command(name='ping')
    async def ping_command(self, ctx: commands.Context) -> None:
        await ctx.send("pong!")

async def main():
    print("Starting Twitch Bot...")
    print(f"Channel: {TWITCH_CHANNEL}")
    bot = TwitchBot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
