import psycopg2


class Postgresql:
    def __init__(self):
        self.con = psycopg2.connect(
            database='postgres',
            user='postgres',
            password='A84db68d',
            host='localhost',
            port='5432',
        )
        self.cursor = self.con.cursor()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE initiators (id INTEGER PRIMARY KEY);
        CREATE TABLE founds (id INTEGER PRIMARY KEY, first_name VARCHAR(40), last_name VARCHAR(40), profile VARCHAR(40));
        CREATE TABLE favourites (initiator_id INTEGER REFERENCES initiators(id), found_id INTEGER REFERENCES founds(id),
        CONSTRAINT pk2 PRIMARY KEY (initiator_id, found_id));
        CREATE TABLE disliked (initiator_id INTEGER REFERENCES initiators(id), found_id INTEGER REFERENCES founds(id),
        CONSTRAINT pk3 PRIMARY KEY (initiator_id, found_id));
        """)
        self.con.commit()

    def insert_initiator(self, user_id):
        self.cursor.execute(f"INSERT INTO initiators VALUES ({user_id})")
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

# db.insert_initiator(125)
# p = db.query(f"SELECT id FROM initiators WHERE id = 56")
# print(p)
select = f"SELECT id, first_name, last_name FROM founds JOIN favourites f ON founds.id = f.found_id WHERE f.initiator_id = 7641579"

# for i in db.query(select):
#     print(i)