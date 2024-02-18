from flask_restx import fields, reqparse
from app.extensions import api

user_model = api.model("Users",{
    "id_user": fields.String,
    "id_client":fields.String(required=False, allow_null=True),
    "name": fields.String,
    "email": fields.String,
    "level": fields.String,
})

get_user_auth_model = api.model("Get User Auth",{
    "message": fields.String,
    "status": fields.Integer,
    "data": fields.List(fields.Nested(user_model)),
})

otp_parser = reqparse.RequestParser()
otp_parser.add_argument("email", type=str)

otp_code_check_parser = reqparse.RequestParser()
otp_code_check_parser.add_argument("email", type=str)
otp_code_check_parser.add_argument("otp_code", type=str)

reset_password_parser = reqparse.RequestParser()
reset_password_parser.add_argument("email", type=str)
reset_password_parser.add_argument("otp_code", type=str)
reset_password_parser.add_argument("password", type=str,help='Password field is required')
reset_password_parser.add_argument("password_confirmation", type=str)

change_password_parser = reqparse.RequestParser()
change_password_parser.add_argument("old_password", type=str)
change_password_parser.add_argument("new_password", type=str)
change_password_parser.add_argument("new_password_confirmation", type=str)