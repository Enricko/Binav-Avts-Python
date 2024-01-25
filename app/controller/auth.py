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
from app.api_model.user import get_user_auth_model,otp_parser,otp_code_check_parser
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
        
@ns.route('/forgot-password')
class ForgotPasswordResource(Resource):
    @ns.expect(otp_parser)
    def post(self):
        args = otp_parser.parse_args()

        email = args['email']
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate OTP
            otp_secret = ''.join(random.choices(string.digits, k=6))
            
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
            msg = Message('Forgot Password OTP', sender=os.getenv("MAIL_USERNAME"), recipients=[email])
            msg.html = render_template('otp_email.html', user=user, code=otp_secret)
            mail.send(msg)

            return {'message': f"OTP sent successfully {otp_secret}"},200
        else:
            return {'error': 'User not found'}, 404

def check_otp(user, otp_value):
    if user and user.code:
        otp = pyotp.TOTP(user.code)
        return otp.verify(otp_value)
    return False

@ns.route('/check-code')
class CheckCodeResource(Resource):
    @ns.expect(otp_code_check_parser)
    def post(self):
        args = otp_code_check_parser.parse_args()

        email = args['email']
        otp_code = args['otp_code']
        resetCodePassword = ResetCodePassword.query.filter_by(email=email).first()
        
        if resetCodePassword.code == otp_code:
            return {'message': 'OTP verification successful'},200
        else:
            return {'error': 'Invalid OTP'}, 400