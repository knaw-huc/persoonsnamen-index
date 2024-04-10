import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

class Db:
    def __init__(self):
        params = { 'host' : os.environ.get('DATABASE_HOST', 'localhost'),
                'port' : int(os.environ.get('DATABASE_PORT', 5432)),
                'database' : os.environ.get('DATABASE_DB', 'persoonsnamen'),
                'user' : os.environ.get('DATABASE_USER', 'meindertkroese'),
                'password' : os.environ.get('DATABASE_PASSWORD', 'test') }

        self.conn = psycopg2.connect(**params)
        self.cur = self.conn.cursor()
        self.item = []
        print(self.version())

    def version(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        print('PostgreSQL database version:')
        self.cur.execute('SELECT version()')
        # display the PostgreSQL database server version
        db_version = self.cur.fetchone()
#        cur.close()
        return {"version": db_version}

    def detail(self, id):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM persons WHERE id = " + id)
        record = cur.fetchone()
        self.single_field(record, "name", "Naam")
        self.date_fields(record, "life_hint_begin", "life_hint_begin")
        cur.close()
        retVal = self.item.copy()
        self.item = []
        return retVal

    def single_field(self, item, key, label):
        if (item[key] != None and item[key] != ""):
            self.item.append({"field": key, "value": item[key], "label": label})
        return

    def date_fields(self, item, key, typeDate, label):
        if (item[key] != None and str(item[key]) != ""):
            self.item.append({"field": key, "value": str(item[key]) + " (" + typeDate + ")", "label": label})
        return

    def get_provincie(self):
        pass

    def get_persons(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("select persons._id as id, persons.name as name,infix,givenname,life_hint_begin,life_hint_end,database.name as database from persons,records,database where records.person_id=persons._id and database_id=database._id")
        records = cur.fetchall()
        print(len(records))
        return records


