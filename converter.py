import csv
import psycopg2
import config
import sys

"""
converter.py: Convert data from CSV to SQL
"""

cur = None
conn = None


def main():
    global cur, conn

    if not sys.argv[1]:
        print("Usage: converter.py filename")
        return 1

    try:
        f = open(sys.argv[1])
        f.close()
    except FileNotFoundError:
        print("File could not be found")
        return 1
    
    conn = psycopg2.connect(
        f"dbname={config.postgres} user={config.postgres_user} password={config.postgres_pass}"
    )

    cur = conn.cursor()

    # Call function below
    update_database(sys.argv[1])

    conn.commit()

    cur.close()
    conn.close()


def counties_from_wiki(filename, state):
    with open(filename, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["County"].split(" ")
            try:
                name.remove("County")
            except ValueError:
                pass
            cur.execute("INSERT INTO counties (name, state) VALUES (%s, %s)",
                        [' '.join(name), state])


def update_database(filename):
    """
    Update all info in database
    """
    cities = []
    areas = []
    users = []
    location_builders = []
    city_builders = []
    county_builders = []
    stats = {}

    # TODO: Reduce redundancy

    with open(filename, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:

            # Users
            builders = row["Members Planning to Build/Currently Building There"].split(", ")
            for user in builders:
                if user not in users:
                    users.append(user)

            # Areas
            if row["Specific Buildings/Areas"]:
                area = (row["Specific Buildings/Areas"], row["City"] if row["City"] else None, row["County"])
                if area not in areas:
                    areas.append(area)

                for user in builders:
                    build = (user, area)
                    if build not in location_builders:
                        location_builders.append(build)

            # Cities
            if row["City"]:
                city = (row["City"], row["County"])
                if city not in cities:
                    cities.append(city)

                if not row["Specific Buildings/Areas"]:
                    for user in builders:
                        build = (user, city)
                        if build not in city_builders:
                            city_builders.append(build)

            # County builders
            if not row["Specific Buildings/Areas"] and not row["City"]:
                for user in builders:
                    build = (user, row["County"])
                    if build not in county_builders:
                        county_builders.append(build)

    # Update location builders
    cur.execute("""SELECT users.name, locations.name as area, cities.name as city, counties.name as county,
                counties.state as state FROM location_builders
                LEFT JOIN locations ON location_builders.location_id = locations.id
                LEFT JOIN cities ON locations.city_id = cities.id
                LEFT JOIN counties ON
                CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id
                JOIN users on location_builders.user_id = users.id""")

    db = [(i[0], (i[1], i[2], i[3])) for i in cur.fetchall()]

    new_lb = [i for i in location_builders if i not in db]
    old_lb = [i for i in db if i not in location_builders]

    stats["lb_added"] = len(new_lb)
    stats["lb_removed"] = len(old_lb)

    # Update city builders
    cur.execute("""SELECT users.name, cities.name as city, counties.name as county,
                counties.state as state FROM city_builders
                LEFT JOIN cities ON city_builders.city_id = cities.id
                LEFT JOIN counties ON cities.county_id = counties.id
                JOIN users on city_builders.user_id = users.id""")

    db = [(i[0], (i[1], i[2])) for i in cur.fetchall()]

    new_cib = [i for i in city_builders if i not in db]
    old_cib = [i for i in db if i not in city_builders]

    stats["cib_added"] = len(new_cib)
    stats["cib_removed"] = len(old_cib)

    # Update county builders
    cur.execute("""SELECT users.name, counties.name as county, counties.state as state FROM county_builders
                LEFT JOIN counties ON county_builders.county_id = counties.id
                JOIN users on county_builders.user_id = users.id""")

    db = [(i[0], i[1]) for i in cur.fetchall()]

    new_cob = [i for i in county_builders if i not in db]
    old_cob = [i for i in db if i not in county_builders]

    stats["cob_added"] = len(new_cob)
    stats["cob_removed"] = len(old_cob)

    # Update users
    cur.execute("SELECT * FROM users")

    results = cur.fetchall()

    db = [i[1] for i in results]
    with_id = [i[1] for i in results if i[2]]

    new_u = [i for i in users if i not in db]
    old_u = [i for i in db if i not in users]

    # Warn if user has ID in database
    warning = [i for i in old_u if i in with_id]
    if warning:
        print(f"[WARN]: Users to be removed with ID: {warning}")

    stats["u_added"] = len(new_u)
    stats["u_removed"] = len(old_u)

    # Update areas
    cur.execute("""SELECT locations.name as areas, cities.name as city, counties.name as county, state FROM locations
                LEFT JOIN cities ON locations.city_id = cities.id
                LEFT JOIN counties ON
                CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id""")

    db = [(i[0], i[1], i[2]) for i in cur.fetchall()]

    new_a = [i for i in areas if i not in db]
    old_a = [i for i in db if i not in areas]

    stats["a_added"] = len(new_a)
    stats["a_removed"] = len(old_a)

    # Update cities
    cur.execute("SELECT * FROM cities LEFT JOIN counties ON cities.county_id = counties.id")

    db = [(i[1], i[4]) for i in cur.fetchall()]

    new_c = [i for i in cities if i not in db]
    old_c = [i for i in db if i not in cities]

    stats["c_added"] = len(new_c)
    stats["c_removed"] = len(old_c)

    # Update database
    # Remove old build locations
    # Remove old location builders
    for i in old_lb:
        user = get_id("users", i[0])
        location = get_location(i[1])
        cur.execute("""DELETE FROM location_builders WHERE user_id = %s AND location_id = %s""", [user, location])
        conn.commit()
    # Remove old city builders
    for i in old_cib:
        user = get_id("users", i[0])
        city = get_city(i[1])
        cur.execute("""DELETE FROM city_builders WHERE user_id = %s AND city_id = %s""", [user, city])
        conn.commit()
    # Remove old county builders
    for i in old_cob:
        user = get_id("users", i[0])
        county = get_id("counties", i[1])
        cur.execute("""DELETE FROM county_builders WHERE user_id = %s AND county_id = %s""", [user, county])
        conn.commit()
    # Remove old locations
    for i in old_a:
        location = get_location(i)
        cur.execute("DELETE FROM locations WHERE id = %s", [location])
        conn.commit()
    # Remove old cities
    for i in old_c:
        city = get_city(i)
        cur.execute("DELETE FROM cities WHERE id = %s", [city])
        conn.commit()
    # Remove old users
    for i in old_u:
        user = get_id("users", i)
        cur.execute("DELETE FROM users WHERE id = %s", [user])
        conn.commit()
    # Add new users
    for i in new_u:
        pass
        cur.execute("INSERT INTO users (name) VALUES (%s)", [i])
        conn.commit()
    # Add new cities
    for i in new_c:
        county = get_id("counties", i[1])
        cur.execute("INSERT INTO cities (name, county_id) VALUES (%s, %s)", [i[0], county])
        conn.commit()
    # Add new locations
    for i in new_a:
        if i[1]:
            city = get_city((i[1], i[2]))
            cur.execute("INSERT INTO locations (name, city_id) VALUES (%s, %s)", [i[0], city])
            conn.commit()
        else:
            county = get_id("counties", i[2])
            cur.execute("INSERT INTO locations (name, county_id) VALUES (%s, %s)", [i[0], county])
            conn.commit()
    # Add new location builders
    for i in new_lb:
        user = get_id("users", i[0])
        location = get_location(i[1])
        cur.execute("""INSERT INTO location_builders (user_id, location_id) VALUES (%s, %s)""", [user, location])
        conn.commit()
    # Add new city builders
    for i in new_cib:
        user = get_id("users", i[0])
        city = get_city(i[1])
        cur.execute("""INSERT INTO city_builders (user_id, city_id) VALUES (%s, %s)""", [user, city])
        conn.commit()
    # Add new county builders
    for i in new_cob:
        user = get_id("users", i[0])
        county = get_id("counties", i[1])
        cur.execute("""INSERT INTO county_builders (user_id, county_id) VALUES (%s, %s)""", [user, county])
        conn.commit()

    print('-'*50)
    print("STATS:")
    print(f"Area builds: {stats['lb_added']} added, {stats['lb_removed']} removed")
    print(f"City builds: {stats['cib_added']} added, {stats['cib_removed']} removed")
    print(f"County builds: {stats['cob_added']} added, {stats['cob_removed']} removed")
    print(f"Users: {stats['u_added']} added, {stats['u_removed']} removed")
    print(f"Areas: {stats['a_added']} added, {stats['a_removed']} removed")
    print(f"Cities: {stats['c_added']} added, {stats['c_removed']} removed")
    print('-'*50)


def get_id(table, name):
    cur.execute(f"SELECT id FROM {table} WHERE name = %s", [name])
    return cur.fetchone()[0]


def get_location(location):
    if location[1]:
        cur.execute("""SELECT locations.id FROM locations
                    LEFT JOIN cities ON locations.city_id = cities.id
                    LEFT JOIN counties ON
                    CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id
                    WHERE locations.name = %s AND cities.name = %s AND counties.name = %s""", location)
    else:
        cur.execute("""SELECT locations.id FROM locations
                    LEFT JOIN cities ON locations.city_id = cities.id
                    LEFT JOIN counties ON
                    CAST(CONCAT(locations.county_id, cities.county_id) AS INT) = counties.id
                    WHERE locations.name = %s AND cities.name IS NULL AND counties.name = %s""",
                    (location[0], location[2]))
    return cur.fetchone()[0]


def get_city(city):
    cur.execute("""SELECT cities.id FROM cities
                LEFT JOIN counties ON cities.county_id = counties.id
                WHERE cities.name = %s AND counties.name = %s""", city)
    return cur.fetchone()[0]


if __name__ == "__main__":
    main()
