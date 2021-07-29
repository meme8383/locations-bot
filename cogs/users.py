import os
import sys

import discord
from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()

    @commands.command(name="userinfo", pass_context=True)
    async def userinfo(self, ctx):
        """
        Get info from database on user
        """
        # Get user
        try:
            user = ctx.message.mentions[0]
        except IndexError:
            user = ctx.message.author

        # Get info from db
        info = self.db.get_user(user.id)

        if info:
            print(info)
            # Create embed
            embed = discord.Embed(color=discord.Color.red())

            embed.set_author(
                name=user.name + "'s locations:", icon_url=user.avatar_url)

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

            await ctx.send(embed=embed)
        else:
            await ctx.send("No user found: " + user.name)

    @commands.command(name="add_ids", pass_context=True)
    async def add_ids(self, ctx):
        """
        Adds discord id's of all users to database
        """
        if ctx.message.author.guild_permissions.manage_roles:
            await ctx.send("Adding id's...")
            count = 0
            for user in ctx.guild.members:
                if self.db.execute("SELECT * FROM users WHERE name = %s", [user.name + "#" + user.discriminator]):
                    self.db.add_user_id(user.name + "#" + user.discriminator, user.id)
                    count += 1
            await ctx.send(f"Updated {count} entries.")
        else:
            await ctx.send("Insufficient permissions")


def setup(bot):
    bot.add_cog(Users(bot))
