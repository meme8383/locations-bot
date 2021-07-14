# Locations bot
#### Video Demo: <url>
### Description:
A Discord bot for searching for users in a database of builders for the BTE Project
https://buildtheearth.net/bte-southwest

This bot can be used to search for builders in certain locations, whether these are locations,
cities, counties, or states. This is useful for keeping track of where people are building and who each regional lead
needs to monitor. The user list can also be used to plan events. Other features include getting information on
where a specific person is building and what collaborations exist.

### database.py
This file includes the BotDB class, which has various methods to access and edit data in the postgresql database.
bot.py routes all SQL queries through this file. Separating the database allows for organization and for control over
the asyncio pool.

### converter.py
I used this file to convert all the old csv files into a more efficient SQL database. It takes one file and contains
functions to create each table in the relational database. The functions to be run must be added to the run statement.

### config.py
This file contains all the private info needed to run the bot. To run the bot, you must create a config.py file and
include the following information:
`client_id = ""
token = ""
postgres = ""
postgres_user = ""
postgres_pass = ""
`

### bot.py
This file contains the actual discord bot and launcher. This file initializes the bot and connects to discord, as well
as reading the information in config.py. There is a search command, which searches the database using database.py and
sends an embed containing a list of users found in the search. Future versions could use cogs to separate the commands
and the bot, as well as containing a custom help command.