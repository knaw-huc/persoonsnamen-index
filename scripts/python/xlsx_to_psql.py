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

cols = { 'name' : 'name',
         'givenname' : 'givenname', 
         'schutte_beginjaar': 'life_hint_begin', 
         'schutte_eindjaar' : 'life_hint_end' }

'''

    1. create a person
    name = name
    givenname = givenname
    life_hint_begin = schutte_beginjaar
    life_hint_end = schutte_eindjaar

    2. create a record

    id = schutte_nr

    3. create a link

    href = url

'''


def xls_file(filename, headerrow=0):
    if filename.endswith("xls"):
        xls_type = True
    else:
        xls_type = False
    if xls_type:
        wb = xlrd.open_workbook(filename,headerrow,encoding_override="utf-8", formatting_info=True)
    else:
        wb = xlrd.open_workbook(filename,headerrow,encoding_override="utf-8")
#
    sheet = wb.sheet_by_index(0)
    headers = [str(cell.value) for cell in sheet.row(0)]
    pp.pprint(headers,indent=4)

    teller = 1
    foreign_keys = ',\n    record_nr integer' # REFERENCES records (_id)'
    create_table('persons',cols.values(),foreign_keys)
    foreign_keys = ',\n    url_id integer' # REFERENCES links(_id)'
    create_table('records',['id'],foreign_keys)
    create_table('links',['href'])

    persons = []
    records = []
    links = []

    for rownum in range(sheet.nrows)[1:-1]:
        row = sheet.row(rownum)
        new_row = []
        #if rownum<5 or rownum>683:
            #stderr(rownum)
        for col in cols.keys():
            new_row.append(row[headers.index(col)].value)
        new_row.append(f"{teller}")
        if len(new_row)>0:
            persons.append(new_row)
            records.append([f"{teller}",row[headers.index('schutte_nr')].value,f"{teller}"])
            links.append([f"{teller}",row[headers.index('url')].value])
            teller += 1

    output.write(f'COPY persons ({", ".join(cols.values())}, record_nr) FROM stdin;\n')
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

    # foreign keys

    output.write('''  
ALTER TABLE persons ADD FOREIGN KEY (record_nr) REFERENCES records;

ALTER TABLE records ADD FOREIGN KEY (url_id) REFERENCES links;
''')




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
                    default = "../../input/schutte_buitenland_met_lemma.xlsx" )
    ap.add_argument('-o', '--outputfile',
                    help="outputfile",
                    default = f"schutte_data_{today}.sql" )
    ap.add_argument('-q', '--quotechar',
                    help="quotechar",
                    default = "'" )
    ap.add_argument('-t', '--headerrow',
                    help="headerrow; 0=row 1 (default = 0)",
                    default = 0 )
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
    headerrow = args['headerrow']
    quotechar = args['quotechar']

    output = open(outputfile, "w", encoding="utf-8")
 
    xls_file(inputfile)
    
    end_prog(0)

