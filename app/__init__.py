from importlib import import_module
from flask import Flask

from .extensions import api, db, socketio
from .resources import ns
import os
from datetime import timedelta
from dotenv import load_dotenv


def import_all_modules():
    model_folder = os.path.join(os.path.dirname(__file__), "model")

    # Dynamically import all modules in the "model" folder
    for file in os.listdir(model_folder):
        if file.endswith(".py") and file != "__init__.py":
            module_name = file[:-3]
            module = import_module(f"app.model.{module_name}")
            globals()[module_name] = module


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"{os.getenv('DB_CONNECTION')}+mysqlconnector://{os.getenv('DB_USERNAME')}@localhost/{os.getenv('DB_DATABASE')}"
    app.config["DEBUG"] = os.getenv("DEBUG")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=int(os.getenv("JWT_EXPIRE_TOKEN", 4800))
    )
    api.init_app(app)
    db.init_app(app)
    socketio.init_app(app)

    api.add_namespace(ns)

    import_all_modules()

    with app.app_context():
        db.create_all()

    return app
