from flask_restx import fields
from app.extensions import api

user_model = api.model("Users",{
    "id_user": fields.String,
    "name": fields.String,
    "email": fields.String,
    "level": fields.String,
})