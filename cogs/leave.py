import os
import sys

import discord
from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database


class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()
        self.log_channel = 813642660388143124

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Send a notification when a member in the db leaves
        """
        # Check if user in db
        user_info = self.db.get_user(member.id)

        if user_info:
            channel = self.get_channel(self.log_channel)

            # Send leave notice and all info in db
            channel.send(member.name + " left the server.")
            channel.send(f"[{member.name}]: {user_info}")


def setup(bot):
    bot.add_cog(Leave(bot))
