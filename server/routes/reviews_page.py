# server/routes/reviews_page.py

from flask import Blueprint, render_template, session, redirect, url_for

reviews_page_bp = Blueprint(
    'reviews_page',
    __name__,
    template_folder='../../client/templates'
)

@reviews_page_bp.route('/reviews/<property_id>')
def reviews_page(property_id):
    # if you require login to post reviews, you can redirect here
    return render_template('reviews.html',
                           property_id=property_id,
                           user_email=session.get('email'))
