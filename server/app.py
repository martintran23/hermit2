from flask import Flask
from server.routes.home import home_bp
from server.routes.properties import properties_bp
from server.routes.api.bookings import bookings_bp

app = Flask(
    __name__,
    template_folder='../client/templates',
    static_folder='../client/static'
)

# register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(properties_bp)
app.register_blueprint(bookings_bp)

if __name__ == '__main__':
    app.run(debug=True)
