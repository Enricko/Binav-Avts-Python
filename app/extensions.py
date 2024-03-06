import random
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import string
from flask_restx import Api
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from apscheduler.schedulers.background import BackgroundScheduler

# app = Flask(__name__, static_url_path='/assets')
app = Flask(__name__)
api = Api()
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
socketio = SocketIO()
scheduler = BackgroundScheduler()
checked_configs = {}


def generate_random_string(length):
    characters = (
        string.ascii_letters + string.digits
    )  # includes both uppercase and lowercase letters and digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def api_handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except AssertionError as exception_message:
            db.session.rollback()
            print(str(exception_message))
            return {
                "message": "{}.".format(str(exception_message)),
                "status": 400,
            }, 400
        except TypeError as e:
            db.session.rollback()
            print(str(e))
            return {
                "message": str(e),
                "status.": 404,
            }, 404
        except AttributeError as e:  # noqa: F841
            db.session.rollback()
            print(str(e))
            return {
                "message": f"Data not found. {str(e)}",
                "status": 400,
            }, 404
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
            return {
                "message": f"{str(e)}.",
                "status": 500,
            }, 500
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return {
                "message": f"{str(e)}.",
                "status": 500,
            }, 500
        finally:
            db.session.remove()

    return wrapper


BLOCKLIST = set()


# Error Handler


@api_handle_exception
@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "message": "Token has expired.",
                "status": 401,
            }
        ),
        401,
    )


@api_handle_exception
@jwt.invalid_token_loader
def invalid_token_response(callback):
    return (
        jsonify(
            {
                "message": "Invalid token.",
                "status": 401,
            }
        ),
        401,
    )


@api_handle_exception
@jwt.unauthorized_loader
def unauthorized_response(callback):
    return (
        jsonify(
            {
                "message": "Missing Authorization Header.",
                "status": 401,
            }
        ),
        401,
    )


@api_handle_exception
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@api_handle_exception
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "message": "Token has been revoked.",
                "status": 401,
            }
        ),
        401,
    )