from email import message
from flask import jsonify, request
from database.database import Client, User
from system.password import hash_password
from system.randomize import generate_random_string


class ClientController():
    def create(db):
        id_client = generate_random_string(35)
        id_user = generate_random_string(35)
        status = request.form.get("status") == 'true'
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        try: 
            # Create a new client
            new_client = Client(id_client=id_client, id_user=id_user,status=status)

            # Create a new user associated with the client
            new_user = User(
                id_user=id_user,
                name=name,
                email=email,
                password_string=f"{name}{password}{email}",
                level="client",
            )
            new_user.set_password(password) 

            db.session.add(new_client)
            db.session.add(new_user)
            db.session.commit() 
            return jsonify(message='Client successfully created', user_id=new_user.id_user), 200 
        except AssertionError as exception_message: 
            return jsonify(message='{}. '.format(exception_message)), 400
        
    def update(db):
        id_client = request.form.get("id_client") 
        id_user = request.form.get("id_client") 
        status = request.form.get("status") == 'true'
        name = request.form.get("name")
        email = request.form.get("email")
        
        try: 
            user = User.query.get(id_user)
            client = Client.query.get(id_client)
            user.name=name,
            user.email=email,
            client.status=status
            db.session.commit() 
            return jsonify(message='Client successfully updated'), 200 
        except AssertionError as exception_message: 
            return jsonify(message='{}. '.format(exception_message)), 400