from flask import Flask, request, jsonify
import json
from elastic_index import Index
from indexer import Indexer
from postgres_handler import Db
import requests


app = Flask(__name__)

config = {
    "url" : "localhost",
    "port" : "9200",
    "doc_type" : "persoonsnamen",
    "index" : "name"
}

index = Index(config)
db = Db()


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Content-type'] = 'application/json'
    return response

@app.route("/")
def hello_world():
    retStruc = {"app": "Procrustus service", "version": "0.1"}
    return json.dumps(retStruc)


@app.route("/facet", methods=['GET'])
def get_facet():
    facet = request.args.get("name")
    amount = request.args.get("amount")
    ret_struc = index.get_facet(facet + ".keyword", amount)
    return json.dumps(ret_struc)

@app.route("/filter-facet", methods=['GET'])
def get_filter_facet():
    facet = request.args.get("name")
    amount = request.args.get("amount")
    facet_filter = request.args.get("filter")
    ret_struc = index.get_filter_facet(facet + ".keyword", amount, facet_filter)
    return json.dumps(ret_struc)

@app.route("/browse", methods=['POST'])
def browse():
    struc = request.get_json()
    #ret_struc = index.browse(struc["page"], struc["page_length"], struc["sortorder"] + ".keyword", struc["searchvalues"])
    ret_struc = index.browse(struc["page"], struc["page_length"], "naam.keyword", struc["searchvalues"])
    return json.dumps(ret_struc)



@app.get('/typeinfo')
def typeinfo():
    if not request.values.get('url'):
        return 'No url specified', 400

    url = request.values.get('url')
    try:
        res = requests.head(url, allow_redirects=True)
        return jsonify(ok=res.ok,
                       url=url,
                       content_type=res.headers['content-type'] if res.ok else None)
    except:
        return jsonify(ok=False, url=url, content_type=None)



@app.get('/detail')
def get_detail():
    rec = request.args.get("rec")
    return json.dumps(db.detail(rec))

def makeNotNull(field):
    if field is None or field == "NULL":
        return ""
    else:
        return field

@app.route('/index', methods=['GET'])
def index_persons():
    res = db.get_persons()
    print(f'index {len(res)} persons') 
    idx = Indexer(config)
    teller = 0
    for elem in res:
        p_id = elem ['id']
        name = elem['name']
        givenname = elem['givenname']
        infix = elem['infix']
        life_hint_begin = makeNotNull(elem['life_hint_begin'])
        life_hint_end = makeNotNull(elem['life_hint_end'])
        database = elem['database']
        fullname = name
        infix = makeNotNull(infix)
        if not infix == '':
            fullname = f'{infix} {fullname}'
        givenname = makeNotNull(givenname)
        if not givenname == '':
            fullname = f'{givenname} {fullname}'
        data = {"ID": p_id,
                "name": name.strip(),
                "fullname": fullname.strip()}
        if life_hint_begin and life_hint_begin!='':
            data["life_hint_begin"] = life_hint_begin
        if life_hint_end and life_hint_end!='':
            data["life_hint_end"] = life_hint_end
        if database and database!='':
            data["database"] = database
        print(data)
        idx.add_to_index(data)
        teller += 1
    return jsonify({'result': f'{teller} names indexed'})


#Start main program

if __name__ == '__main__':
    app.run()

