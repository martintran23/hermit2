from flask import Blueprint, render_template, request, session, redirect, url_for
from server.routes.api.bookings import bookings  # assuming this is your in‑memory list

modify_bp = Blueprint(
    'modify',
    __name__,
    template_folder='../../client/templates'
)

@modify_bp.route('/modify-booking', methods=['GET', 'POST'])
def modify_booking_page():
    user = session.get('email')
    if not user:
        return redirect(url_for('home.login_page'))

    booking_id = request.values.get('booking_id', '')
    if not booking_id:
        return redirect(url_for('user_bookings.my_bookings_page'))

    # Find the booking
    booking = next((b for b in bookings if b['booking_id'] == booking_id), None)
    if not booking or booking['user_email'] != user:
        return redirect(url_for('user_bookings.my_bookings_page'))

    confirmation = None
    if request.method == 'POST':
        # Update dates
        booking['start_date'] = request.form.get('start_date')
        booking['end_date']   = request.form.get('end_date')
        confirmation = "Your booking dates have been updated."

    return render_template(
        'modify_booking.html',
        user_email=user,
        booking=booking,
        confirmation=confirmation
    )
