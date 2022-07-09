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

    def create_insert(self, query_text):
        self.cursor.execute(query_text)
        self.con.commit()

    def query(self, query_text):
        self.cursor.execute(query_text)
        result = self.cursor.fetchall()
        return result

    def __del__(self):
        self.con.close()


create_table1 = '''CREATE TABLE initiators (id INTEGER PRIMARY KEY, first_name VARCHAR(40), last_name VARCHAR(40),
                    birthday INTEGER, id_sex INTEGER, city VARCHAR(40));'''
create_table2 = """CREATE TABLE founds (id INTEGER PRIMARY KEY, first_name VARCHAR(40), last_name VARCHAR(40),
                    birthday VARCHAR(40), id_sex INTEGER, city VARCHAR(40));"""
create_table3 = """CREATE TABLE initiators_founds (initiator_id INTEGER REFERENCES initiators(id), 
                    found_id INTEGER REFERENCES founds(id), 
                    CONSTRAINT pk2 PRIMARY KEY (initiator_id, found_id));"""

insert_data1 = "INSERT INTO initiators VALUES (13526, 'ramil', 'mamytov', 29, 1, 'Moscow')"
insert_data2 = "INSERT INTO founds VALUES (22896, 'alfa', 'mamytova', 26, 2, 'Kazan')"
insert_data3 = "INSERT INTO initiators_founds VALUES (13526, 22896)"

a = 13526

query_select = f"SELECT * FROM founds JOIN initiators_founds if ON founds.id = if.found_id WHERE if.initiator_id = {a}"

db = Postgresql()

# db.create_insert(create_table1)
# db.create_insert(create_table2)
# db.create_insert(create_table3)
# db.create_insert(insert_data1)
# db.create_insert(insert_data2)
# db.create_insert(insert_data3)

for user in db.query(query_select):
    print(user)