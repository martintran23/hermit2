from flask import Flask, request, jsonify
import requests
from datetime import datetime
import uuid

app = Flask(__name__)

# ----------------------------------------
# CONFIGURATION
RENT_URL   = "https://us-real-estate-listings.p.rapidapi.com/for-rent"
DETAIL_URL = "https://us-real-estate-listings.p.rapidapi.com/v2/property"
HEADERS = {
    "X-RapidAPI-Key":  "bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb",
    "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
}

# In-memory booking store
bookings = []

# === PROPERTIES ENDPOINTS ===
@app.route('/api/properties', methods=['GET'])
def list_properties():
    """Return a list of rental properties based on query params."""
    location = request.args.get('location')
    if not location:
        # Invalid location param
        return jsonify({"error": "Location parameter is required."}), 400

    # valid search: use provided params
    limit = int(request.args.get('limit', 5))
    offset = int(request.args.get('offset', 0))
    params = {"location": location, "limit": limit, "offset": offset}

    resp = requests.get(RENT_URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        # upstream API error
        return jsonify({"error": "Error fetching properties."}), resp.status_code

    listings = resp.json().get('listings', [])
    if not listings:
        # no results for provided location
        return jsonify({"error": "No properties found for location."}), 404

    return jsonify(listings), 200

@app.route('/api/properties/<property_id>', methods=['GET'])
def get_property_detail(property_id):
    """Return detailed info for a single property or 404 if not found."""
    params = {"property_id": property_id}
    resp = requests.get(DETAIL_URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        # invalid property id or upstream error
        return jsonify({"error": "Property not found."}), 404

    payload = resp.json()
    detail = payload.get('listing') or payload.get('data') or {}
    if not detail:
        return jsonify({"error": "Property not found."}), 404

    return jsonify(detail), 200

# === BOOKING ENDPOINTS ===
@app.route('/api/bookings', methods=['GET'])
def list_bookings():
    return jsonify(bookings), 200

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    required_fields = ['property_id', 'user_email', 'start_date', 'end_date']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required booking fields."}), 400

    booking = {
        "booking_id": str(uuid.uuid4()),
        "property_id": data['property_id'],
        "user_email": data['user_email'],
        "start_date": data['start_date'],
        "end_date": data['end_date'],
        "timestamp": datetime.utcnow().isoformat()
    }

    bookings.append(booking)
    return jsonify({"message": "Booking created.", "booking": booking}), 201

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    global bookings
    bookings = [b for b in bookings if b['booking_id'] != booking_id]
    return jsonify({"message": f"Booking {booking_id} canceled (if it existed)."}), 200

@app.route('/api/bookings/user/<email>', methods=['GET'])
def get_user_bookings(email):
    user_bookings = [b for b in bookings if b['user_email'] == email]
    return jsonify(user_bookings), 200

# === MAIN ===
if __name__ == '__main__':
    app.run(debug=True)
