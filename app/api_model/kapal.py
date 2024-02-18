from flask_restx import fields, reqparse
import werkzeug
from app.extensions import api
from app.api_model.client import client_model


kapal_model = api.model(
    "Kapal",
    {
        "call_sign": fields.String,
        "flag": fields.String,
        "kelas": fields.String,
        "builder": fields.String,
        "size": fields.String,
        "status": fields.Boolean,
        "xml_file": fields.String,
        "year_built": fields.String,
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "client": fields.Nested(client_model),
    },
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

ip_kapal_model = api.model(
    "Ip Kapal",
    {
        "id_ip_kapal": fields.Integer,
        "call_sign": fields.String,
        "type_ip": fields.String,
        "ip": fields.String,
        "port": fields.Integer,
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
    },
)

get_ip_kapal_model = api.model(
    "List Ip Kapal",
    {
        "message": fields.String,
        "status": fields.Integer,
        "total": fields.Integer,
        "data": fields.List(fields.Nested(ip_kapal_model)),
    },
)

# Insert Kapal
insert_kapal_parser = reqparse.RequestParser()
insert_kapal_parser.add_argument("call_sign", type=str)
insert_kapal_parser.add_argument("id_client", type=str)
insert_kapal_parser.add_argument("flag", type=str)
insert_kapal_parser.add_argument("kelas", type=str)
insert_kapal_parser.add_argument("builder", type=str)
insert_kapal_parser.add_argument("year_built", type=str)
insert_kapal_parser.add_argument(
    "size", type=str, choices=("small", "medium", "large", "extra_large")
)
insert_kapal_parser.add_argument("builder", type=str)
insert_kapal_parser.add_argument(
    "xml_file", type=werkzeug.datastructures.FileStorage, location="files"
)
insert_kapal_parser.add_argument("status", type=str)

# Update Kapal
update_kapal_parser = reqparse.RequestParser()
update_kapal_parser.add_argument("new_call_sign", type=str)
update_kapal_parser.add_argument("flag", type=str)
update_kapal_parser.add_argument("kelas", type=str)
update_kapal_parser.add_argument("builder", type=str)
update_kapal_parser.add_argument("year_built", type=str)
update_kapal_parser.add_argument(
    "size", type=str, choices=("small", "medium", "large", "extra_large")
)
update_kapal_parser.add_argument("builder", type=str)
update_kapal_parser.add_argument(
    "xml_file", type=werkzeug.datastructures.FileStorage, location="files"
)
update_kapal_parser.add_argument("status", type=str)


insert_ip_kapal_parser = reqparse.RequestParser()
insert_ip_kapal_parser.add_argument(
    "type_ip", type=str, choices=("all", "gga", "vtg", "hdt")
)
insert_ip_kapal_parser.add_argument("ip", type=str)
insert_ip_kapal_parser.add_argument("port", type=int)
