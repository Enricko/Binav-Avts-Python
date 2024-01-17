from flask_restx import fields, reqparse
from app.extensions import api
from app.api_model.user import user_model


client_model = api.model(
    "Client",
    {
        "id_client": fields.String,
        "status": fields.Boolean,
        "user": fields.Nested(user_model),
    },
)

insert_client_parser = reqparse.RequestParser()
insert_client_parser.add_argument("name", type=str)
insert_client_parser.add_argument("email", type=str)
insert_client_parser.add_argument("status", type=bool)
insert_client_parser.add_argument("password", type=str)
insert_client_parser.add_argument("password_confirmation", type=str)

insert_client_model = api.model(
    "InsertClient",
    {
        "name": fields.String,
        "email": fields.String,
        "status": fields.Boolean,
        "password": fields.String,
        "password_confirmation": fields.String,
    },
)

update_client_parser = reqparse.RequestParser()
update_client_parser.add_argument("name", type=str)
update_client_parser.add_argument("email", type=str)
update_client_parser.add_argument("status", type=bool)
