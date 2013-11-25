import json
from py2neo import neo4j, node, rel

f = open("file1.json", "r")
data = json.loads(f.read())

def is_watchevent(event):
    return event[u'type'] == u'WatchEvent'

watchevents = filter(is_watchevent, data)
db = neo4j.GraphDatabaseService("http://localhost:7474/db/data")

for we in watchevents:
    reponode = db.get_or_create_indexed_node(index_name="watchevents", key=we['repo']['id'], value=we['repo']['url'], properties=we['repo'])
    usernode = db.get_or_create_indexed_node(index_name="watchevents", key=we['actor']['id'], value=we['actor']['login'], properties=we['actor'])
    db.create(rel(usernode, "WATCHES", reponode))
    print "Creating relationship %s WATCHES %s" % (we['actor']['login'], we['repo']['url'])

