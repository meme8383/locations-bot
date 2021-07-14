import csv
import psycopg2

"""
converter.py: Convert data from CSV to SQL
"""


def add_counties(filename):
    counties = []
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            county = (row["County"], row["State"])
            if county not in counties:
                counties.append(county)

    for county in counties:
        cur.execute("""
                    INSERT INTO counties (name, state)
                    VALUES (%s, %s);
                    """,
                    (county[0], county[1]))


def add_cities(filename):
    cities = []
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["City"]:
                continue
            city = (row["City"], row["County"])
            if city not in cities:
                for item in cities:
                    if item[0] == city[0] and item[1] != city[1]:
                        print(f"[WARN]: Duplicate {city}, {item}")
                cities.append(city)

    for city in cities:
        cur.execute("""
                    SELECT id FROM counties
                    WHERE name = %s;""", [city[1]])

        county = cur.fetchone()

        cur.execute("""
                    INSERT INTO cities (name, county_id)
                    VALUES (%s, %s);
                    """,
                    (city[0], county))


def add_locations(filename):
    locations = []
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["Areas"]:
                continue
            area = (row["Areas"], row["County"], row["City"])
            if area not in locations:
                locations.append(area)

    for area in locations:
        if area[2]:
            cur.execute("""
                        SELECT id FROM cities
                        WHERE name = %s;""", [area[2]])

            city = cur.fetchone()

            cur.execute("""
                        INSERT INTO locations (name, city_id)
                        VALUES (%s, %s);
                        """,
                        (area[0], city))
        else:
            cur.execute("""
                        SELECT id FROM counties
                        WHERE name = %s;""", [area[1]])

            county = cur.fetchone()

            cur.execute("""
                        INSERT INTO locations (name, county_id)
                        VALUES (%s, %s);
                        """,
                        (area[0], county))


def add_users(filename):
    users = []
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            userdb = row["Members"].split(", ")
            for user in userdb:
                if user not in users:
                    users.append(user)

    for user in users:
        cur.execute(""" INSERT INTO users (name)
                    VALUES (%s)""", [user])


def add_builders(filename):
    location_builders = []
    city_builders = []
    county_builders = []
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Areas"]:
                for user in row["Members"].split(", "):
                    location_builders.append((user, row["Areas"]))
            elif row["City"]:
                for user in row["Members"].split(", "):
                    city_builders.append((user, row["City"]))
            else:
                for user in row["Members"].split(", "):
                    county_builders.append((user, row["County"]))

    for builder in location_builders:
        cur.execute("SELECT id FROM users WHERE name = %s", [builder[0]])
        user = cur.fetchone()[0]
        cur.execute("SELECT id FROM locations WHERE name = %s", [builder[1]])
        location = cur.fetchone()[0]

        cur.execute("INSERT INTO location_builders (user_id, location_id) VALUES (%s, %s)",
                    (user, location))
    for builder in city_builders:
        cur.execute("SELECT id FROM users WHERE name = %s", [builder[0]])
        user = cur.fetchone()[0]
        cur.execute("SELECT id FROM cities WHERE name = %s", [builder[1]])
        location = cur.fetchone()[0]

        cur.execute("INSERT INTO city_builders (user_id, city_id) VALUES (%s, %s)",
                    (user, location))
    for builder in county_builders:
        cur.execute("SELECT id FROM users WHERE name = %s", [builder[0]])
        user = cur.fetchone()[0]
        cur.execute("SELECT id FROM counties WHERE name = %s", [builder[1]])
        location = cur.fetchone()[0]

        cur.execute("INSERT INTO county_builders (user_id, county_id) VALUES (%s, %s)",
                    (user, location))


if __name__ == "__main__":
    conn = psycopg2.connect("dbname=btesw user=postgres password=password")
    cur = conn.cursor()

    # add_x(filename)

    conn.commit()

    cur.close()
    conn.close()
