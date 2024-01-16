from flask import app, jsonify
from flask_jwt_extended import JWTManager

from config.blocklist import BLOCKLIST


jwt = JWTManager(app)

# Error Handler 
@jwt.invalid_token_loader
def invalid_token_response(callback):
    return jsonify({"message": "Invalid token"}), 401


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"message": "Missing Authorization Header"}), 401


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "Token has been revoked"}),
        401,
    )