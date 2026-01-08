from flask import Flask
from config import Config
from extensions import db, bcrypt, jwt, cors
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.dashboard import dashboard_bp
import os

def create_app(test_config: dict = None):
    app = Flask(__name__)
    # Load default config, then allow tests to override via test_config
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)


    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    app.register_blueprint(profile_bp, url_prefix="/api/profile")

    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")


    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return {"status": "Backend + DB running successfully"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
