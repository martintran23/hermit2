from flask import Blueprint, render_template, session, redirect, url_for

host_listings_bp = Blueprint(
    'host_listings',
    __name__,
    template_folder='../../client/templates'
)

@host_listings_bp.route('/host/listings')
def host_listings_page():
    # 1) Must be logged in
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    # 2) If not a host, redirect to the Become Host prompt
    #    (the endpoint is become_host.become_host)
    if session.get('role') != 'host':
        return redirect(url_for('become_host.become_host'))

    # 3) Otherwise show the Host Dashboard
    return render_template('host_listings.html', user_email=session['email'])
