from elasticsearch import Elasticsearch

class Indexer:
    def __init__(self, config):
        self.config = config
        self.es = Elasticsearch([{"host": self.config["url"],
            "port": int(self.config["port"]),
            'scheme': "http"}],
            verify_certs=False)

    # Insert single document to index
    def add_to_index(self, data):
        result = self.es.index(index = self.config["index"], body = data)

    # Insert set of documents to index
    def bulk_to_index(self, data):
        result = self.es.bulk(index = self.config["index"], body=data, refresh='wait_for');

    def add_to_index_with_id(self, data, data_id):
        result = self.es.index(index = self.config["index"], body = data, id=data_id)

    def test_search(self):
        res = self.es.search(index= self.config["index"], query={"match": { "name": "Meerman"}})
        print("Got %d Hits:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print(hit)
#            print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

