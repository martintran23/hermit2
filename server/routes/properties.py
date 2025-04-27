from flask import Blueprint, request, jsonify
import requests

properties_bp = Blueprint('properties', __name__)

# API URL and Headers
RENT_URL = "https://us-real-estate-listings.p.rapidapi.com/for-rent"
HEADERS = {
    "X-RapidAPI-Key": "bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb",
    "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
}

@properties_bp.route('/api/properties', methods=['GET'])
def list_properties():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location parameter is required."}), 400

    limit = request.args.get('limit', 5)
    offset = request.args.get('offset', 0)

    params = {
        "location": location,
        "limit": limit,
        "offset": offset,
        "days_on": "30"
    }

    try:
        response = requests.get(RENT_URL, headers=HEADERS, params=params)
        print("RapidAPI raw response:", response.status_code, response.text)
        response.raise_for_status()
        listings = response.json().get('listings', [])
        return jsonify(listings), 200