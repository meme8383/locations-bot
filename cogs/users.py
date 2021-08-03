import os
import sys
import DiscordUtils
from cogs.search import Search

import discord
from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()
        self.search = Search(self.bot)

    @commands.command(name="userinfo", pass_context=True)
    async def userinfo(self, ctx):
        """
        Get info from database on user
        :param ctx: Command invoke context
        :returns: None
        """
        # Get user
        try:
            user = ctx.message.mentions[0]
        except IndexError:
            user = ctx.message.author

        locations = []

        # Get user id, send message if not in db
        try:
            user_id = self.db.get_query("SELECT id FROM users WHERE discord_id = %s", [user.id])[0]
        except IndexError:
            ctx.send(f"`{user}` could not be found.")
            return

        for area in self.db.get_query("SELECT location_id FROM location_builders WHERE user_id = %s", [user_id]):
            locations.append(self.search.get_description("area", area[0]))
        for city in self.db.get_query("SELECT city_id FROM city_builders WHERE user_id = %s", [user_id]):
            locations.append(self.search.get_description("city", city[0]))
        for county in self.db.get_query("SELECT county_id FROM county_builders WHERE user_id = %s", [user_id]):
            locations.append(self.search.get_description("county", county[0]))

        if locations:
            # Create embed
            embed = discord.Embed(color=0xffc324)

            embed.set_author(name=user.name + "'s locations:",
                             icon_url=user.avatar_url)

            embed.add_field(name=f"Found {len(locations)}:", value="\n".join(locations))

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No data found for `{user}`")

    @commands.command(name="add-ids", pass_context=True)
    async def add_ids(self, ctx):
        """
        Adds discord id's of all users to database
        """
        if ctx.message.author.guild_permissions.manage_roles:
            await ctx.send("Adding id's...")
            added = 0
            skipped = 0
            changed = 0
            okay = 0

            async with ctx.typing():
                for user in ctx.guild.members:
                    info = self.db.get_query("SELECT * FROM users WHERE name = %s", [str(user)])
                    if info:
                        if not info[0][2]:
                            self.db.add_user_id(str(user), user.id)
                            added += 1
                        elif info[0][2] != user.id:
                            self.db.add_user_id(str(user), user.id)
                            changed += 1
                        else:
                            okay += 1
                    else:
                        skipped += 1

            message = f"Added ID's.\nAdded: {added}\nChanged: {changed}\nOkay: {okay}\nSkipped: {skipped}"
            await ctx.send(message)
            print(message)
        else:
            await ctx.send("Insufficient permissions")

    @commands.command(name="unknown-users", pass_context=True)
    async def unknown_users(self, ctx):
        """
        Lists all users with no ID in the database
        :param ctx: Command invoke context
        :return: None
        """
        users = self.db.get_query("SELECT name FROM users WHERE discord_id IS NULL", [])

        embeds = []
        for i in range(0, len(users), 20):
            embed = discord.Embed(title="Unknown users", color=0xb71234)

            # Page numbers
            page = int(i/20 + 1)
            total = int(len(users)/20) + 1

            # Vertical list of user names
            try:
                user_list = "\n".join([j[0] for j in users[i:i+20]])
            except IndexError:
                user_list = "\n".join([j[0] for j in users[i:]])

            embed.add_field(name=f"Found {len(users)} (page {page} of {total}):", value=user_list)

            embeds.append(embed)

        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        await paginator.run(embeds)


def setup(bot):
    bot.add_cog(Users(bot))
