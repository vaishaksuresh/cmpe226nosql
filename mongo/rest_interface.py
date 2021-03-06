__author__ = 'vaishaksuresh'
import bottle
from bottle import route, run, request, response, abort, static_file
from pymongo import Connection, ASCENDING
from json import JSONEncoder
from bson.objectid import ObjectId
from bson.son import SON
from bson.code import Code
from pprint import pprint
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


@route('/repo/top', method='GET')
def get_push_events():

    if not request.query.limit:
        limit = 10
    else:
        limit = int(request.query.limit)
    reducer = Code("""
                    function(obj, prev){
                    prev.count++;
                    }
                """)
    cursor = db['push_events'].aggregate([
        {"$group": {"_id": "$repo.name", "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])},
        {"$limit": limit}
    ])
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor['result']]
    return MongoEncoder().encode(entries)


@route('/user/top', method='GET')
def get_push_events():

    if not request.query.limit:
        limit = 10
    else:
        limit = int(request.query.limit)
    cursor = db['push_events'].aggregate([
        {"$group": {"_id": {"username": "$actor.login", "profileurl": "$actor.url"}, "commits": {"$sum": 1}}},
        {"$sort": SON([("commits", -1), ("_id", -1)])},
        {"$limit": limit},
    ])
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor['result']]
    return MongoEncoder().encode(entries)


@route('/watch/top', method='GET')
def get_push_events():

    if not request.query.limit:
        limit = 10
    else:
        limit = int(request.query.limit)
    reducer = Code("""
                    function(obj, prev){
                    prev.count++;
                    }
                """)
    cursor = db['watch_events'].aggregate([
        {"$group": {"_id": {"repository": "$repo.name"}, "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])},
        {"$limit": limit}
    ])
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor['result']]
    return MongoEncoder().encode(entries)


@route('/issues/top', method='GET')
def get_push_events():

    if not request.query.limit:
        limit = 10
    else:
        limit = int(request.query.limit)
    reducer = Code("""
                    function(obj, prev){
                    prev.count++;
                    }
                """)
    cursor = db['issues_events'].aggregate([
        {"$group": {"_id": {"repository": "$repo.name"}, "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])},
        {"$limit": limit}
    ])
    if not cursor:
        abort(404, 'No document with id')
    response.content_type = 'application/json'
    entries = [entry for entry in cursor['result']]
    return MongoEncoder().encode(entries)


@route('/getfile', method='GET')
def get_index():
        f = open('../visualization/index.html').read()
        print f
        return static_file("index.html", "/Users/vaishaksuresh/Semester3/cmpe226/dev/cmpe226nosql/visualization")

run(host='localhost', port=8080, reloader=True)
