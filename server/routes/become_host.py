from flask import Blueprint, session, redirect, url_for, render_template

become_host_bp = Blueprint('become_host', __name__, template_folder='../../client/templates')

@become_host_bp.route('/become-host')
def become_host():
    # Must be logged in
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    return render_template('become_host.html', user_email=session['email'])
