# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
import re
import sys

output = None
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



def stderr(text="",nl="\n"):
    sys.stderr.write(f"{text}{nl}")


def arguments():
    today = f'{datetime.today().strftime("%Y%m%d")}'
    ap = argparse.ArgumentParser(description='Read schutte xlsx to make postgres import file')
    ap.add_argument('-i', '--inputfile',
                    help="inputfile",
                    default = "input/RAA_Dump20211011.sql" )
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
    record_links = []
    teller = 1000
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
                    id_link = cols[0][1:]
                    id = f'{teller}'
                    name = f'{cols[5]}'.strip()
                    name = re.sub(r"\\'","'",name)
                    name = re.sub(r'\\"','"',name)
                    name = re.sub(r"(\\n|\\r)"," ",name)
                    infix = f'{cols[4]}'.strip()
                    infix = re.sub(r"\\'","'",infix)
                    infix = re.sub(r'\\"','"',infix)
                    infix = re.sub(r"(\\n|\\r)"," ",infix)
                    givenname = cols[3]
                    givenname = re.sub(r"(\\n|\\r)"," ",givenname)
                    life_hint_begin = cols[6]
                    life_hint_end = cols[10]
                    href = f'https://switch.sd.di.huc.knaw.nl/raa/persoon/{id_link}'
                    #                    
                    new_row = [id,name,infix,givenname,life_hint_begin,life_hint_end]
                    persons.append(new_row)
                    records.append([id,f'{id}',f"{teller}","1" ])
                    links.append([f'{teller}',href])
                    record_links.append([f"{teller}",f"{teller}"])
                    teller += 1

    output = open(outputfile, "w", encoding="utf-8")

    output.write(f'COPY database (_id,name) FROM stdin;\n')
    output.write('1\t"RAA"\n')
    output.write("\\.\n\n")

    output.write(f'COPY persons (_id,name,infix,givenname,life_hint_begin,life_hint_end) FROM stdin;\n')
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

    end_prog(0)

