import os
from flask import render_template
from flask_jwt_extended import jwt_required
from app.extensions import api_handle_exception, db, generate_random_string, mail
from app.model.user import User
from app.model.client import Client
from flask_restx import Resource, reqparse
from sqlalchemy.exc import IntegrityError
from app.api_model.client import (
    get_client_model,
    insert_client_parser,
    update_client_parser,
)
from app.resources import ns
from flask_mail import Message

# Pagination parameters
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("page", type=int, help="Page number", default=1)
pagination_parser.add_argument("per_page", type=int, help="Items per page", default=10)


@ns.route("/client")
class ClientList(Resource):
    @ns.marshal_list_with(get_client_model)
    @ns.expect(pagination_parser)
    @api_handle_exception
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
    @api_handle_exception
    def post(self):
        args = insert_client_parser.parse_args()

        id_client = generate_random_string(35)
        id_user = generate_random_string(35)
        name = args["name"]
        email = args["email"]
        status = str(args["status"]).lower() == "true"
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
            {
                "message": "Client successfully created.",
                "status": 201,
            },
            201,
        )


@ns.route("/client/<string:id_client>")
class ClientData(Resource):

    @ns.marshal_list_with(get_client_model)
    @api_handle_exception
    def get(self, id_client):

        total_count = Client.query.count()

        client = Client.query.get(id_client)

        return {
            "message": "Data Client Ditemukan",
            "status": 200,
            "total": total_count,
            "data": client,
        }, 200

    @ns.expect(update_client_parser)
    @api_handle_exception
    def put(self, id_client):
        args = update_client_parser.parse_args()

        name = args["name"]
        email = args["email"]
        status = str(args["status"]).lower() == "true"

        client_user = (
            db.session.query(Client, User)
            .join(User)
            .filter(Client.id_client == id_client)
            .first()
        )

        if client_user is None:
            raise TypeError("Client not found")

        client, user = client_user

        password_string = user.password_string.replace(user.name, "", 1).replace(
            user.email, "", 1
        )

        user.name = name
        user.email = email
        client.status = status
        user.password_string = password_string
        db.session.commit()

        return {
            "message": "Client successfully updated.",
            "status": 201,
        }, 201

    @api_handle_exception
    def delete(self, id_client):
        client = Client.query.get(id_client)
        if client:
            user = User.query.get(client.id_user)
            db.session.delete(client)
            db.session.delete(user)
            db.session.commit()

            return {
                "message": "Client successfully deleted.",
                "status": 201,
            }, 201
        return {
            "message": "Client not found.",
            "status": 404,
        }, 404


@ns.route("/client_email/<string:id_client>")
class ClientData(Resource):

    @api_handle_exception
    def get(self, id_client):
        client_user = (
            db.session.query(Client, User)
            .join(User)
            .filter(Client.id_client == id_client)
            .first()
        )

        if client_user is None:
            raise TypeError("Client not found")

        client, user = client_user
        get_password = user.password_string.replace(user.name, "", 1).replace(
            user.email, "", 1
        )
        msg = Message(
            "Binav AVTS Account Details",
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[user.email],
        )
        msg.html = render_template(
            "email_client_detail.html", client=client, user=user, password=get_password
        )
        mail.send(msg)

        return {"message": "Email sent successfully.", "status": 200}, 200
