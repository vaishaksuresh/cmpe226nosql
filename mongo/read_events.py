__author__ = 'vaishaksuresh'
import json
import os

push_data = []
watch_data = []
follow_data = []


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

    for line in push_events:
        push_data.append(json.loads(unicode(line, errors='replace')))

    for line in watch_events:
        watch_data.append(json.loads(unicode(line, errors='replace')))

    for line in follow_events:
        follow_data.append(json.loads(unicode(line, errors='replace')))


def main():
    for dirname, dirnames, filenames in os.walk('./data'):
        dirnames.remove('processed')
        if '.git' in dirnames:
            dirnames.remove('.git')
        for filename in filenames:
            if filename != '.DS_Store':
                print os.path.join(dirname, filename)
                process_files(os.path.join(dirname, filename))

    with open('./data/processed/push_events.json', 'a') as outfile:
        json.dump(push_data, outfile, indent=2)
    with open('./data/processed/watch_events.json', 'a') as outfile:
        json.dump(watch_data, outfile, indent=2)
    with open('./data/processed/follow_events.json', 'a') as outfile:
        json.dump(follow_data, outfile, indent=2)

if __name__ == '__main__':
    main()


