from flask_restx import fields, reqparse
import werkzeug
from app.extensions import api


kapal_model = api.model(
    "Kapal",
    {
        "id_client": fields.String,
        "call_sign": fields.String,
        "flag": fields.String,
        "kelas": fields.String,
        "builder": fields.String,
        "size": fields.String,
        "status": fields.Boolean,
        "xml_file": fields.Url,
        "year_built": fields.String,
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime
    }
)

get_kapal_model = api.model(
    "List Kapal",
    {
        "message": fields.String,
        "status": fields.Integer,
        "perpage": fields.Integer,
        "page": fields.Integer,
        "total": fields.Integer,
        "data": fields.List(fields.Nested(kapal_model)),
    },
)

insert_client_parser = reqparse.RequestParser()
insert_client_parser.add_argument("call_sign", type=str)
insert_client_parser.add_argument("id_client", type=str)
insert_client_parser.add_argument("flag", type=str)
insert_client_parser.add_argument("kelas", type=str)
insert_client_parser.add_argument("builder", type=str)
insert_client_parser.add_argument("year_built", type=str)
insert_client_parser.add_argument("size", type=str,choices=('small', 'medium', 'large', 'extra_large'))
insert_client_parser.add_argument("builder", type=str)
insert_client_parser.add_argument("xml_file", type=werkzeug.datastructures.FileStorage, location='files')
insert_client_parser.add_argument("status", type=bool)