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
    limit = int(request.args.get('limit', 5))
    offset = int(request.args.get('offset', 0))

    if not location:
        return jsonify({"error": "Location parameter is required."}), 400

    # First try to find from MongoDB
    cached_listings = list(rentals_collection.find({"search_location": location}).limit(limit))

    if cached_listings:
        # If Found in MongoDB, return cached data
        for rental in cached_listings:
            rental['_id'] = str(rental['_id'])  # MongoDB ID to string for JSON
        return jsonify(cached_listings), 200

    # If Not found in MongoDB, fetch from RapidAPI
    params = {
        "location": location,
        "limit": limit,
        "offset": offset,
        "days_on": "30"
    }

    try:
        response = requests.get(RENT_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        print(data.keys())
        listings = response.json().get('listings', [])

        if listings:
            # Save new listings into MongoDB
            for listing in listings:
                listing['search_location'] = location  # save search keyword for filtering later
                rentals_collection.update_one(
                    {"property_id": listing['property_id']},
                    {"$set": listing},
                    upsert=True
                )

        return jsonify(listings), 200

    except requests.RequestException as e:
        if e.response is not None:
            print("RapidAPI error:", e.response.text)
            return jsonify({"error": e.response.text}), e.response.status_code
        else:
            print("Request failed without response:", str(e))
            return jsonify({"error": str(e)}), 500