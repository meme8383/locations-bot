import os
import sys

import discord
from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database
from config import log_channel_id


class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()
        self.log_channel = log_channel_id

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Send a notification when a member in the db leaves
        :param member: User who left
        :returns: None
        """

        # Check if user in db
        info = self.db.get_user(member.id)

        if info:
            channel = self.bot.get_channel(self.log_channel)

            # Send leave notice and all info in db
            embed = discord.Embed(title=f"{member} has left the server", color=0xffc324)
            embed.set_thumbnail(url=member.avatar_url)

            locations = [i for i in info if i[3] is not None]
            cities = [i for i in info if i[4] is not None]
            counties = [i for i in info if i[5] is not None]

            if locations:
                embed.add_field(
                    name="Location",
                    value='\n'.join([i[3] for i in locations]),
                    inline=True
                )
            if cities:
                embed.add_field(
                    name="City",
                    value='\n'.join([i[4] for i in cities]),
                    inline=True
                )
            if counties:
                embed.add_field(
                    name="County/State",
                    value='\n'.join([i[5] + " County, " + i[6] for i in counties]),
                    inline=True
                )

            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Leave(bot))
