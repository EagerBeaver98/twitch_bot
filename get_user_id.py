import asyncio
import twitchio

CLIENT_ID = "0eaaimvqpdxgn807oimbmgk589f4dm"
CLIENT_SECRET = "6kavxpksynm3ljxp89hbxo1qtsvbqb"

async def main():
    async with twitchio.Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET) as client:
        await client.login()
        # Replace with your real usernames
        users = await client.fetch_users(logins=["eagerbotver98", "eagerbeaver98"])
        for u in users:
            print(f"{u.name} -> {u.id}")

asyncio.run(main())