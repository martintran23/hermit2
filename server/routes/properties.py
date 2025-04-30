from flask import Blueprint, request, jsonify
import requests
from pymongo import MongoClient

properties_bp = Blueprint('properties', __name__)

# === MongoDB Connection ===
client = MongoClient('mongodb://localhost:27017/')
db = client['hermit_db']
rentals_collection = db['rentals']

# API URL and Headers
RENT_URL = "https://us-real-estate-listings.p.rapidapi.com/for-rent"
HEADERS = {
    "X-RapidAPI-Key": "bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb",
    "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
}

# === Search Rentals ===
@properties_bp.route('/api/properties', methods=['GET'])
def list_properties():
    location = request.args.get('location')
    try:
        limit  = int(request.args.get('limit', 5))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400

    if not location:
        return jsonify({"error": "Location parameter is required."}), 400

    # ——— Try MongoDB cache first ———
    try:
        raw = rentals_collection.find({"search_location": location})
        if hasattr(raw, 'limit'):
            # real cursor
            cursor = raw.limit(limit).skip(offset)
            cached_listings = list(cursor)
        else:
            # in tests, raw might already be a list
            cached_listings = raw[offset: offset + limit]
    except Exception:
        cached_listings = []

    if cached_listings:
        for r in cached_listings:
            if '_id' in r:
                r['_id'] = str(r['_id'])
        return jsonify(cached_listings), 200

    # ——— Fallback to external API ———
    params = {"location": location, "limit": limit, "offset": offset, "days_on": "30"}
    try:
        resp = requests.get(RENT_URL, headers=HEADERS, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # NEW: if the API says “no results,” return 404
        total = data.get("totalResultCount", 0)
        if total == 0:
            return jsonify({
                "error": f"No properties found for location '{location}'."
            }), 404

        listings = data.get("listings", [])
        # save into Mongo
        for listing in listings:
            listing['search_location'] = location
            rentals_collection.update_one(
                {"property_id": listing['property_id']},
                {"$set": listing},
                upsert=True
            )

        return jsonify(listings), 200

    except requests.RequestException as e:
        # propagate API errors
        if e.response is not None:
            return jsonify({"error": e.response.text}), e.response.status_code
        return jsonify({"error": str(e)}), 500