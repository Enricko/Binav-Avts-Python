from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, decode_token


from database.database import User

class Auth:
    def login(db):
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Include additional user data in the identity
            access_token = create_access_token(identity=user.id_user)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"message": "Email & Password are incorrect"}), 401
    

