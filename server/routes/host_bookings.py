from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from pymongo import MongoClient
from server.routes.api.bookings import bookings  # in‑memory list or DB abstraction
from server.routes.api.listings import host_listings

host_bookings_bp = Blueprint(
    'host_bookings',
    __name__,
    template_folder='../../client/templates'
)

@host_bookings_bp.route('/host/bookings')
def host_bookings_page():
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') != 'host':
        return redirect(url_for('become_host.become_host'))
    return render_template('host_bookings.html', user_email=session['email'])

@host_bookings_bp.route('/api/bookings/host', methods=['GET'])
def api_host_bookings():
    """
    Returns a JSON list of bookings whose property_id belongs
    to the currently‐logged‐in host.
    """
    host = session.get('email')
    if not host:
        return jsonify({"error": "Login required"}), 401

    # 1) fetch all this host’s listings
    client = MongoClient('mongodb://localhost:27017/')
    db = client['hermit_db']
    my_listings = db['host_listings'].find({"host_email": host})
    my_ids = { str(l['_id']) for l in my_listings }

    # 2) fetch all bookings (in-memory or from your real DB)
    from server.routes.api.bookings import bookings  # your in‑memory list
    host_bookings = [b for b in bookings if b['property_id'] in my_ids]

    return jsonify(host_bookings), 200
