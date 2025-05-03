# server/routes/payments.py

from flask import Blueprint, render_template, session

payments_bp = Blueprint(
    'payments',
    __name__,
    template_folder='../../client/templates'
)

@payments_bp.route('/payments/<booking_id>')
def payment_page(booking_id):
    return render_template('payment.html', booking_id=booking_id)

@payments_bp.route('/payments/<booking_id>/confirm')
def payment_confirm(booking_id):
    # step 2: show the “booking confirmed” page
    user_email = session.get('email')  # ← grab the logged‑in email
    return render_template(
        'payment_confirm.html',
        booking_id=booking_id,
        user_email=user_email  # ← pass it to the template
    )
