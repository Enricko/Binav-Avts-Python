from flask import json, jsonify
from flask_socketio import emit
from app.extensions import api_handle_exception, socketio
from marshmallow import Schema
import datetime

from app.model.kapal import Kapal


def socketrun1second():
    print("asdasasd")
    emit("message", f"{datetime.datetime.now()}")


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("message")
def handle_message(msg):
    emit("message", msg, broadcast=True)
    emit("message", msg + "asd", broadcast=False)


class KapalSchema(Schema):
    class Meta:
        model = Kapal


@socketio.on("kapal_coordinate")
@api_handle_exception
def handle_kapal_coordinate(payload):
    # Type = ["global","filter"]
    type = payload.get("type", "").lower()
    page = payload.get("page", 1)
    perpage = payload.get("perpage", 10)
    kapal = Kapal.query.all()
    # print([e.serialize() for e in kapal])
    # emit('message', [eserialize() for e in kapal],broadcast=True)

    data_json = {
        "message": "Data di temukan",
        "status": 200,
        "perpage": perpage,
        "page": page,
        "total": len(kapal),
        "data": [
            {
                "id_client": x.id_client,
                "call_sign": x.call_sign,
                "flag": x.flag,
                "kelas": x.kelas,
                "builder": x.builder,
                "size": x.size,
                "status": x.status,
                "xml_file": x.xml_file,
                "year_built": x.year_built,
                "created_at": str(x.created_at),
                "updated_at": str(x.updated_at),
            }
            for x in kapal
        ],
    }

    emit("message", data_json, broadcast=True)
