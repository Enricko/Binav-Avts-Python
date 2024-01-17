from app.model.user import User
from flask_restx import Resource, reqparse
from app.api_model.user import user_model
from ..resources import ns

@ns.route("/hello")
class Hello(Resource):
    def get(self):
        return {"hello": "world"}


@ns.route("/user")
class UserList(Resource):
    @ns.marshal_list_with(user_model)
    def get(self):
        return User.query.all()