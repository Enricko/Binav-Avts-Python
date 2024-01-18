from app.extensions import db, generate_random_string
from app.model.user import User
from app.model.client import Client
from flask_restx import Resource, reqparse
from app.api_model.client import (
    get_client_model,
    insert_client_parser,
    update_client_parser,
)
from app.resources import ns

# Pagination parameters
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("page", type=int, help="Page number", default=1)
pagination_parser.add_argument("per_page", type=int, help="Items per page", default=10)


@ns.route("/client")
class ClientList(Resource):
    @ns.marshal_list_with(get_client_model)
    @ns.expect(pagination_parser)
    def get(self):
        args = pagination_parser.parse_args()
        page = args["page"]
        per_page = args["per_page"]
        offset = (page - 1) * per_page

        total_count = Client.query.count()

        client = Client.query.offset(offset).limit(per_page).all()

        return {
            "message": "Data Client Ditemukan",
            "status": 200,
            "page": page,
            "perpage": per_page,
            "total": total_count,
            "data": client,
        }, 200

    @ns.expect(insert_client_parser)
    def post(self):
        try:
            args = insert_client_parser.parse_args()

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
                password_string=f"{name}-{password}-{email}",
                level="client",
            )
            new_client = Client(id_client=id_client, id_user=id_user, status=status)
            new_user.set_password(password, password_confirmation)

            db.session.add(new_client)
            db.session.add(new_user)
            db.session.commit()
            return (
                {"message": "Client successfully created."},
                201,
            )
        except AssertionError as exception_message:
            return {"message": "{}.".format(str(exception_message))}, 400
        except TypeError as e:
            db.session.rollback()
            return {"message": str(e)}, 404


@ns.route("/client/<string:id_client>")
class ClientData(Resource):
    
    @ns.marshal_list_with(get_client_model)
    def get(self,id_client):

        total_count = Client.query.count()

        client = Client.query.get(id_client)

        return {
            "message": "Data Client Ditemukan",
            "status": 200,
            "total": total_count,
            "data": client,
        }, 200
        
    @ns.expect(update_client_parser)
    def put(self, id_client):
        try:
            args = update_client_parser.parse_args()

            name = args["name"]
            email = args["email"]
            status = args["status"]

            client_user = (
                db.session.query(Client, User)
                .join(User)
                .filter(Client.id_client == id_client)
                .first()
            )

            if client_user is None:
                raise TypeError("Client not found")

            client, user = client_user

            split_password = user.password_string.split("-")
            split_password[0] = str(name)
            split_password[2] = str(email)
            password_string = "-".join(split_password)

            user.name = name
            user.email = email
            client.status = status
            user.password_string = password_string
            db.session.commit()

            return {"message": "Client successfully updated."}, 201

        except AssertionError as exception_message:
            db.session.rollback()
            return {"message": "{}.".format(str(exception_message))}, 400
        except TypeError as e:
            db.session.rollback()
            return {"message": str(e)}, 404

    def delete(self, id_client):
        try:
            client = Client.query.get(id_client)
            user = User.query.get(client.id_user)
            db.session.delete(client)
            db.session.delete(user)
            db.session.commit()

            return {"message": "Client successfully deleted."}, 201

        except AssertionError as exception_message:
            db.session.rollback()
            return {"message": "{}.".format(str(exception_message))}, 400
        except TypeError as e:
            db.session.rollback()
            return {"message": str(e)}, 404
