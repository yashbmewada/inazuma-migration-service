#!/usr/bin/env python
from json import dumps

from flask import Flask, g, Response, request

from neo4j.v1 import GraphDatabase, basic_auth, ResultError

app = Flask(__name__, static_url_path='/static/')
driver = GraphDatabase.driver('bolt://127.0.0.1', auth=basic_auth("neo4j","1"))
#basic auth with: driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("<user>", "<pwd>"))

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()

@app.route("/")
def get_index():
    return app.send_static_file('index.html')

def serialize_member(member):
    return {
        'id': member['id'],
        'member_id': member['member_id'],
        'reference_id': member['reference_id'],
        'referer_name': member['referer_name'],
        'name': member['name'],
        'name_again': member['name_again'],
        'state': member['state'],
        'status_flag1':member['status_flag1'],
        'status_flag2':member['status_flag2']
    }


@app.route("/name")
def get_graph():
    db = get_db()
    results = db.run("MATCH (m:Member) "\
             "RETURN m.name as name "\
             "LIMIT {limit}", {"limit": request.args.get("limit", 100)})
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["name"], "label": "Member"})
        target = i
        i += 1
    return Response(dumps({"nodes": nodes}),
                    mimetype="application/json")

@app.route("/tree")
def get_tree():
    db = get_db()
    results = db.run("MATCH (a:Member)<-[:Refers*]-(b:Member) return b.name as parent, a.name as children limit 100000")
    data = []
    parent_list = set()
    json = []
    i=0
    for record in results:
        data.append(dict(record))
    for value in data:
        parent_list.add(value["parent"])
    print(parent_list)
    for parent in parent_list:
        json.append({"name":parent,"children":[]})
    for person in json:
        for value in data:
            if person["name"] == value["parent"]:
                person["children"].append({"name":value["children"]})

    return Response(dumps({"data":json}), mimetype="application/json")
    

@app.route("/search")
def get_search():
    return "SEARCH OK"

@app.route("/add")
def add_member():
    return "ADD OK"

@app.route("/update")
def update_member():
    return "UPDATE OK"

@app.route("/delete")
def delete_member():
    return "DELETE OK"

@app.route("/commission")
def commision():
    return "COMMISSION OK"

if __name__ == '__main__':
    app.debug = True
    app.run(port=8080)
