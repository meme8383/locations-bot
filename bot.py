import discord
import config
import csv
import psycopg2

from discord.ext import commands
from database import get_database

"""
bot.py: Discord bot to search for discord users in database
Some inspiration taken from RoboDanny: https://github.com/Rapptz/RoboDanny
"""

__author__ = "Eduard Tanase"
__version__ = "1.0.0"


PREFIX = '~'

COGS = [
    "cogs.leave",
    "cogs.search",
    "cogs.users"
]


class MembersBot(commands.Bot):
    def __init__(self):
        # Configure discord bot
        intents = discord.Intents(
            guilds=True,
            members=True,
            messages=True
        )
        super().__init__(command_prefix=PREFIX, intents=intents)

        # Get bot ID
        self.client_id = config.client_id

        # Connect to postgresql database with credentials in config.py
        self.db = get_database()

        self.add_commands()

        for cog in COGS:
            self.load_extension(cog)

        self.log_channel = config.log_channel_id

    async def on_ready(self):
        # Print info to console
        print(f'[INFO]: Ready: {self.user} (ID: {self.user.id})')

    def add_commands(self):
        @self.command(name="ping", pass_context=True)
        async def ping(ctx):
            """
            Pings the bot. Also shows latency
            :param ctx: Command invoke context
            :return: None
            """
            print(f"[DEBUG]: Pinged by {ctx.message.author}")
            await ctx.send(f"Pong! Latency: {int(self.latency * 1000)} ms")


if __name__ == '__main__':
    bot = MembersBot()
    bot.run(config.token)
