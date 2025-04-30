from flask import Blueprint, request, jsonify, session
from server.models import users

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 409

    users.insert_one({
        "email": email,
        "password": password  # PLAINTEXT, can be replaced with hashes for security concern in the future
    })

    return jsonify({"message": "Signup successful"}), 201


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email})
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid login"}), 401

    session["user"] = str(user["_id"])
    session["email"] = email
    return jsonify({"message": "Login successful"}), 200