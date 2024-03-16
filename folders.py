import requests
import json
from random import randrange
import time
import csv
import os

base_url = "https://play.grafana.org"

contents = requests.get(base_url + "/api/folders?limit=5000").text
folders = json.loads(contents)
# print(json.dumps(folders))

x = 0

fieldNames = ['folderId', 'title', 'inherited', 'url', 'userLogin', 'userEmail', 'created', 'updated', 'role', 'permission', 'permissionName']

with open('permissions.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=fieldNames)
    w.writeheader()

    for folder in folders:
        x = x + 1
        headers = {"Authorization": "Bearer %s" % os.environ.get('GRAFANACLOUD_API_TOKEN')}
        txt = requests.get(base_url + "/api/folders/%s/permissions" % str(folder['uid']), headers=headers).text
        perms = json.loads(txt)
        
        for perm in perms:
            print(perm)
            obj = {
                'folderId': perm.get('folderId', "null"),
                'title': perm.get('title', "null"),
                'inherited': perm.get('inherited', "null"),    
                'url': perm.get('url', "null"),
                'userLogin': perm.get('userLogin', "null"),
                'userEmail': perm.get('userEmail', "null"),
                'created': perm.get('created', "null"),
                'updated': perm.get('updated', "null"),
                'role': perm.get('role', "null"),
                'permission': perm.get('permission', "null"),
                'permissionName': perm.get('permissionName', "null")
            }
            w.writerow(obj)