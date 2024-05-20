import requests
from requests.adapters import HTTPAdapter, Retry
import json
from random import randrange
import time
import csv
import datetime

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
    'url', 'title', 'expires', 'created', 'created_dt', 'updated', 'updated_dt', 'updatedBy', 'createdBy', 'version', 'folderUrl', 'editable', 'datasources',
    'panels', 'rows', 'links', 'tags', 'variables', 'annotations', 'variableNames', 'hasAcl', 'liveNow', 'panelTitles'
]

users = {}

def default_user(id):
    return {
        'id': id,
        'dashboards': 0,
        'lastSeen': datetime.datetime.fromisoformat("1980-03-10T21:49:33Z")
    }

def keep_user_stats(obj):
    if not obj['createdBy'] in users:
        users[obj['createdBy']] = default_user(obj['createdBy'])
    if not obj['updatedBy'] in users:
        users[obj['updatedBy']] = default_user(obj['updatedBy'])

    users[obj['createdBy']]['dashboards'] += 1
    if obj['created'] > users[obj['createdBy']]['lastSeen']:
        users[obj['createdBy']]['lastSeen'] = obj['created']
    if obj['updated'] > users[obj['updatedBy']]['lastSeen']:
        users[obj['updatedBy']]['lastSeen'] = obj['updated']

    if obj['createdBy'] == obj['updatedBy'] or obj['updatedBy'] == '':
        return

    users[obj['updatedBy']]['dashboards'] += 1
    if obj['updated'] > users[obj['updatedBy']]['lastSeen']:
        users[obj['updatedBy']]['lastSeen'] = obj['updated']

"""Format ISO dates in a way friendlier to spreadsheet typing"""
def dt(x):
    some_date = datetime.fromisoformat(x)
    return some_date.strftime("%m/%d/%Y")

def count_total_panels(dash):
    base = dash.get("panels", [])
    rows = dash.get("rows", [])
    tot = len(base)

    for row in rows:
        tot += len(row.get("panels", []))
    return tot

with open('dashboards.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=fieldNames)
    w.writeheader()

    session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for x in range(0, limit):
        dash = dashboards[x]
        time.sleep(0.1)

        if x % 100 == 0:
            print("%d dashboards so far..." % x)

        deets = session.get(base_url + "/api/dashboards/uid/" + dash['uid']).text
        j = json.loads(deets)
        # print(j)

        obj = {
            'url': base_url + j['meta']['url'],
            'title': j['dashboard']['title'],
            'expires': j['meta']['expires'],
            'created': datetime.datetime.fromisoformat(j['meta']['created']) if j['meta']['created'] else None,
            'updated': datetime.datetime.fromisoformat(j['meta']['updated']) if j['meta']['updated'] else None,
            'updatedBy': j['meta']['updatedBy'],
            'createdBy': j['meta']['createdBy'],
            'version': j['meta']['version'],
            'folderUrl': j['meta']['folderUrl'],
            'editable': j['dashboard'].get('editable', 'null'),
            'datasources': extract_datasources(j['dashboard']),
            'panels': count_total_panels(j['dashboard']),
            'rows': len(j['dashboard'].get('rows', [])),
            'links': len(j['dashboard'].get('links', [])),
            'tags': ', '.join(j['dashboard'].get('tags', [])),
            'variables': len(j['dashboard'].get('templating', {}).get('list', [])),
            'annotations': len(j['dashboard'].get('annotations', {"list":[]})['list']),
            'variableNames': ', '.join([v["name"] for v in j['dashboard'].get('templating', {"list":[]}).get('list', [])]),
            'panelTitles': '\n'.join([panel.get('title', '') for panel in j['dashboard'].get('panels', [])]),
            'hasAcl': j['meta'].get('hasAcl', False),
            'liveNow': j['dashboard'].get('liveNow', False),
        }
        obj['created_dt'] = obj['created'].strftime("%m/%d/%Y")
        obj['updated_dt'] = obj['updated'].strftime("%m/%d/%Y")

        keep_user_stats(obj)            

        records.append(obj)
        w.writerow(obj)

with open('users.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=['id', 'dashboards', 'lastSeen'])
    w.writeheader()
    for k, v in users.items():
        w.writerow(v)



