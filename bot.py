import discord
import config
import csv
import psycopg2

from discord.ext import commands
from database import BotDB

"""
bot.py: Discord bot to search for discord users in database
"""

__author__ = "Eduard Tanase"
__version__ = "0.0.1"


PREFIX = '~'


class MembersBot(commands.Bot):
    def __init__(self):
        # Configure discord bot
        super().__init__(command_prefix=PREFIX)

        # Get bot ID
        self.client_id = config.client_id

        # Connect to postgresql database with credentials in config.py
        self.db = BotDB(config.postgres, config.postgres_user, config.postgres_pass)

        self.add_commands()

    async def on_ready(self):
        # Print info to console
        print(f'[INFO]: Ready: {self.user} (ID: {self.user.id})')

    @property
    def config(self):
        # Config file
        return __import__('config')

    def add_commands(self):
        @self.command(name="search", pass_context=True)
        async def search(ctx, *args):
            """
            Searches database for user based on area
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
                query = " ".join(args[1:])

            # Search for query in table
            if scope == "area":
                name = self.db.search_name("locations", query)
            elif scope == "city":
                name = self.db.search_name("cities", query)
            elif scope == "county":
                name = self.db.search_name("counties", query)
            elif scope == "state":
                if len(query) == 2:
                    # Search state abbreviation
                    name = self.db.get_query("SELECT abbr FROM states WHERE abbr = %s", [query.upper()])
                else:
                    name = self.db.get_query("SELECT abbr FROM states WHERE lower(name) LIKE %s",
                                             ["%%%s%%" % query.lower()])

            # Multiple areas matching search
            if len(name) > 1:
                await ctx.send("Found multiple matches:")
                # TODO: List of matches
                return

            # No areas matching search
            if len(name) == 0:
                await ctx.send("No results found")
                return

            # Get users from query, make description
            if scope == "area":
                results = self.db.get_area(name[0][0])
                description = f"{name[0][0]}, {results[0][3]} in {results[0][4]} County, {results[0][5]}"
            elif scope == "city":
                results = self.db.get_city(name[0][0])
                description = f"{name[0][0]} in {results[0][4]} County, {results[0][5]}"
            elif scope == "county":
                results = self.db.get_county(name[0][0])
                description = f"{name[0][0]} County, {results[0][5]}"
            elif scope == "state":
                results = self.db.get_state(name[0][0])
                description = f"{name[0][0]}"

            # Append users to list without duplicates
            users = []
            for item in results:
                if item[0] not in users:
                    users.append(item[0])

            # Verify allowed length
            if 0 < len(users) < 100:
                # Create and send embed
                embed = discord.Embed(title="Search Results", description=description, color=0xff0000)
                # Vertical list of user names
                embed.add_field(name=f"Found {len(users)}:", value="\n".join(users))
                await ctx.send(embed=embed)
            elif len(users) >= 100:
                await ctx.send(f"User list too long: {len(users)} users found")
            else:
                await ctx.send(f"No users found")


if __name__ == '__main__':
    bot = MembersBot()
    bot.run(config.token)
