from flask import Blueprint, render_template, session, redirect, url_for

chat_page_bp = Blueprint(
    'chat_page',
    __name__,
    template_folder='../../client/templates'
)

@chat_page_bp.route('/chat/<booking_id>')
def chat_page(booking_id):
    # require login
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    # pass booking_id into the template
    return render_template('chat.html', booking_id=booking_id, user_email=session['email'])
