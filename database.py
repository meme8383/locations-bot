import psycopg2

"""
database.py: Access and edit database
"""


class BotDB:
    def __init__(self, db, user, passwd):
        # Connect to postgresql database
        self.conn = psycopg2.connect(f"dbname={db} user={user} password={passwd}")
        self.cur = self.conn.cursor()

    def execute(self, query, args):
        """
        Execute custom sql query to insert into database
        :param query: SQL command to be run, string type
        :param args: Args to be inserted, iterable type
        :return: None
        """
        self.cur.execute(query, args)
        print("[DEBUG]: " + query + ", " + str(args))
        self.conn.commit()

    def get_query(self, query, args=None):
        """
        Execute custom sql query to get from database
        :param query: SQL command to be run, string type
        :param args: Args to be inserted, iterable type
        :return: SQL results
        """
        self.cur.execute(query, args)
        print("[DEBUG]: " + query + "," + str(args))
        return self.cur.fetchall()

    def get_all(self):
        """
        Get all builder info in database
        """
        self.cur.execute("""
                         SELECT users.name as user, builders.user as userid, areas, city, county, state FROM (
                             SELECT user_id as user, Null as areas, Null as city, counties.name as county,
                             counties.state as state FROM county_builders
                             JOIN counties ON county_builders.county_id = counties.id
                             UNION
                             SELECT user_id as user, Null as areas, cities.name as city, counties.name as county,
                             counties.state as state FROM city_builders
                             LEFT JOIN cities ON city_builders.city_id = cities.id
                             JOIN counties ON cities.county_id = counties.id
                             UNION
                             SELECT user_id as user, locations.name as areas, cities.name as city,
                             counties.name as county, counties.state as state FROM location_builders
                             LEFT JOIN locations ON location_builders.location_id = locations.id
                             LEFT JOIN cities ON locations.city_id = cities.id
                             LEFT JOIN counties ON
                             CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id)
                         AS builders
                         JOIN users on builders.user = users.id;
                         """)

        return self.cur.fetchall()

    def get_area(self, query):
        """
        Get all users working in a location
        :param query: Search for specific location
        :return: SQL results
        """
        self.cur.execute("""
                         SELECT users.name as user, builders.user as userid, areas, city, county, state FROM (
                             SELECT user_id as user, locations.name as areas, cities.name as city,
                             counties.name as county, counties.state as state FROM location_builders
                             LEFT JOIN locations ON location_builders.location_id = locations.id
                             LEFT JOIN cities ON locations.city_id = cities.id
                             LEFT JOIN counties ON
                             CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id
                             WHERE locations.name = %s)
                         AS builders
                         JOIN users on builders.user = users.id;
                         """, [query])

        return self.cur.fetchall()

    def get_city(self, query=None):
        """
        Get all users working in a city
        :param query: Search for specific city
        :return: SQL results
        """
        self.cur.execute("""
                         SELECT users.name as user, builders.user as userid, areas, city, county, state FROM (
                             SELECT user_id as user, Null as areas, cities.name as city, counties.name as county,
                             counties.state as state FROM city_builders
                             LEFT JOIN cities ON city_builders.city_id = cities.id
                             JOIN counties ON cities.county_id = counties.id
                             UNION
                             SELECT user_id as user, locations.name as areas, cities.name as city,
                             counties.name as county, counties.state as state FROM location_builders
                             LEFT JOIN locations ON location_builders.location_id = locations.id
                             LEFT JOIN cities ON locations.city_id = cities.id
                             LEFT JOIN counties ON
                             CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id)
                         AS builders
                         JOIN users on builders.user = users.id
                         WHERE city = %s;
                         """, [query])

        return self.cur.fetchall()

    def get_county(self, query=None):
        """
        Get all users working in a county
        :param query: Search for specific county
        :return: SQL results
        """
        self.cur.execute("""
                         SELECT users.name as user, builders.user as userid, areas, city, county, state FROM (
                             SELECT user_id as user, Null as areas, Null as city, counties.name as county,
                             counties.state as state FROM county_builders
                             JOIN counties ON county_builders.county_id = counties.id
                             UNION
                             SELECT user_id as user, Null as areas, cities.name as city, counties.name as county,
                             counties.state as state FROM city_builders
                             LEFT JOIN cities ON city_builders.city_id = cities.id
                             JOIN counties ON cities.county_id = counties.id
                             UNION
                             SELECT user_id as user, locations.name as areas, cities.name as city,
                             counties.name as county, counties.state as state FROM location_builders
                             LEFT JOIN locations ON location_builders.location_id = locations.id
                             LEFT JOIN cities ON locations.city_id = cities.id
                             LEFT JOIN counties ON
                             CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id)
                         AS builders
                         JOIN users on builders.user = users.id
                         WHERE county = %s;
                         """, [query])

        return self.cur.fetchall()

    def get_state(self, query=None):
        """
        Get all users working in a state
        :param query: Search for specific state
        :return: SQL results
        """
        self.cur.execute("""
                         SELECT users.name as user, builders.user as userid, areas, city, county, state FROM (
                             SELECT user_id as user, Null as areas, Null as city, counties.name as county,
                             counties.state as state FROM county_builders
                             JOIN counties ON county_builders.county_id = counties.id
                             UNION
                             SELECT user_id as user, Null as areas, cities.name as city, counties.name as county,
                             counties.state as state FROM city_builders
                             LEFT JOIN cities ON city_builders.city_id = cities.id
                             JOIN counties ON cities.county_id = counties.id
                             UNION
                             SELECT user_id as user, locations.name as areas, cities.name as city,
                             counties.name as county, counties.state as state FROM location_builders
                             LEFT JOIN locations ON location_builders.location_id = locations.id
                             LEFT JOIN cities ON locations.city_id = cities.id
                             LEFT JOIN counties ON
                             CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id)
                         AS builders
                         JOIN users on builders.user = users.id
                         WHERE state = %s;
                         """, [query])

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


# class BotDB:
#     """
#     Use CSV instead of database
#     """
#     def __init__(self, directory):
#         self.locations = []
#
#         with open(directory + "/Location List.csv", "r", encoding="utf8") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 self.locations.append(row)
#
#         print("[INFO]: Ready: Location List.csv")
#
#     def search(self, alias, keyword):
#         try:
#             return [i for i in self.locations if keyword.lower() in i[alias].lower()]
#         except KeyError:
#             return None
