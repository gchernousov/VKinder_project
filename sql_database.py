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

    def check_user_in_initiators(self, user_id):
        if not self.query(f"SELECT id FROM initiators WHERE id = {user_id}"):
            self.insert_initiator(user_info)

    def check_users_for_match(self, user_id, liked_person_id):
        match = False
        if len(self.query(f"SELECT * FROM initiators WHERE id = {liked_person_id}")) != 0:
            if len(self.query(f"SELECT * FROM favourites WHERE initiator_id = {liked_person_id} AND "
                              f"found_id = {user_id}")) != 0:
                match = True
        return match

    def check_user_in_founds(self, founded_person):
        if not self.query(f"SELECT id FROM founds WHERE id = {founded_person['id']}"):
            self.insert_found(founded_person)

    def check_like_dislike(self, user_id, founded_person):
        evaluate = False
        if not self.query(
                f"SELECT found_id FROM favourites WHERE found_id = {founded_person['id']} and initiator_id = {user_id}"
        ) and not self.query(
            f"SELECT found_id FROM disliked WHERE found_id = {founded_person['id']} and initiator_id = {user_id}"
        ):
            evaluate = True
        return evaluate

    def show_all_favorites(self, user_id):
        select = f"SELECT id, first_name, last_name, profile FROM founds " \
                 f"JOIN favourites f ON founds.id = f.found_id WHERE f.initiator_id = {user_id}"
        favorites = self.query(select)
        return favorites

    def __del__(self):
        self.con.close()


# db = Postgresql()
# db.create_tables()