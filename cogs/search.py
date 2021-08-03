import os
import sys
import requests
import asyncio
import DiscordUtils

import discord
from discord.ext import commands
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()

    @commands.command(name="search", pass_context=True)
    async def search(self, ctx, *args):
        """
        Searches database for users based on area
        :param ctx: Command invoke context
        :param args: Search scope + Search keywords
        :return: None
        """
        # Check for arguments
        if len(args) < 2:
            await ctx.send("Usage: search <area:city:county:state> <query>")
            return

        # Verify correct usage
        elif args[0].lower() not in ["area", "city", "county", "state"]:
            await ctx.send("Invalid search scope. Must be area, city, county, or state.")
            return

        # Separate scope and keywords
        else:
            scope = args[0].lower()
            query = " ".join(args[1:]).title()

        # Relate db tables and scope
        table = {"area": "locations", "city": "cities", "county": "counties"}

        # Get ID for search
        if scope == "state":
            try:
                if len(query) == 2:
                    # Search state abbreviation
                    id, name = self.db.get_query("SELECT abbr, name FROM states WHERE abbr = %s",
                                                 [query.upper()])[0]
                else:
                    # Search state name
                    id, name = self.db.get_query("SELECT abbr, name FROM states WHERE lower(name) LIKE %s",
                                                 ["%%%s%%" % query.lower()])[0]
            except IndexError:
                await ctx.send(f"The state `{query}` does not exist. Please try again.")
                return
        else:
            # Search for exact match
            search = self.db.get_query(f"SELECT id, name FROM {table[scope]} WHERE name = %s",
                                       [query])
            if not search:
                # Search for close matches
                search = self.db.get_query(f"SELECT id, name FROM {table[scope]} WHERE name LIKE %s",
                                           ["%%%s%%" % query])
            if 1 < len(search) < 10:
                # Multiple matches, get list of info for each result
                info = []
                for i in search:
                    if scope == "area":
                        info.append(self.db.area_info(i[0]))
                    elif scope == "city":
                        info.append(self.db.city_info(i[0]))
                    else:
                        info.append(self.db.county_info(i[0]))

                # Reactions for list of matches
                reactions = [str(i + 1) + '\N{combining enclosing keycap}' for i in range(len(info))]

                # Create embed with results
                embed = discord.Embed(title="Multiple matches found", color=0xffc324)
                embed.add_field(name="React to select your choice:",
                                value="\n".join([f"{reactions[i]} " + self._get_description(scope, search[i][0])
                                                 for i in range(len(search))]))
                msg = await ctx.send(embed=embed)

                # Add reactions
                for i in reactions:
                    await msg.add_reaction(i)

                # Check valid reaction
                def check(reaction, user):
                    return str(reaction) in reactions and user != self.bot.user

                # Wait for user reaction
                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=300.0, check=check)
                except asyncio.TimeoutError:
                    return

                # Get ID, name of selection
                id, name = search[int(str(reaction)[0]) - 1]

            elif len(search) >= 10:
                await ctx.send(f"{len(search)} matches found. Please narrow your search.")
                return
            elif not search:
                # No matches
                await ctx.send(f"No results found for `{query}`")
                return
            else:
                # One match
                id, name = search[0]

        # Get builders
        results = self.db.get_builders_by_id(scope, id)

        # No results with corrected name
        if not results:
            await ctx.send(f"No builders found in `{name}`")
            return

        # Make description
        description = self._get_description(scope, id)

        # Append users to list without duplicates
        users = []
        no_id = False
        for item in results:
            # Get user name, add * if no ID found
            if item[0]:
                user = item[1]
            else:
                user = item[1] + '*'
                no_id = True
            if user not in users:
                user = user.replace('*', '\*')
                user = user.replace('_', '\_')
                users.append(user)

        # No users found
        if not users:
            await ctx.send(f"No users found")
            return

        # Paginate for 20 users
        embeds = []
        per_page = 20

        if len(users) > 20:
            for i in range(0, len(users), per_page):
                embed = discord.Embed(title="Search Results", description=description, color=0xb71234)
                # Add * note
                if no_id:
                    embed.set_footer(text="*No ID found for user")

                # Page numbers
                page = int(i/per_page + 1)
                total = int(len(users)/per_page) + 1

                # Vertical list of user names
                try:
                    user_list = "\n".join(users[i:i + per_page])
                except IndexError:
                    user_list = "\n".join(users[i:])

                embed.add_field(name=f"Found {len(users)} (page {page} of {total}):", value=user_list)
                embeds.append(embed)

            paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx, remove_reactions=True)
            await paginator.run(embeds)
        else:
            embed = discord.Embed(title="Search Results", description=description, color=0xb71234)
            # Add * note
            if no_id:
                embed.set_footer(text="*No ID found for user")

            # Vertical list of user names
            embed.add_field(name=f"Found {len(users)}:", value="\n".join(users))
            await ctx.send(embed=embed)

        # # Create embed
        # embed = discord.Embed(
        #     title="Search Results", description=description, color=0xb71234)
        # # Vertical list of user names
        # embed.add_field(name=f"Found {len(users)}:", value="\n".join(users))
        #
        # # Add * note
        # if no_id:
        #     embed.set_footer(text="*No ID found for user")
        #
        # # Add image
        # image = self.get_google_img(name)
        # if image:
        #     embed.set_thumbnail(url=image)
        #
        # try:
        #     await ctx.send(embed=embed)
        # except discord.HTTPException as ex:
        #     if ex.status != 400 or ex.code != 50035:
        #         return
        #     await ctx.send(f"User list too long: {len(users)} users found.")
        #     return

    def get_google_img(self, query):
        pass

    def _get_description(self, scope, id):
        """
        Get a detailed description of an area
        :param scope: Area, city, county, or state
        :param id: ID of the location
        :return: String describing the location
        """
        if scope == "area":
            info = self.db.area_info(id)
            return f"{info[0]}, {info[1]} in {info[2]} County, {info[3]}"
        elif scope == "city":
            info = self.db.city_info(id)
            return f"{info[0]} in {info[1]} County, {info[2]}"
        elif scope == "county":
            info = self.db.county_info(id)
            return f"{info[0]} County, {info[1]}"
        else:
            info = self.db.get_query("SELECT name FROM states WHERE abbr = %s", [id])
            return f"{info[0][0]}"


def setup(bot):
    bot.add_cog(Search(bot))
