from flask import Flask
from routes.home import home_bp
from routes.properties import properties_bp

app = Flask(
    __name__,
    template_folder='../client/templates',
    static_folder='../client/static'
)

app.register_blueprint(home_bp)
app.register_blueprint(properties_bp)

if __name__ == '__main__':
    app.run(debug=True)