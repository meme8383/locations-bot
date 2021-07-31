# Locations bot

Discord bot + database for BTESW

Some inspiration taken from https://github.com/Rapptz/RoboDanny

## Features

### Search Command
![Search Command](https://i.gyazo.com/37f50b74c0e01c4a5853ddbea6f300a9.png)

### Userinfo Command
![Userinfo Command](https://i.gyazo.com/659e6a9d4af244eee8bf260e92e9edd7.png)

### Leave Notifications
These only activate when the user is in the database, and they show all of the user's locations similar to the userinfo command.
![Leave Notifications](https://i.gyazo.com/a280891037d1751cfbd9dc6e892c22af.png)

## Files

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