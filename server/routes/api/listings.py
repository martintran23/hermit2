from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId

listings_api = Blueprint('listings_api', __name__)

# Mongo connection (reuse or create new)
client = MongoClient('mongodb://localhost:27017/')
db = client['hermit_db']
host_listings = db['host_listings']

def host_only():
    if 'email' not in session:
        return jsonify({"error": "Authentication required"}), 401

@listings_api.route('/api/listings', methods=['GET'])
def get_listings():
    # Return only this host's listings
    host = session.get('email')
    if not host:
        return jsonify({"error": "Login required"}), 401

    docs = list(host_listings.find({"host_email": host}))
    for d in docs:
        d['id'] = str(d['_id'])
        del d['_id']
    return jsonify(docs), 200

@listings_api.route('/api/listings', methods=['POST'])
def create_listing():
    host = session.get('email')
    if not host:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json() or {}
    required = ['title', 'address', 'price', 'description', 'image_url']
    if not all(field in data for field in required):
        return jsonify({"error": "Missing fields"}), 400

    doc = {
        "host_email":  host,
        "title":       data['title'],
        "address":     data['address'],
        "price":       data['price'],
        "description": data['description'],
        "image_url":   data['image_url']
    }
    res = host_listings.insert_one(doc)
    doc['id'] = str(res.inserted_id)
    return jsonify(doc), 201

@listings_api.route('/api/listings/<id>', methods=['PUT'])
def update_listing(id):
    host = session.get('email')
    if not host:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json() or {}
    # only allow update of these fields
    update = {k: data[k] for k in ['title','address','price','description','image_url'] if k in data}

    result = host_listings.update_one(
        {"_id": ObjectId(id), "host_email": host},
        {"$set": update}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Listing not found or unauthorized"}), 404
    return jsonify({"message": "Updated"}), 200

@listings_api.route('/api/listings/<id>', methods=['DELETE'])
def delete_listing(id):
    host = session.get('email')
    if not host:
        return jsonify({"error": "Login required"}), 401

    result = host_listings.delete_one({"_id": ObjectId(id), "host_email": host})
    if result.deleted_count == 0:
        return jsonify({"error": "Listing not found or unauthorized"}), 404
    return jsonify({"message": "Deleted"}), 200
