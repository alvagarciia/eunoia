from flask import Flask
from dotenv import load_dotenv 
import os

def create_app():
    load_dotenv()  # Load secrets from .env
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev")

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app