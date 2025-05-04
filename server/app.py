from flask import Flask, session

from server.routes.home            import home_bp
from server.routes.properties      import properties_bp
from server.routes.api.bookings    import bookings_bp
from server.routes.api.auth        import auth_bp
from server.routes.payments        import payments_bp
from server.routes.user_bookings   import user_bookings_bp
from server.routes.support         import support_bp
from server.routes.modify          import modify_bp
from server.routes.api.listings    import listings_api
from server.routes.host_listings   import host_listings_bp
from server.routes.host_bookings   import host_bookings_bp
from server.routes.become_host     import become_host_bp
from server.routes.api.chat        import chat_api
from server.routes.chat_page       import chat_page_bp
from server.routes.api.reviews     import reviews_api
from server.routes.reviews_page    import reviews_page_bp

app = Flask(
    __name__,
    template_folder='../client/templates',
    static_folder='../client/static'
)

app.secret_key = 'my-secret-key'

# make `session` available in all Jinja templates
@app.context_processor
def inject_session():
    return {"session": session}

# core pages & APIs
app.register_blueprint(home_bp)
app.register_blueprint(properties_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(auth_bp)

# user‐facing features
app.register_blueprint(user_bookings_bp)
app.register_blueprint(support_bp)
app.register_blueprint(modify_bp)

# host listing management
app.register_blueprint(listings_api)
app.register_blueprint(host_listings_bp)
app.register_blueprint(host_bookings_bp)

# become‐host prompt
app.register_blueprint(become_host_bp)

# chat (API + page)
app.register_blueprint(chat_api)
app.register_blueprint(chat_page_bp)

# reviews (API + page)
app.register_blueprint(reviews_api)
app.register_blueprint(reviews_page_bp)

if __name__ == '__main__':
    app.run(debug=True)
