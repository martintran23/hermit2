from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import datetime

support_bp = Blueprint(
    'support',
    __name__,
    template_folder='../../client/templates'
)

# --- In-memory store of support tickets ---
support_requests = []

@support_bp.route('/support', methods=['GET', 'POST'])
def support_page():
    # 1) Must be logged in
    user = session.get('email')
    if not user:
        return redirect(url_for('home.login_page'))

    # 2) Get booking_id from query string or POST
    booking_id = request.values.get('booking_id', '')

    # 3) On POST, record the new ticket
    confirmation = None
    if request.method == 'POST' and booking_id:
        message = request.form.get('message', '').strip()
        support_requests.append({
            'user_email': user,
            'booking_id': booking_id,
            'message': message,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
        confirmation = "Your support request has been submitted! 😊"

    # 4) Gather this user’s tickets
    user_tickets = [
        t for t in support_requests
        if t['user_email'] == user
    ]

    return render_template(
        'support.html',
        user_email=user,
        booking_id=booking_id,
        tickets=user_tickets,
        confirmation=confirmation
    )
