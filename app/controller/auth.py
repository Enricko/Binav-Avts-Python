from app.extensions import api_handle_exception, db, jwt, BLOCKLIST
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    get_jwt,
)
from app.model.user import User
from app.api_model.user import get_user_auth_model
from flask_restx import Resource, reqparse
from app.resources import ns

login_parser = reqparse.RequestParser()
login_parser.add_argument("email", type=str, help="Email Address")
login_parser.add_argument("password", type=str, help="Password")


@ns.route("/login")
class AuthLogin(Resource):
    @ns.expect(login_parser)
    @api_handle_exception
    def post(self):
        args = login_parser.parse_args()
        email = args["email"]
        password = args["password"]
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if user.check_password(password):
                # Include additional user data in the identity
                access_token = create_access_token(identity=user.id_user)
                return {
                    "message": f"Welcome Back {user.name.title()}.",
                    "token": access_token,
                    "status": 200,
                }, 200
            else:
                return {
                    "message": "Email & Password are incorrect.",
                    "status": 401,
                }, 401
        else:
            return {
                "message": "Email not found.",
                "status": 404,
            }, 404


@ns.route("/user")
class AuthGet(Resource):
    @ns.marshal_list_with(get_user_auth_model)
    @jwt_required()
    @api_handle_exception
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        return {
            "message": "Successfully get data.",
            "status": 200,
            "data": user,
        }, 200


@ns.route("/logout")
class AuthLogout(Resource):
    @jwt_required()
    @api_handle_exception
    def delete(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {
            "message": "Successfully logged out.",
            "status": 200,
        }, 200
        
