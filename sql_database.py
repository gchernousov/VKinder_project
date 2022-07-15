import psycopg2
import configparser

settings = configparser.ConfigParser()
settings.read("settings.ini")

database = settings['DATABASE_SETTINGS']['database_name']
user = settings['DATABASE_SETTINGS']['user']
password = settings['DATABASE_SETTINGS']['password']


class Postgresql:
    def __init__(self):
        self.con = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host='localhost',
            port='5432',
        )
        self.cursor = self.con.cursor()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE initiators (id INTEGER PRIMARY KEY, first_name VARCHAR(40), last_name VARCHAR(40));
        CREATE TABLE founds (id INTEGER PRIMARY KEY, first_name VARCHAR(40), last_name VARCHAR(40), profile VARCHAR(40));
        CREATE TABLE favourites (initiator_id INTEGER REFERENCES initiators(id), found_id INTEGER REFERENCES founds(id),
        CONSTRAINT pk2 PRIMARY KEY (initiator_id, found_id));
        CREATE TABLE disliked (initiator_id INTEGER REFERENCES initiators(id), found_id INTEGER REFERENCES founds(id),
        CONSTRAINT pk3 PRIMARY KEY (initiator_id, found_id));
        """)
        self.con.commit()

    def insert_initiator(self, user_info):
        self.cursor.execute(f"INSERT INTO initiators VALUES ({user_info['user_id']}, '{user_info['first_name']}', '{user_info['last_name']}')")
        self.con.commit()

    def insert_found(self, result: dict):
        self.cursor.execute(f"INSERT INTO founds VALUES ({result['id']}, '{result['first_name']}', '{result['last_name']}', '{result['profile']}')")
        self.con.commit()

    def insert_favourite(self, user_id, result_id):
        self.cursor.execute(f"INSERT INTO favourites VALUES ({user_id}, {result_id})")
        self.con.commit()

    def insert_dislike(self, user_id, result_id):
        self.cursor.execute(f"INSERT INTO disliked VALUES ({user_id}, {result_id})")
        self.con.commit()

    def query(self, query_text):
        self.cursor.execute(query_text)
        result = self.cursor.fetchall()
        return result

    def __del__(self):
        self.con.close()


# db = Postgresql()
# db.create_tables()