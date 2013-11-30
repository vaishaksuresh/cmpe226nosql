import json
from py2neo import neo4j, node, rel
import os

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
            
    
db = neo4j.GraphDatabaseService("http://localhost:7474/db/data")

# db.clear()

def process_single_file_data(jsonArray):
    data = json.loads(jsonArray)
    issueevents = filter(is_issueevent, data)
    for ie in issueevents:
    #     print ie
        
        eventType = ie["type"]
        repoId = ie["repo"]["id"]
        repoName = ie["repo"]["name"]
        
        issueId = ie["payload"]["issue"]["id"]
        issueTitle = ie["payload"]["issue"]["title"]
        issueAction = ie["payload"]["action"]
        issueCreatedAt = ie["payload"]["issue"]["created_at"]
        
#         print eventType
#         print "repository:", repoId, repoName  
#         print "issue:", issueId, issueAction, issueCreatedAt
        
        #remove null value and non-primitive values as properties cannot contain nested objects
        issueProperties = top_level_properties(ie['payload']['issue'])
#         print issueProperties
#         print issueProperties["id"], issueProperties['action']
        
        repoNode = db.get_or_create_indexed_node(index_name="issueevents", key=repoId, value=repoName, properties=top_level_properties(ie['repo']))
        repoNode.add_labels("REPOSITORY")
        issueNode = db.get_or_create_indexed_node(index_name="issueevents", key=issueId, value=issueTitle, properties=issueProperties)
        issueNode.add_labels("ISSUE")
        db.create(rel(repoNode, ("ISSUE_" + issueAction, {"issue_created_at": issueCreatedAt, "issue_action":issueAction}), issueNode))
        print "created relationship: "  + "ISSUE_" + str(issueAction) + "\tbetween reposirotyNode: " + str(repoId) + "\t and IssueNode: " + str(issueId)


jsonFiles = []
src = "./files"
names = os.listdir(src)
for file in names:
    if file.endswith(".json"):
        #print os.path.join(root, file)
        jsonFiles.append(os.path.join(src, file));

    
# f = open("file1.json", "r")
# data = json.loads(f.read())

def jsonify_file(file):
    f = open(file, "r")
    jsonArray = ""
    for line in f:
        line = line.rstrip() + ','
        jsonArray += line
    
    if(len(jsonArray.strip()) > 0):
        jsonArray = jsonArray[:-1]
        jsonArray2 = ''.join(('[', jsonArray, ']'))
    
        return jsonArray2
    
    #return empty array
    return []
    

for file in jsonFiles:
    print "processing file: " + file;
    jsonArray = jsonify_file(file)
    process_single_file_data(jsonArray)
    
        
        
    
    
    
