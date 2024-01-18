from app.extensions import db, generate_random_string
from flask_restx import Resource, reqparse
from app.api_model.client import (
    client_model,
    insert_client_parser,
    update_client_parser,
)
from app.resources import ns

@ns.route("/kapal")
class Hello(Resource):
    def get(self):
        return {"hello": "world"}
