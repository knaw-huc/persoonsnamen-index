# -*- coding: utf-8 -*-
import argparse
import csv
from datetime import datetime
import re
import sys
import xlrd 
import json
import pprint as pp
import roman;
from roman import InvalidRomanNumeralError;

# This script uses xlrd to read xlsx files.
# According to https://xlrd.readthedocs.io/en/latest/index.html :
# 'This library will no longer read anything other than .xls files'
# In future a conversion to another library might be nescessary, for example: openpyxl
# (https://foss.heptapod.net/openpyxl)

output = None
delimiter = ','
quotechar = ''
pattern = re.compile(r'([^(]*)\(([^)]*)\)([^(]*)')
pattern_2 = re.compile(r'([^[]*)\[([^]]*)]([^[]*)')
patt = re.compile(r'([^+)(\][]+)')
long_lat_patt = re.compile(r"([NSEW]) (\d+)° (\d+)' (\d+)'?'?")
manuscript_ids = []


'''
based on raa and our model

for this mapping

    1. create a database:

    * name = "RAA"

for each row:

    1. create a person

    * name = geslachtsnaam
    * givenname = voornaam
    * life_hint_begin = geboortedatum
    * life_hint_end = overlijdensdatum

    2. create a record

    * id = id

    3. create a link

    * href = https://switch.sd.di.huc.knaw.nl/raa/persoon/{id}
'''


def create_table(table, columns,foreign=''):
     output.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
     output.write(f"CREATE TABLE {table} (\n    ")
     output.write(f"_id SERIAL PRIMARY KEY,\n    ")
     if len(columns)>0:
         output.write(" TEXT,\n    ".join(columns))
         output.write(f" TEXT")
     output.write(f"{foreign}\n);\n\n")


def stderr(text="",nl="\n"):
    sys.stderr.write(f"{text}{nl}")


def arguments():
    today = f'{datetime.today().strftime("%Y%m%d")}'
    ap = argparse.ArgumentParser(description='Read schutte xlsx to make postgres import file')
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default = "../../input/RAA_Dump20211011.sql" )
    ap.add_argument('-o', '--outputfile',
                    help="outputfile",
                    default = f"raa_data_{today}.sql" )
    ap.add_argument('-q', '--quotechar',
                    help="quotechar",
                    default = "'" )
    args = vars(ap.parse_args())
    return args


def end_prog(code=0):
    stderr(f'einde: {datetime.today().strftime("%H:%M:%S")}')
    sys.exit(code)

 
if __name__ == "__main__":
    stderr(f'start: {datetime.today().strftime("%H:%M:%S")}')

    args = arguments()
    inputfile = args['inputfile']
    outputfile = args['outputfile']
    quotechar = args['quotechar']

    persons = []
    records = []
    links = []
    teller = 1
    with open(inputfile , 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('INSERT INTO `persoon`'):
                recs = line[29:].split('),(')
                for idx in range(0,len(recs)):
                    recs[idx] = re.sub(r',(\d+),',r",'\1',",recs[idx])
                    recs[idx] = re.sub(r',(\d+),',r",'\1',",recs[idx])
                    recs[idx] = re.sub(r'\((\d+),',r"'\1',",recs[idx])
                    recs[idx] = re.sub(r'^(\d+),',r"'\1',",recs[idx])
                    recs[idx] = re.sub('NULL',"'NULL'",recs[idx])
                    cols = recs[idx].split("','")
                    id = cols[0][1:]
                    name = f'{cols[4]} {cols[5]}'.strip()
                    givenname = cols[3]
                    life_hint_begin = cols[6]
                    life_hint_end = cols[10]
                    href = f'https://switch.sd.di.huc.knaw.nl/raa/persoon/{id}'
                    new_row = [id,name,givenname,life_hint_begin,life_hint_end,f"{teller}"]
                    persons.append(new_row)
                    records.append([f"{teller}",id,f"{teller}"])
                    links.append([f"{teller}",href])
                    teller += 1

    output = open(outputfile, "w", encoding="utf-8")
    teller = 1
    foreign_keys = ',\n    record_nr integer REFERENCES records (_id)'
    create_table('persons',['name','givenname','life_hint_begin','life_hint_end'],foreign_keys)
    foreign_keys = ',\n    url_id integer REFERENCES links(_id)'
    create_table('records',['id'],foreign_keys)
    create_table('links',['href'])

    output.write(f'COPY persons (name,givenname,life_hint_begin,life_hint_end,record_nr) FROM stdin;\n')
    for person in persons:
        output.write("\t".join(person) + "\n")
    output.write("\\.\n\n")

    output.write(f'COPY records (_id,id,url_id) FROM stdin;\n')
    for record in records:
        output.write("\t".join(record) + "\n")
    output.write("\\.\n\n")

    output.write(f'COPY links (_id,href) FROM stdin;\n')
    for link in links:
        output.write("\t".join(link) + "\n")
    output.write("\\.\n\n")
    
    end_prog(0)

