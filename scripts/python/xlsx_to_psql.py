# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
import re
import sys
import xlrd 
import pprint as pp

# This script uses xlrd to read xlsx files.
# According to https://xlrd.readthedocs.io/en/latest/index.html :
# 'This library will no longer read anything other than .xls files'
# In future a conversion to another library might be nescessary, for example: openpyxl
# (https://foss.heptapod.net/openpyxl)

output = None
delimiter = ','
quotechar = ''

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
    #pp.pprint(headers,indent=4)

    teller = 1
    persons = []
    records = []
    links = []
    record_links = []
    last_id = ''
    for rownum in range(sheet.nrows)[1:-1]:
        row = sheet.row(rownum)
        #if rownum<5 or rownum>683:
            #stderr(rownum)
        id = row[headers.index('schutte_nr')].value 
        if id==last_id:
            continue
        last_id = id
        new_row = [f'{id}']
        for col in cols.keys():
            new_row.append(row[headers.index(col)].value)
        if len(new_row)>0:
            persons.append(new_row)
            records.append([f"{teller}",f"{teller}",f'{id}','2'])
            links.append([f"{teller}",row[headers.index('url')].value])
            record_links.append([f"{teller}",f"{teller}"])
            teller += 1

    output.write(f'COPY database (_id,name) FROM stdin;\n')
    output.write('2\t"Schutte"\n')
    output.write("\\.\n\n")

    output.write(f'COPY persons (_id,{", ".join(cols.values())}) FROM stdin;\n')
    for person in persons:
        output.write("\t".join(person) + "\n")
    output.write("\\.\n\n")

    output.write(f'COPY links (_id,href) FROM stdin;\n')
    for link in links:
        output.write("\t".join(link) + "\n")
    output.write("\\.\n\n")

    output.write(f'COPY records (_id,id,person_id,database_id) FROM stdin;\n')
    for record in records:
        output.write("\t".join(record) + "\n")
    output.write("\\.\n\n")

    output.write(f'COPY record_links (record_id,link_id) FROM stdin;\n')
    for record in record_links:
        output.write("\t".join(record) + "\n")
    output.write("\\.\n\n")

def stderr(text="",nl="\n"):
    sys.stderr.write(f"{text}{nl}")


def arguments():
    today = f'{datetime.today().strftime("%Y%m%d")}'
    ap = argparse.ArgumentParser(description='Read schutte xlsx to make postgres import file')
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default = "input/schutte_buitenland_met_lemma.xlsx" )
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

