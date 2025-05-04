# server/routes/api/auth.py

from flask import Blueprint, request, jsonify, session
from server.models import users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email    = data.get("email")
    password = data.get("password")
    role     = data.get("role", "traveler")  # default traveler

    if not email or not password or role not in ("traveler", "host"):
        return jsonify({"error": "Missing email/password or invalid role"}), 400

    if users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 409

    # Create user with chosen role
    users.insert_one({
        "email":    email,
        "password": password,
        "role":     role
    })

    return jsonify({"message": "Signup successful"}), 201


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email    = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email})
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid login"}), 401

    # Store user info and role in session
    session["user"]  = str(user["_id"])
    session["email"] = email
    session["role"]  = user.get("role", "traveler")

    return jsonify({"message": "Login successful"}), 200
