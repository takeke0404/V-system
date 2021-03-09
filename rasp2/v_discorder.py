import discord
import asyncio
import threading
import time
import os


class DiscordClient(discord.Client):

    def __init__(self):
        super().__init__()


    async def on_message(self, message):
        # print("v_discorder on_message", message.content)
        if message.guild is None and not message.author.bot:
            await message.author.send(message.content[ : : -1])


    async def send_dm(self, user_id, message):
        print("v_discorder send_dm:", message)
        user = await self.fetch_user(user_id)
        if user.dm_channel is None:
            await user.create_dm()
        await user.send(message)


class Manager(threading.Thread):

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

        loop = self.client.loop
        loop.create_task(self.client.start(self.token))
        threading.Thread(target=loop.run_forever())

        # Linux では Error: set_wakeup_fd only works in main thread
        # self.client.run(self.token)


    def send_dm(self, user_id, message):
        asyncio.run_coroutine_threadsafe(self.client.send_dm(user_id, message), self.client.loop)
