from flask import Blueprint, render_template

payments_bp = Blueprint(
    'payments',
    __name__,
    template_folder='../../client/templates'
)

@payments_bp.route('/payments/<booking_id>')
def payment_page(booking_id):
    # step 1: show a fake payment form
    return render_template('payment.html', booking_id=booking_id)

@payments_bp.route('/payments/<booking_id>/confirm')
def payment_confirm(booking_id):
    # step 2: show the “booking confirmed” page
    return render_template('payment_confirm.html', booking_id=booking_id)