import os
import sys

import discord
from discord.ext import commands

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
        :param ctx: message context
        :param args: search scope, search keywords
        :return: exit code
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
            if len(query) == 2:
                # Search state abbreviation
                name = self.db.get_query("SELECT abbr FROM states WHERE abbr = %s", [query.upper()])
            else:
                name = self.db.get_query("SELECT abbr FROM states WHERE lower(name) LIKE %s",
                                         ["%%%s%%" % query.lower()])
        else:
            name = self.db.search_name(table[scope], query)

        # Multiple areas matching search
        if len(name) > 1:
            await ctx.send("Found multiple matches: " + ", ".join(name))
            return
        else:
            name = name[0][0]

        # No areas matching search
        if len(name) == 0:
            await ctx.send("No results found")
            return

        results = self.db.get_builders(scope, query)

        # Get users from query, make description
        if scope == "area":
            description = f"{name}, {results[0][3]} in {results[0][4]} County, {results[0][5]}"
        elif scope == "city":
            description = f"{name} in {results[0][4]} County, {results[0][5]}"
        elif scope == "county":
            description = f"{name} County, {results[0][5]}"
        else:
            description = f"{name}"

        # Append users to list without duplicates
        users = []
        for item in results:
            if item[0] not in users:
                users.append(item[0])

        # Verify allowed length
        if 0 < len(users) < 100:
            # Create and send embed
            embed = discord.Embed(
                title="Search Results", description=description, color=0xff0000)
            # Vertical list of user names
            embed.add_field(name=f"Found {len(users)}:", value="\n".join(users))
            await ctx.send(embed=embed)
        elif len(users) >= 100:
            await ctx.send(f"User list too long: {len(users)} users found")
        else:
            await ctx.send(f"No users found")


def setup(bot):
    bot.add_cog(Search(bot))
