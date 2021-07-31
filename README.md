# Locations bot

Discord bot + database for BTESW

Some inspiration taken from https://github.com/Rapptz/RoboDanny

### config.py
To run the bot, create a file named `config.py` with the following format:
```
client_id = ""
token = ""
postgres = ""
postgres_user = ""
postgres_pass = ""
log_channel_id = 
```

### SQL
The `btesw_schema` file is a schema-only backup of the psql database. Restore this file and use `converter.py` to insert the data.