from app.extensions import db, generate_random_string
from app.model.user import User
from app.model.client import Client
from flask_restx import Resource, reqparse
from app.api_model.client import client_model
from ..resources import ns

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="Name from form data")
parser.add_argument("email", type=str, help="Email from form data")
parser.add_argument("status", type=bool, help="Status from form data")
parser.add_argument("password", type=str, help="Password from form data")
parser.add_argument(
    "password_confirmation", type=str, help="Password confirmation from form data"
)


@ns.route("/client")
class ClientList(Resource):
    @ns.marshal_list_with(client_model)
    def get(self):
        return Client.query.all()

    @ns.expect(parser)
    def post(self):
        try:
            args = parser.parse_args()

            id_client = generate_random_string(35)
            id_user = generate_random_string(35)
            name = args["name"]
            email = args["email"]
            status = args["status"]
            password = args["password"]
            password_confirmation = args["password_confirmation"]
            # Create a new client

            # Create a new user associated with the client
            new_user = User(
                id_user=id_user,
                name=name,
                email=email,
                password_string=f"{name}{password}{email}",
                level="client",
            )
            new_client = Client(id_client=id_client, id_user=id_user, status=status)
            new_user.set_password(password, password_confirmation)

            db.session.add(new_client)
            db.session.add(new_user)
            db.session.commit()
            return (
                {"message": "Client successfully created"},
                200,
            )
        except AssertionError as exception_message:
            return {"message": "{}.".format(str(exception_message))}, 400
