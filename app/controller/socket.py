from flask import json, jsonify, current_app
from flask_socketio import emit
from app.extensions import api_handle_exception, socketio, db, app
from marshmallow import Schema
import datetime
from app.model.coordinate_gga import CoordinateGGA
from app.model.coordinate_hdt import CoordinateHDT
from app.model.coordinate_vtg import CoordinateVTG
from app.model.coordinate import Coordinate

from app.model.kapal import Kapal


def socketrun1second():
    with app.app_context():
        socketio.emit("kapal_coor", kapal_coor_data())


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("kapal_coor", kapal_coor_data(), broadcast=False)
    
@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("message")
def handle_message(msg):
    emit("message", msg, broadcast=True)
    emit("message", msg + "asd", broadcast=False)


@socketio.on("kapal_coordinate")
def handle_kapal_coordinate(payload):
    emit("kapal_coor", kapal_coor_data(payload), broadcast=True)


# @api_handle_exception
def kapal_coor_data(payload={}):
    call_sign = payload.get("call_sign", None)
    page = payload.get("page", 1)
    perpage = payload.get("perpage", 100)
    offset = (page - 1) * perpage

    # kapal_coor = db.session.query(Kapal, CoordinateGGA,CoordinateHDT,CoordinateVTG).outerjoin(CoordinateGGA).outerjoin(CoordinateHDT).outerjoin(CoordinateVTG)
    latest_series_id_subquery = (
        db.session.query(
            Coordinate.call_sign,
            db.func.max(Coordinate.series_id).label("max_series_id")
        )
        .group_by(Coordinate.call_sign)
        .subquery()
    )
    kapal_coor = (
        db.session.query(
            Coordinate,
            Kapal,
            CoordinateGGA,
            CoordinateHDT,
            CoordinateVTG,
        )
        .outerjoin(Kapal, Coordinate.call_sign == Kapal.call_sign)
        .outerjoin(CoordinateGGA, Coordinate.id_coor_gga == CoordinateGGA.id_coor_gga)
        .outerjoin(CoordinateHDT, Coordinate.id_coor_hdt == CoordinateHDT.id_coor_hdt)
        .outerjoin(CoordinateVTG, Coordinate.id_coor_vtg == CoordinateVTG.id_coor_vtg)
        .join(
            latest_series_id_subquery,
            db.and_(
                Coordinate.call_sign == latest_series_id_subquery.c.call_sign,
                Coordinate.series_id == latest_series_id_subquery.c.max_series_id,
            ),
        )
    )
    
    kapal_coor_page = kapal_coor.offset(offset).limit(perpage)
    
    data_json = {
        "message": "Data di temukan",
        "status": 200,
        "perpage": perpage,
        "page": page,
        "total": kapal_coor.count(),
        "data": [
            {
                "id_client": getattr(kapal,"id_client",None),
                "call_sign": getattr(kapal, "call_sign", None),
                "flag": getattr(kapal, "flag", None),
                "kelas": getattr(kapal, "kelas", None),
                "size": getattr(kapal, "size", None),
                "status": getattr(kapal, "status", None),
                "id_coor": getattr(coor, "id_coor", None),
                "coor_gga": {
                    "latitude": getattr(coor_gga, "latitude", None),
                    "longitude": getattr(coor_gga, "longitude", None),
                },
                "coor_hdt":{
                    "id_coor_hdt":getattr(coor_hdt,"id_coor_hdt",None),
                    "heading_degree":getattr(coor_hdt,"heading_degree",None)
                }
            }
            for coor, kapal, coor_gga, coor_hdt, coor_vtg in (kapal_coor_page.all() if call_sign is None else kapal_coor.filter(Kapal.call_sign == call_sign).all())
            # for kapal,coor_gga,coor_hdt,coor_vtg in (kapal_coor_page.all() if call_sign is None else kapal_coor.filter(Kapal.call_sign == call_sign).all())
        ],
    }
    return data_json
