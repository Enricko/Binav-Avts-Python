from flask_restx import fields, reqparse
from app.extensions import api
from app.api_model.user import user_model

pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("page", type=int, default=1, help="Page number")
pagination_parser.add_argument("per_page", type=int, default=10, help="Items per page")



client_model = api.model(
    "Client",
    {
        "id_client": fields.String,
        "status": fields.Boolean,
        "user": fields.Nested(user_model),
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime
    },
)

get_client_model = api.model(
    "List Client",
    {
        "message": fields.String,
        "status": fields.Integer,
        "perpage": fields.Integer,
        "page": fields.Integer,
        "total": fields.Integer,
        "data": fields.List(fields.Nested(client_model)),
    },
)

insert_client_parser = reqparse.RequestParser()
insert_client_parser.add_argument("name", type=str)
insert_client_parser.add_argument("email", type=str)
insert_client_parser.add_argument("status", type=str)
insert_client_parser.add_argument("password", type=str)
insert_client_parser.add_argument("password_confirmation", type=str)

# insert_client_model = api.model(
#     "InsertClient",
#     {
#         "name": fields.String,
#         "email": fields.String,
#         "status": fields.Boolean,
#         "password": fields.String,
#         "password_confirmation": fields.String,
#     },
# )

update_client_parser = reqparse.RequestParser()
update_client_parser.add_argument("name", type=str)
update_client_parser.add_argument("email", type=str)
update_client_parser.add_argument("status", type=str)
