import os
import sys
import requests

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
            await ctx.send("Usage: search [SCOPE] [QUERY]")
            return

        # Verify correct usage
        elif args[0].lower() not in ["area", "city", "county", "state"]:
            await ctx.send("Invalid search scope. Must be area, city, county, or state.")
            return

        # Separate scope and keywords
        else:
            scope = args[0].lower()
            query = " ".join(args[1:]).capitalize()

        # Relate db tables and scope
        table = {"area": "locations", "city": "cities", "county": "counties"}

        # Search for query in table
        if scope == "state":
            try:
                if len(query) == 2:
                    # Search state abbreviation
                    name, fname = self.db.get_query("SELECT abbr, name FROM states WHERE abbr = %s", [query.upper()])[0]
                else:
                    name, fname = self.db.get_query("SELECT abbr, name FROM states WHERE lower(name) LIKE %s",
                                                    ["%%%s%%" % query.lower()])[0][0]
            except IndexError:
                await ctx.send(f"The state `{query}` does not exist. Please try again.")
                return
        else:
            name = query.capitalize()

        results = self.db.get_builders(scope, name)

        # No exact match
        if not results:
            name = self.db.search_name(table[scope], query)
            # Multiple areas matching search
            if len(name) > 1:
                await ctx.send("Found multiple matches: " + ", ".join([i[0] for i in name]))
                return

            # No areas matching search
            elif len(name) == 0:
                await ctx.send(f"No results found for `{query}`")
                return

            # Try again with corrected name
            else:
                name = name[0][0]
                results = self.db.get_builders(scope, name)

        # No results with corrected name
        if not results:
            await ctx.send(f"No builders found in `{name}`")
            return

        # Get users from query, make description
        if scope == "area":
            description = f"{name}, {results[0][4]} in {results[0][5]} County, {results[0][6]}"
        elif scope == "city":
            description = f"{name} in {results[0][5]} County, {results[0][6]}"
        elif scope == "county":
            description = f"{name} County, {results[0][6]}"
        else:
            description = f"{fname}"

        # Append users to list without duplicates
        users = []
        for item in results:
            # MENTION FUNCTIONALITY - doesn't work as discord only shows cached users as mentions
            # if item[0]:
            #     ping = f"<@{item[0]}>"
            #     if ping not in users:
            #         users.append(ping)
            if item[1] not in users:
                users.append(item[1])

        # Verify allowed length
        if 0 < len(users) < 80:
            # Create and send embed
            embed = discord.Embed(
                title="Search Results", description=description, color=0xb71234)
            # Vertical list of user names
            embed.add_field(name=f"Found {len(users)}:", value="\n".join(users))

            # Add image
            image = self.get_google_img(name)
            if image:
                embed.set_thumbnail(url=image)

            await ctx.send(embed=embed)
        elif len(users) >= 100:
            await ctx.send(f"User list too long: {len(users)} users found")
        else:
            await ctx.send(f"No users found")

    def get_google_img(self, query):
        pass


def setup(bot):
    bot.add_cog(Search(bot))
