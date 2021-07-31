import psycopg2
import config

"""
database.py: Access and edit database
"""

STATEMENT = """
            SELECT discord_id, users.name as user, builders.user as userid, area, city, county, state FROM (
                SELECT user_id as user, Null as area, Null as city, counties.name as county,
                counties.state as state FROM county_builders
                JOIN counties ON county_builders.county_id = counties.id
                UNION
                SELECT user_id as user, Null as area, cities.name as city, counties.name as county,
                counties.state as state FROM city_builders
                LEFT JOIN cities ON city_builders.city_id = cities.id
                JOIN counties ON cities.county_id = counties.id
                UNION
                SELECT user_id as user, locations.name as area, cities.name as city,
                counties.name as county, counties.state as state FROM location_builders
                LEFT JOIN locations ON location_builders.location_id = locations.id
                LEFT JOIN cities ON locations.city_id = cities.id
                LEFT JOIN counties ON
                CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id)
            AS builders
            JOIN users on builders.user = users.id
            """

connection = None


def get_database():
    global connection

    if connection is None:
        connection = BotDB(config.postgres, config.postgres_user, config.postgres_pass)

    return connection


class BotDB:
    def __init__(self, db, user, passwd):
        # Connect to postgresql database
        self.conn = psycopg2.connect(f"dbname={db} user={user} password={passwd}")
        self.cur = self.conn.cursor()

        print(f"[INFO]: Database: Connected to {db} as {user} successfully")

    def execute(self, query, args):
        """
        Execute custom sql query to insert into database
        :param query: SQL command to be run
        :param args: Args to be inserted
        :return: None
        """
        self.cur.execute(query, args)
        # print("[DEBUG]: " + query + ", " + str(args))
        self.conn.commit()

    def get_query(self, query, args=None):
        """
        Execute custom sql query to get from database
        :param query: SQL command to be run, string type
        :param args: Args to be inserted, iterable type
        :return: SQL results
        """
        self.cur.execute(query, args)
        # print("[DEBUG]: " + query + ", " + str(args))
        return self.cur.fetchall()

    def get_all(self):
        """
        Get all builder info in database
        """
        self.cur.execute(STATEMENT)
        return self.cur.fetchall()

    def get_builders(self, scope, query):
        """
        Get all builders in a certain area
        """
        self.cur.execute(STATEMENT + f" WHERE {scope} = %s", [query])
        return self.cur.fetchall()

    def search_name(self, table, query):
        """
        Get the true name of an area based on a query
        :param table: Table to search in
        :param query: Area to search for
        :return: Areas found LIKE query
        """
        self.cur.execute(f"SELECT name FROM {table} WHERE lower(name) LIKE lower(%s)",
                         ["%%%s%%" % query])
        return self.cur.fetchall()

    def get_user(self, user):
        """
        Get all info on a user
        :param user: discord user id
        :return: database entry
        """
        self.cur.execute(STATEMENT + " WHERE discord_id = %s;", [user])
        return self.cur.fetchall()

    def add_user_id(self, username, discord_id):
        """
        Add a discord id to a user in the database
        :param discord_id: user's discord id
        :param username: username of user to add
        :return: Nones
        """
        self.cur.execute("UPDATE users SET discord_id = %s WHERE name = %s", [discord_id, username])
        self.conn.commit()
