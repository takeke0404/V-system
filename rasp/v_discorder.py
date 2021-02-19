import discord
import asyncio
import threading
import time
import os


class DiscordClient(discord.Client):


    def __init__(self):
        super().__init__()


    async def send_dm(self, user_id, message):
        user = await self.fetch_user(user_id)
        await user.send(message)


class DiscordClientThread(threading.Thread):


    def __init__(self):
        super().__init__()

        discord_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "discord.key")
        if os.path.isfile(discord_key_path):
            with open(discord_key_path, "r") as key_file:
                self.token = key_file.readline().splitlines()[0]
        else:
            raise Exception("Discorder: " + discord_key_path + " does not exist.")

        self.client = DiscordClient()


    def run(self):
        time.sleep(10)
        self.loop = asyncio.new_event_loop()
        try:
            self.loop.run_until_complete(self.client.start(self.token))
        finally:
            self.loop.close()


class Manager():


    def __init__(self):
        self.discorder = DiscordClientThread()


    def start(self):
        self.discorder.start()


    def send_dm(self, user_id, message):
        asyncio.run_coroutine_threadsafe(self.discorder.client.send_dm(user_id, message), self.discorder.loop)
