import json
from py2neo import neo4j, node, rel

f = open("file1.json", "r")
data = json.loads(f.read())

def is_issueevent_and_opened(event):
    return event[u'type'] == u'IssuesEvent' and event[u'payload'][u'action'] == u'opened' 

def is_issueevent(event):
    return event[u'type'] == u'IssuesEvent'

#remove empty values and values which are objects
def top_level_properties(event):
    newEvent = event.copy()
    for k in newEvent.keys():
        v = newEvent[k]
        if(v is None or type(v) is dict or type(v) is list):
            del newEvent[k]
    return newEvent
            
    

issueevents = filter(is_issueevent, data)

db = neo4j.GraphDatabaseService("http://localhost:7474/db/data")

#db.clear()

for ie in issueevents:
#     print ie
    
    eventType = ie["type"]
    repoId = ie["repo"]["id"]
    repoName = ie["repo"]["name"]
    
    issueId = ie["payload"]["issue"]["id"]
    issueTitle = ie["payload"]["issue"]["title"]
    issueAction = ie["payload"]["action"]
    issueCreatedAt = ie["payload"]["issue"]["created_at"]
    
#     print eventType
#     print "repository:", repoId, repoName  
#     print "issue:", issueId, issueAction, issueCreatedAt
    
    #remove null value and non-primitive values as properties cannot contain nested objects
    issueProperties = top_level_properties(ie['payload']['issue'])
#     print issueProperties
    
#     print issueProperties["id"], issueProperties['action']
    
    repoNode = db.get_or_create_indexed_node(index_name="issueevents", key=repoId, value=repoName, properties=top_level_properties(ie['repo']))
    issueNode = db.get_or_create_indexed_node(index_name="issueevents", key=issueId, value=issueTitle, properties=issueProperties)
    db.create(rel(repoNode, ("ISSUE_" + issueAction, {"issue_created_at": issueCreatedAt, "issue_action":issueAction}), issueNode))
    print "created relationship: "  + "ISSUE_" + str(issueAction) + "\tbetween reposirotyNode: " + str(repoId) + "\t and IssueNode: " + str(issueId)
