from flask import Blueprint, request, jsonify
from config.blocklist import BLOCKLIST
from app.controller.auth import Auth
from app.controller.client import ClientController
from database.database import db
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity

bp = Blueprint("main", __name__)


# Route for user login
@bp.route("/login", methods=["POST"])
def login():
    return Auth.login(db)


@bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200


# Get user data by JWT token
@bp.route("/user", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(user=current_user), 200


# Creating client user
@bp.route("/insert_client", methods=["POST"])
def create_client_user():
    return ClientController.create(db)

# Creating client user
@bp.route("/update_client", methods=["PUT"])
def update_client_user():
    return ClientController.update(db)
