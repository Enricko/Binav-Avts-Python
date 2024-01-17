from flask_restx import fields
from app.extensions import api
from app.api_model.user import user_model

client_model = api.model(
    "Client",
    {
        "id_client": fields.String,
        "status": fields.String,
        "user": fields.Nested(user_model),
    },
)

insert_client_model = api.model(
    "InsertClient",
    {
        "status": fields.Boolean,
        "name": fields.String,
        "email": fields.String,
        "password": fields.String,
        "password_confirmation": fields.String,
    },
)
