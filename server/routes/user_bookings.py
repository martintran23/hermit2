from flask import Blueprint, render_template, session, redirect, url_for

user_bookings_bp = Blueprint(
    'user_bookings',
    __name__,
    template_folder='../../client/templates'
)

@user_bookings_bp.route('/my-bookings')
def my_bookings_page():
    user = session.get('email')  # ✅ FIXED from 'user_email' to 'email'
    if not user:
        return redirect(url_for('home.login_page'))
    return render_template('my_bookings.html', user_email=user)
