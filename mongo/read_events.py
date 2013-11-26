__author__ = 'vaishaksuresh'
try:
    import simplejson as json
except ImportError:
    import json
import os
from pymongo import MongoClient

def is_push_event(event_data):

    try:
        return json.loads(unicode(event_data, errors='replace'))['type'] == 'PushEvent'
    except UnicodeDecodeError:
        print "UnicodeDecodeError: %s" % unicode(event_data, errors='replace')
        return False
    except:
        print "Exception: %s" % event_data
        return False


def is_watch_event(event_data):
    try:
        return json.loads(unicode(event_data, errors='replace'))['type'] == 'WatchEvent'
    except UnicodeDecodeError:
        print "UnicodeDecodeError: %s" % event_data
        return False
    except:
        print "Exception: %s" % event_data
        return False


def is_follow_event(event_data):
    try:
        return json.loads(unicode(event_data, errors='replace'))['type'] == 'FollowEvent'
    except UnicodeDecodeError:
        print "UnicodeDecodeError: %s" % event_data
        return False
    except:
        print "Exception: %s" % event_data
        return False


def process_files(file_name):

    with open(file_name) as data_file:
        data = data_file.readlines()

    push_events = filter(is_push_event, data)
    watch_events = filter(is_watch_event, data)
    follow_events = filter(is_follow_event, data)

    client = MongoClient()
    db = client.github_events
    push_collection = db.push_events
    watch_collection = db.watch_events
    follow_collection = db.follow_events


    for line in push_events:
        #push_data.append(json.loads(unicode(line, errors='replace')))
        push_collection.save(json.loads(unicode(line, errors='replace')))

    for line in watch_events:
        #watch_data.append(json.loads(unicode(line, errors='replace')))
        watch_collection.save(json.loads(unicode(line, errors='replace')))

    for line in follow_events:
        #follow_data.append(json.loads(unicode(line, errors='replace')))
        follow_collection.save(json.loads(unicode(line, errors='replace')))


def main():
    for dirname, dirnames, filenames in os.walk('../data'):
        dirnames.remove('processed')
        if '.git' in dirnames:
            dirnames.remove('.git')
        for filename in filenames:
            if filename != '.DS_Store':
                print os.path.join(dirname, filename)
                process_files(os.path.join(dirname, filename))


if __name__ == '__main__':
    main()


