# -*- coding: utf-8 -*-
import argparse
import csv
from datetime import datetime
import re
import sys
import xlrd 
import json
import os
import psycopg2
import pprint as pp

'''

based on schutte_en_raa.tsv and our model

for each row:

    create a person

    name = geslachtsnaam
    infix = tussenvoegsel
    givenname = voornaam
    life_hint_begin = geboortejaaar
    life_hint_end = sterftejaar

    link a record that has record.id=schutte_nr en record komt van de database "Schutte" -verwijder de oude persoon
    link a record that has record.id=id en record komt van de database "RAA" -verwijder de oude persoon


    * href = https://switch.sd.di.huc.knaw.nl/raa/persoon/{id}
'''


def get_connection():
    conn = None
    cur = None
    try:
        # read database configuration
        params = { 'host' : os.environ.get('DATABASE_HOST', 'localhost'),
                'port' : int(os.environ.get('DATABASE_PORT', 5432)),
                'database' : os.environ.get('DATABASE_DB', 'persoonsnamen'),
                'user' : os.environ.get('DATABASE_USER', 'meindertkroese'),
                'password' : os.environ.get('DATABASE_PASSWORD', 'test') }
        
        #stderr(params)
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
    except Exception as e:
        stderr(f'connection to db failed:\n{e}')
        exit(1)
    return conn,cur

def db_command(cur,command,data):
    try:
        result = cur.execute(command,data)
        return result
    except Exception as e:
        stderr(f'{e}')
        stderr(f'command: {data}')
        stderr(f'data: {data}')
    return ''




def stderr(text="",nl="\n"):
    sys.stderr.write(f"{text}{nl}")


def arguments():
    today = f'{datetime.today().strftime("%Y%m%d")}'
    ap = argparse.ArgumentParser(description='Read raa_schutte.tsv and make database updates ')
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default = "input/schutte_en_raa.tsv" )
    args = vars(ap.parse_args())
    return args


def end_prog(code=0):
    stderr(f'einde: {datetime.today().strftime("%H:%M:%S")}')
    sys.exit(code)

 
if __name__ == "__main__":
    stderr(f'start: {datetime.today().strftime("%H:%M:%S")}')

    args = arguments()
    inputfile = args['inputfile']
    conn,cur = get_connection()

    persons = []
    records = []
    links = []
    teller = 1
    with open(inputfile) as fd:
        reader = csv.DictReader(fd, delimiter="\t", quotechar='"')
        for row in reader:
            #print(row)
            naam = row['geslachtsnaam']
            infix = row['tussenvoegsel']
            givenname = row['voornaam']
            life_hint_begin = row['geboortejaar']
            life_hint_end = row['sterfjaar']
            record_id = db_command(cur,"SELECT _id FROM records WHERE id = %s",[row['schutte_nr']])
            db_command(cur,"DELETE FROM persons WHERE record_nr = %s",[row['schutte_nr']])
            record_id = db_command(cur,"SELECT _id FROM records WHERE id=%s",[row['id']])
            db_command(cur,"DELETE FROM persons WHERE record_nr = %s",[row['id']])
            db_command(cur,"INSERT INTO persons (name, infix, givenname, life_hint_begin, life_hint_end, record_nr) VALUES (%s,%s,%s,%s,%s,%s)",[naam,infix,givenname,life_hint_begin,life_hint_end,record_id]);
            conn.commit()

    end_prog(0)

