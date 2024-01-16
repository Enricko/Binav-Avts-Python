from datetime import timedelta
import os
from flask import Flask, app
from flask_restx import Api

api = Api()

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{os.getenv('DB_CONNECTION')}+mysqlconnector://{os.getenv('DB_USERNAME')}@localhost/{os.getenv('DB_DATABASE')}"
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    seconds=int(os.getenv("JWT_EXPIRE_TOKEN", 4800))
)