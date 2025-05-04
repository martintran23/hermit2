from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

reviews_api = Blueprint('reviews_api', __name__)

# Mongo setup (reuse hermit_db)
client = MongoClient('mongodb://localhost:27017/')
db = client['hermit_db']
reviews_col = db['reviews']

def require_login():
    if 'email' not in session:
        return jsonify({"error": "Login required"}), 401
    return None

@reviews_api.route('/api/reviews/<property_id>', methods=['GET'])
def get_reviews(property_id):
    # Return all reviews for this property
    docs = list(reviews_col.find({"property_id": property_id}).sort("timestamp", 1))
    out = []
    for d in docs:
        out.append({
            "id":        str(d["_id"]),
            "user_email": d["user_email"],
            "rating":    d["rating"],
            "comment":   d["comment"],
            "timestamp": d["timestamp"].isoformat()
        })
    return jsonify(out), 200

@reviews_api.route('/api/reviews/<property_id>', methods=['POST'])
def post_review(property_id):
    err = require_login()
    if err: return err

    data = request.get_json() or {}
    rating  = data.get("rating")
    comment = data.get("comment", "").strip()

    if rating is None or not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be 1–5"}), 400

    doc = {
        "property_id": property_id,
        "user_email":  session["email"],
        "rating":      int(rating),
        "comment":     comment,
        "timestamp":   datetime.utcnow()
    }
    res = reviews_col.insert_one(doc)
    return jsonify({
        "id":        str(res.inserted_id),
        "user_email": doc["user_email"],
        "rating":    doc["rating"],
        "comment":   doc["comment"],
        "timestamp": doc["timestamp"].isoformat()
    }), 201
