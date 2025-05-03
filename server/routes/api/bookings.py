from flask import Blueprint, request, jsonify, session
import uuid
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)

# In-memory booking store (you can switch to DB later)
bookings = []

@bookings_bp.route('/api/bookings', methods=['GET'])
def list_bookings():
    return jsonify(bookings), 200

@bookings_bp.route('/api/bookings', methods=['POST'])
def create_booking():
    if 'email' not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json() or {}
    required = ['property_id', 'start_date', 'end_date']  #  user_email no longer required
    if not all(field in data for field in required):
        return jsonify({"error": "Missing booking fields"}), 400

    booking = {
        "booking_id": str(uuid.uuid4()),
        "property_id": data['property_id'],
        "user_email": session['email'],  # ✅ Use session email only
        "start_date": data['start_date'],
        "end_date": data['end_date'],
        "timestamp": datetime.utcnow().isoformat()
    }
    bookings.append(booking)
    return jsonify({"booking": booking}), 201

@bookings_bp.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    global bookings
    bookings = [b for b in bookings if b['booking_id'] != booking_id]
    return jsonify({"message": f"Booking {booking_id} canceled"}), 200

@bookings_bp.route('/api/bookings/user/<email>', methods=['GET'])
def get_user_bookings(email):
    user_bookings = [b for b in bookings if b['user_email'] == email]
    return jsonify(user_bookings), 200
