import requests
import json
import time
from pyfacebook import GraphAPI
from random import choice


UID = [
    "2077515769149584_2724909161076905",
    "2077515769149584",
    "1567847753582085_1589855691381291",
    "1567847753582085",
    "100018967787763_980280095947574",
    "100018967787763",
]
url = "https://graph.facebook.com"
access_tokens = list()
with open("resources/facebook/access_token/live", 'rt') as fp:
    for line in fp:
        access_tokens.append(line.strip())
meta_params = {'access_token': None, 'metadata': 1}
fields_params = {'access_token': None, 'fields': ''}
proxy = {"http": "http://user-kocstaging:EV!L&D!hJ6Ugy5Rs@vn.smartproxy.com:46000", "https": "http://user-kocstaging:EV!L&D!hJ6Ugy5Rs@vn.smartproxy.com:46000"}
# proxy = None
graph = GraphAPI(access_token=access_tokens[0], proxies=proxy)
versions = ['v1.0', 'v2.0', 'v2.1', 'v2.2', 'v2.3', 'v2.4', 'v2.5', 'v2.6', 'v2.7', 'v2.8', 'v2.9', 'v3.0', 'v3.1', 'v3.2', 'v3.3', 'v4.0', 'v5.0', 'v6.0', 'v7.0', 'v8.0', 'v9.0', 'v10.0', 'v11.0', 'v12.0', 'v13.0']
for uid in UID:
    TYPE, info, fields, old_fields, connections, old_connections = None, dict(), dict(), dict(), dict(), dict()
    for version in versions:
        current_url = f"{url}/{version}/{uid}"
        access_token = choice(access_tokens)
        meta_params["access_token"] = access_token
        response = graph.session.request(method="GET", url=current_url, params=meta_params)
        if response.status_code != 200:
            print(f"Cant get info {version}")
            continue
        data = response.json()
        if data.get("error"):
            print(f"Error {version}: {data['error']}")
            continue
        if data.get("metadata"):
            metadata = data["metadata"]
            TYPE = metadata["type"]
            current_fields, current_connections = dict(), dict()
            for field_detail in metadata["fields"]:
                typ3 = field_detail.pop("type", None)
                if typ3 is None:
                    continue
                name = field_detail.pop("name")
                current_fields[name] = {"type": typ3, "description": field_detail["description"], "version": version}
            for field_name in list(set(old_fields.keys()) - set(current_fields.keys())):
                fields[field_name] = old_fields[field_name]
            old_fields = current_fields
            for name in metadata["connections"]:
                current_connections[name] = {"version": version, "param": name, "type": "list"}
            for name in list(set(old_connections.keys()) - set(current_connections.keys())):
                connections[name] = old_connections[name]
            old_connections = current_connections
    for field_name in old_fields:
        fields[field_name] = old_fields[field_name]
    for name in old_connections:
        connections[name] = old_connections[name]
    print(TYPE)
    live_fields, die_fields = dict(), dict()
    for name in fields:
        version = fields[name]["version"]
        current_url = f"{url}/{version}/{uid}"
        fields_params["fields"] = name
        while True:
            access_token = choice(access_tokens)
            fields_params["access_token"] = access_token
            response = graph.session.request(method="GET", url=current_url, params=fields_params)
            if response.status_code == 200:
                live_fields[name] = fields[name]
                break
            else:
                data = response.json()
                if data.get("error"):
                    if "checkpoint" in data['error']['message']:
                        print(data['error']['message'])
                    else:
                        die_fields[name] = fields[name]
                        print(f"field {name} is dead: {data['error']['message']}")
                        break
                else:
                    print(data)
    live_connections, die_connections = dict(), dict()
    for name in connections:
        version = connections[name]["version"]
        current_url = f"{url}/{version}/{uid}/{name}"
        while True:
            access_token = choice(access_tokens)
            params = {"access_token": access_token}
            response = graph.session.request(method="GET", url=current_url, params=params)
            if response.status_code == 200:
                live_connections[name] = connections[name]
                break
            else:
                data = response.json()
                if data.get("error"):
                    if "checkpoint" in data['error']['message']:
                        print(data['error']['message'])
                    else:
                        die_connections[name] = connections[name]
                        print(f"connection {name} is dead: {data['error']['message']}")
                        break
                else:
                    print(data)
    with open(f"resources/metadata/{TYPE}_live_fields.json", 'wt') as fp:
        json.dump(live_fields, fp)
        print(live_fields)
    with open(f"resources/metadata/{TYPE}_die_fields.json", 'wt') as fp:
        json.dump(die_fields, fp)
        print(die_fields)
    with open(f"resources/metadata/{TYPE}_live_connections.json", "wt") as fp:
        json.dump(live_connections, fp)
        print(list(live_connections.keys()))
    with open(f"resources/metadata/{TYPE}_die_connections.json", "wt") as fp:
        json.dump(die_connections, fp)
        print(list(die_connections.keys()))