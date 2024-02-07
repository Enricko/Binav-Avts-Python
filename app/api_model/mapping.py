from flask_restx import fields, reqparse
import werkzeug
from app.extensions import api
from app.api_model.client import client_model

mapping_model = api.model(
    "Mapping",
    {
        "id_client": fields.String,
        "id_mapping": fields.Integer,
        "name": fields.String,
        "file": fields.String,
        "status": fields.Boolean,
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "client":fields.Nested(client_model),
    }
)

get_mapping_model = api.model(
    "List Mapping",
    {
        "message": fields.String,
        "status": fields.Integer,
        "perpage": fields.Integer,
        "page": fields.Integer,
        "total": fields.Integer,
        "data": fields.List(fields.Nested(mapping_model)),
    },
)

insert_mapping_parser = reqparse.RequestParser()
insert_mapping_parser.add_argument("id_client", type=str)
insert_mapping_parser.add_argument("name", type=str)
insert_mapping_parser.add_argument("file", type=werkzeug.datastructures.FileStorage, location='files')
insert_mapping_parser.add_argument("status", type=str)

update_mapping_parser = reqparse.RequestParser()
update_mapping_parser.add_argument("name", type=str)
update_mapping_parser.add_argument("file", type=werkzeug.datastructures.FileStorage, location='files')
update_mapping_parser.add_argument("status", type=str)