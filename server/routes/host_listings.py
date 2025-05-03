from flask import Blueprint, render_template, session, redirect, url_for

host_listings_bp = Blueprint(
    'host_listings',
    __name__,
    template_folder='../../client/templates'
)

@host_listings_bp.route('/host/listings')
def host_listings_page():
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    return render_template('host_listings.html', user_email=session['email'])
