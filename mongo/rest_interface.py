__author__ = 'vaishaksuresh'
import bottle
from bottle import route, run, request, response, abort
from pymongo import Connection
from json import JSONEncoder
from bson.objectid import ObjectId
import urlparse
import json
from bson import json_util

connection = Connection('localhost', 27017)
db = connection.github_events


class MongoEncoder(JSONEncoder):
    def default(self,obj,**kwargs):
        if isinstance(obj,ObjectId):
            return str(obj)
        else:
            return JSONEncoder.default(obj,**kwargs)



@route('/push', method='GET')
def get_push_events():
    if not request.query.limit:
        limit = 100
    else:
        limit = int(request.query.limit)
    if not request.query.skip:
        skip = 0
    else:
        skip = int(request.query.skip)
    cursor = db['push_events'].find({}, {"repo": 1, "created_at": 1, "actor": 1, "payload.commits": 1})\
        .limit(limit).skip(skip)
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor]
    return MongoEncoder().encode(entries)



@route('/watch', method='GET')
def get_push_events():
    if not request.query.limit:
        limit = 100
    else:
        limit = int(request.query.limit)
    if not request.query.skip:
        skip = 0
    else:
        skip = int(request.query.skip)
    cursor = db['watch_events'].find({}, {"repo": 1, "created_at": 1, "actor": 1}).limit(limit).skip(skip)
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor]
    return MongoEncoder().encode(entries)

@route('/follow', method='GET')
def get_push_events():
    if not request.query.limit:
        limit = 100
    else:
        limit = int(request.query.limit)
    if not request.query.skip:
        skip = 0
    else:
        skip = int(request.query.skip)
    cursor = db['follow_events'].find({}, {"repo": 1, "created_at": 1, "actor": 1}).limit(limit).skip(skip)
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor]
    return MongoEncoder().encode(entries)

@route('/issue', method='GET')
def get_push_events():
    if not request.query.limit:
        limit = 100
    else:
        limit = int(request.query.limit)
    if not request.query.skip:
        skip = 0
    else:
        skip = int(request.query.skip)
    cursor = db['issues_events'].find({}, {"repo": 1, "created_at": 1, "actor": 1}).limit(limit).skip(skip)
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor]
    return MongoEncoder().encode(entries)

run(host='localhost', port=8080)
