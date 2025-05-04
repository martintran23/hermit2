from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime

chat_api = Blueprint('chat_api', __name__)

# Mongo setup (reuse hermit_db)
client = MongoClient('mongodb://localhost:27017/')
db = client['hermit_db']
chats = db['chats']   # each document: { booking_id, user_email, message, timestamp }

def require_login():
    if 'email' not in session:
        return jsonify({"error": "Login required"}), 401
    return None

@chat_api.route('/api/chat/<booking_id>', methods=['GET'])
def get_messages(booking_id):
    err = require_login()
    if err: return err
    msgs = list(chats.find({"booking_id": booking_id}).sort("timestamp", 1))
    for m in msgs:
        m['id'] = str(m['_id'])
        m['timestamp'] = m['timestamp'].isoformat()
        del m['_id']
    return jsonify(msgs), 200

@chat_api.route('/api/chat/<booking_id>', methods=['POST'])
def post_message(booking_id):
    err = require_login()
    if err: return err
    data = request.get_json() or {}
    text = data.get('message','').strip()
    if not text:
        return jsonify({"error":"Empty message"}), 400

    msg = {
        "booking_id": booking_id,
        "user_email": session['email'],
        "message":    text,
        "timestamp":  datetime.utcnow()
    }
    res = chats.insert_one(msg)
    msg['id'] = str(res.inserted_id)
    msg['timestamp'] = msg['timestamp'].isoformat()
    return jsonify(msg), 201
