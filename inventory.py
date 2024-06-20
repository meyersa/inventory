from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import validators
import re 

MONGO_DB = None
app = Flask(__name__)

@app.post("/entity")
def add_entity(entity: str=None, type: str=None): 
    # Input from function param
    if entity is not None and type is not None: 
        pass

    # Input from URI
    elif len(request.args) > 0: 
        entity = request.args.get("entity")
        type = request.args.get("type")

    # Input from JSON data
    elif request.get_json(force=True) is not None: 
        data = request.get_json(force=True)

        entity = data.get("entity")
        type = data.get("type")

    # Fail, no input
    else: 
        return jsonify({'success': False, 'message': 'Could not get entity or type'}), 400

    # Clean data
    entity = str(entity).strip().lower()
    type = str(type).strip().lower()

    # Clear path
    if entity.find('/') != -1: 
        entity[:entity.find('/')]

    # Clear protocol 
    if "http://" in entity: 
        entity = entity.replace("http://", "")
    if "https://" in entity: 
        entity = entity.replace("https://", "")

    if not (validators.ipv4(entity) or validators.url("https://" + entity)):
        return jsonify({'success': False, 'message': 'Entity is not valid url/IP'}), 400

    # Ensure record doesn't exist already
    try: 
        if len(list(MONGO_DB.get_collection(type).find({"entity": entity}))) > 0: 
            return jsonify({'success': False, 'message': 'Entity already exists'}), 400
    
    except: 
        return jsonify({'success': False, 'message': 'Could not query Mongo'}), 400

    # Add entity with all checks passed
    try: 
        MONGO_DB.get_collection(type).insert_one({"entity": entity, "timestamp": str(datetime.now())})
    
    except: 
        return jsonify({'success': False, 'message': 'Could not add entity'}), 400

    return jsonify({'success': True, 'message': 'Entity added successfully'}), 200

@app.delete("/entity")
def delete_entity(entity: str=None, type: str=None):
    # Input from function param
    if entity is not None and type is not None: 
        pass

    # Input from URI
    elif len(request.args) > 0: 
        entity = request.args.get("entity")
        type = request.args.get("type")

    # Input from JSON data
    elif request.get_json(force=True) is not None: 
        data = request.get_json(force=True)

        entity = data.get("entity")
        type = data.get("type")

    # Fail, no input
    else: 
        return jsonify({'success': False, 'message': 'Could not get entity or type'}), 400

    # Clean data
    entity = str(entity).strip().lower()
    type = str(type).strip().lower()

    # Add entity with all checks passed
    try: 
        res = MONGO_DB.get_collection(type).delete_one({"entity": entity})
        
        if res.deleted_count != 1: 
            return jsonify({'success': False, 'message': 'Nothing was deleted'}), 400
    except: 
        return jsonify({'success': False, 'message': 'Could not delete entity'}), 400

    return jsonify({'success': True, 'message': 'Entity deleted successfully'}), 200

@app.get("/entities")
def get_entities(type: str=None):
    # Input from function param
    if type is not None: 
        type = type

    # Input from URI
    elif len(request.args) > 0: 
        type = request.args.get("type")

    # Input from JSON data
    elif request.get_json(force=True) is not None: 
        data = request.get_json(force=True)
        type = data.get("type")

    # Fail, no input
    else: 
        return jsonify({'success': False, 'message': 'Could not get entity type'}), 400

    # Clean data
    type = str(type).strip().lower()

    # Get all results
    to_return = list()
    try: 
        for ent in MONGO_DB.get_collection(type).find():
            to_return.append([str(ent.get("entity")), str(ent.get("timestamp"))])
    
    except: 
        return jsonify({'success': False, 'message': 'Could not list entities'}), 400

    return to_return

@app.get("/")
def home():
    return render_template("index.html", websites=get_entities("website"), hosts=get_entities("host"))


def init():
    # Get environment/constant values
    print("Getting environment variables")
    load_dotenv()

    mongo_url = str(os.getenv("MONGO_URL")).strip()
    mongo_db = str(os.getenv("MONGO_DB")).strip()

    if len(mongo_url) < 1 or len(mongo_db) < 1:
        raise ValueError("Could not locate ENV for Mongo URL/DB")

    print("Successfully got environment variables")

    # Setup Mongo client
    print("Setting up Mongo client")

    global MONGO_DB
    mongo_client = MongoClient(mongo_url)
    MONGO_DB = mongo_client.get_database(mongo_db)

    print("Successfully set up Mongo client")


if __name__ == "__main__":
    print("Starting inventory service")

    print("Initializing...")
    init()

    print("Starting web server...")
    app.run("0.0.0.0", port=8000, debug=True)
