import datetime
import os
import pyotp
import random
import string

from app.extensions import api_handle_exception, db, mail, BLOCKLIST
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    get_jwt,
)
from app.model.reset_code_password import ResetCodePassword
from app.model.user import User
from app.api_model.user import (
    get_user_auth_model,
    otp_parser,
    otp_code_check_parser,
    reset_password_parser,
)
from flask_restx import Resource, reqparse
from app.resources import ns
from flask_mail import Message
from flask import render_template

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
            print("Email123")
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


@ns.route("/forgot-password")
class ForgotPassword(Resource):
    @ns.expect(otp_parser)
    @api_handle_exception
    def post(self):
        args = otp_parser.parse_args()

        email = args["email"]
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate OTP
            otp_secret = "".join(random.choices(string.digits, k=6))

            oldResetCodePassword = ResetCodePassword.query.get(email)
            if oldResetCodePassword:
                db.session.delete(oldResetCodePassword)

            # Save OTP secret to the user
            resetCodePassword = ResetCodePassword(
                email=email,
                code=otp_secret,
            )
            db.session.add(resetCodePassword)
            db.session.commit()

            # Send OTP via email
            msg = Message(
                "Forgot Password OTP",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[email],
            )
            msg.html = render_template("otp_email.html", user=user, code=otp_secret)
            mail.send(msg)

            return {"message": "OTP sent successfully.", "status": 200}, 200
        else:
            return {"message": "User not found.","status":404}, 404


@ns.route("/check-code")
class CheckCode(Resource):
    @ns.expect(otp_code_check_parser)
    @api_handle_exception
    def post(self):
        args = otp_code_check_parser.parse_args()

        email = args["email"]
        otp_code = args["otp_code"]
        resetCodePassword = ResetCodePassword.query.filter_by(email=email).first()

        if resetCodePassword and resetCodePassword.code == otp_code:
            if (
                resetCodePassword.created_at
                < resetCodePassword.created_at + datetime.timedelta(minutes=15)
            ):
                return {"message": "OTP verification successful.", "status": 200}, 200
            else:
                db.session.delete(resetCodePassword)
                db.session.commit()
                return {"message": "OTP Expired.", "status": 403}, 403
        else:
            return {"message": "Invalid OTP.", "status": 400}, 400


@ns.route("/reset-password")
class ResetPassword(Resource):
    @ns.expect(reset_password_parser)
    @api_handle_exception
    def post(self):
        args = reset_password_parser.parse_args()

        email = args["email"]
        otp_code = args["otp_code"]
        password = args["password"]
        password_confirmation = args["password_confirmation"]
        resetCodePassword = ResetCodePassword.query.filter_by(email=email).first()

        if resetCodePassword and resetCodePassword.code == otp_code:
            if (
                resetCodePassword.created_at
                < resetCodePassword.created_at + datetime.timedelta(minutes=15)
            ):
                user = User.query.filter_by(email=email).first()

                user.password_string = f"{user.name}-{password}-{email}"
                user.set_password(password, password_confirmation)
                db.session.delete(resetCodePassword)

                db.session.commit()

                return {"message": "Reset Password successful.", "status": 200}, 200
            else:
                db.session.delete(resetCodePassword)
                db.session.commit()
                return {"message": "OTP Expired.", "status": 201}, 201
        else:
            return {"message": "Invalid OTP.", "status": 400}, 400
