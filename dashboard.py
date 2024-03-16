import requests
import json
from random import randrange
import time
import csv

base_url = "https://play.grafana.org"

contents = requests.get(base_url + "/api/search?limit=5000&type=dash-db").text
dashboards = json.loads(contents)

# for dash in dashboards:
#     [title, uid, id] = [dash['title'], dash['uid'], dash['id']]
#     print(dash['title'])
#     print(dash['uid'])
#     print(dash['id'])

limit = len(dashboards)
records = []

def euid(thing):
    try:
        return thing.get('uid', '')
    except:
        return thing

def extract_datasources(dash):
    try:
        return sorted(set([euid(ds) for ds in [panel.get('datasource', {}) for panel in dash['panels']]]))
    except: 
        return []

fieldNames = [
    'url', 'title', 'expires', 'created', 'updated', 'updatedBy', 'createdBy', 'version', 'folderUrl', 'editable', 'datasources'
]

with open('dashboards.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=fieldNames)
    w.writeheader()

    for x in range(0, limit):
        dash = dashboards[x]
        time.sleep(0.1)

        if x % 100 == 0:
            print("%d dashboards so far..." % x)

        deets = requests.get(base_url + "/api/dashboards/uid/" + dash['uid']).text
        j = json.loads(deets)
        # print(j)
        obj = {
            'url': base_url + '/' + j['meta']['url'],
            'title': j['dashboard']['title'],
            'expires': j['meta']['expires'],
            'created': j['meta']['created'],
            'updated': j['meta']['updated'],
            'updatedBy': j['meta']['updatedBy'],
            'createdBy': j['meta']['createdBy'],
            'version': j['meta']['version'],
            'folderUrl': j['meta']['folderUrl'],
            'editable': j['dashboard'].get('editable', 'null'),
            'datasources': extract_datasources(j['dashboard'])
        }
        records.append(obj)
        w.writerow(obj)




