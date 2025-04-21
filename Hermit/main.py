from flask import Flask, request, jsonify
import requests
from datetime import datetime
import uuid

app = Flask(__name__)

# ----------------------------------------
# 1) Lodgify code
#url = "https://api.lodgify.com/v2/properties"
#api_key = '4PE72MIUggANayatgtL7crI9SyEMllqE25DERi/2+Ue/GnmRXyMjqnsyc61u/frt'
#headers = {
#    "Accept": "application/json",   
#    "X-ApiKey": api_key             
#}
# ----------------------------------------

# 2) CONFIGURATION
RENT_URL = "https://us-real-estate-listings.p.rapidapi.com/for-rent"
DETAIL_URL = "https://us-real-estate-listings.p.rapidapi.com/v2/property"
rent_params = {
    "location": "Metairie, LA",  # change to desired city/ZIP
    "limit": 5,
    "offset": 0
}

# 3) Headers (Maro’s key)
headers = {
    "X-RapidAPI-Key":  "bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb",
    "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
}
# Booking store
bookings = []

# 4) Fetch and print the rental listings
resp = requests.get(RENT_URL, headers=headers, params=rent_params)
resp.raise_for_status()
rent_listings = resp.json().get("listings", [])

print("=== Rental Listings (/for-rent) ===")
for lst in rent_listings:
    pid  = lst["property_id"]
    href = lst["href"]
    addr = lst["location"]["address"]
    print(f"ID:      {pid}")
    print(f"URL:     {href}")
    print(f"Address: {addr['line']}, {addr['city']}, {addr['state_code']} {addr['postal_code']}")
    print("-" * 40)

if not rent_listings:
    print("No rentals found; check your location/params.")
    exit(0)

# ----------------------------------------
# 5) Group’s original v2/property call, now with a real property_id
DETAIL_URL = "https://us-real-estate-listings.p.rapidapi.com/v2/property"
first_id    = rent_listings[0]["property_id"]
detail_params = {"property_id": first_id}

detail_resp = requests.get(DETAIL_URL, headers=headers, params=detail_params)
print("\n=== Detail View (/v2/property) ===")
print("Status:", detail_resp.status_code)
print("Response headers:", detail_resp.headers)

if detail_resp.ok:
    detail = detail_resp.json().get("listing") or detail_resp.json().get("data") or {}
    print("Detail for property ID:", first_id)
    print("URL:    ", detail.get("href") or detail.get("permalink"))
    addr = detail.get("location", {}).get("address", {})
    print("Address:", f"{addr.get('line')}, {addr.get('city')}, {addr.get('state_code')} {addr.get('postal_code')}")
else:
    print("Error fetching detail:", detail_resp.status_code, detail_resp.text)

# === BOOKING ENDPOINT ===
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

# === Main ===
if __name__ == '__main__':
    app.run(debug=True)
