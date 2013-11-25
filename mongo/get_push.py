__author__ = 'vaishaksuresh'
import json

dict_repo = {}
with open('./data/processed/push_events.json', 'r') as infile:
    data = infile.read()

json_data = json.loads(data)
print len(json_data)
for line in json_data:
    if line['repo']['name'] in dict_repo:
        dict_repo[line['repo']['name']] += 1
    else:
        dict_repo[line['repo']['name']] = 1

for w in sorted(dict_repo, key=dict_repo.get, reverse=True):
    print w, dict_repo[w]

