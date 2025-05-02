from flask import Blueprint, render_template, request, session, redirect, url_for

support_bp = Blueprint(
    'support',
    __name__,
    template_folder='../../client/templates'
)

@support_bp.route('/support', methods=['GET', 'POST'])
def support_page():
    user = session.get('user_email')
    if not user:
        return redirect(url_for('auth.login_page'))

    booking_id = request.values.get('booking_id', '')

    if request.method == 'POST':
        # In a real app you’d save this message to your DB or send an email.
        # For now we just pretend:
        message = request.form.get('message')
        # TODO: store/send support request here...
        return render_template('support.html',
                               user_email=user,
                               booking_id=booking_id,
                               confirmation="Your support request has been submitted! 😊")
    return render_template('support.html',
                           user_email=user,
                           booking_id=booking_id,
                           confirmation=None)
