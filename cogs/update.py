import os
import sys
import datetime

import discord
from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database


class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        # Try to fetch user id from db
        try:
            user = self.db.get_query("SELECT id FROM users WHERE discord_id = %s", [before.id])[0][0]
        except IndexError:
            return

        # If user changed name, insert change
        if str(before) != str(after):
            self.db.execute("INSERT INTO name_changes (user_id, before, after, datetime) VALUES (%s, %s, %s, %s)",
                            [user, str(before), str(after), datetime.datetime.now(datetime.timezone.utc)])
            self.db.execute("UPDATE users SET name = %s WHERE discord_id = %s", [str(after), after.id])


def setup(bot):
    bot.add_cog(Update(bot))
