import random
from flask_socketio import SocketIO
import string
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


api = Api()
db = SQLAlchemy()
socketio = SocketIO()


def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # includes both uppercase and lowercase letters and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def api_handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except AssertionError as exception_message:
            db.session.rollback()
            return {"message": "{}.".format(str(exception_message))}, 400
        except TypeError as e:
            db.session.rollback()
            return {"message": str(e)}, 404
        except AttributeError as e:  # noqa: F841
            db.session.rollback()
            return {"message": "Data not found"}, 404
        except IntegrityError as e:
            db.session.rollback()
            return {"message": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500
        finally:
            db.session.close()
            
    return wrapper