import random
import string
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

api = Api()
db = SQLAlchemy()

def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # includes both uppercase and lowercase letters and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string