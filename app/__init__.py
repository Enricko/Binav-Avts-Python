from flask import Flask

from .extensions import api, db
from .resources import ns
import os
from datetime import timedelta
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"{os.getenv('DB_CONNECTION')}+mysqlconnector://{os.getenv('DB_USERNAME')}@localhost/{os.getenv('DB_DATABASE')}"
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=int(os.getenv("JWT_EXPIRE_TOKEN", 4800))
    )
    api.init_app(app)
    db.init_app(app)
    
    api.add_namespace(ns)

    return app
