from os import name
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_socketio import emit, join_room, leave_room
from socketio import Namespace
from app.extensions import socketio, db, app, scheduler
from app.model.coordinate_gga import CoordinateGGA
from app.model.coordinate_hdt import CoordinateHDT
from app.model.coordinate_vtg import CoordinateVTG
from app.model.coordinate import Coordinate
import datetime

from app.model.kapal import Kapal
from app.model.mapping import Mapping

# Dictionary to store user sessions
user_kapal_session = {}


def socketrun1second():
    with app.app_context():
        pass
        # socketio.emit("kapal_coor", self.kapal_coor_data())


class KapalSocket:
    namespace = "/kapal"

    @socketio.on("connect", namespace=namespace)
    def handle_connect():
        with app.app_context():
            user_id = request.sid
            user_kapal_session[user_id] = {}
            user_kapal_session[user_id]["payload"] = {}

            name_event = request.args.get("name_event", "kapal_coor")

            call_sign = request.args.get("call_sign", None)
            if call_sign is not None:
                if Kapal.query.get(call_sign) is None:
                    return False
                user_kapal_session[user_id]["payload"]["call_sign"] = call_sign

            join_room(user_id)

            KapalSocket.handle_kapal_coordinate(
                user_kapal_session[user_id]["payload"], user_id, name_event
            )

            user_kapal_session[user_id]["job"] = scheduler.add_job(
                KapalSocket.handle_kapal_coordinate,
                "interval",
                seconds=5,
                args=[user_kapal_session[user_id]["payload"], user_id, name_event],
            ).id

    @socketio.on("disconnect", namespace=namespace)
    def handle_disconnect():
        user_id = request.sid
        leave_room(user_id)
        scheduler.remove_job(user_kapal_session[user_id]["job"])
        del user_kapal_session[user_id]
        print(f"User {user_id} disconnected")

    @socketio.on("kapal_coordinate", namespace=namespace)
    def handle_kapal_coordinate(payload, user_id=None, name_event="kapal_coor"):
        with app.app_context():
            if user_id is None:
                user_id = request.sid
            if payload is not None:
                user_kapal_session[user_id]["payload"] = payload
            socketio.emit(
                name_event,
                KapalSocket.kapal_coor_data(user_kapal_session[user_id]["payload"]),
                room=user_id,
                namespace=KapalSocket.namespace,
            )

    def kapal_coor_data(payload={}):
        if payload is None:
            payload = {}

        call_sign = payload.get("call_sign", None)
        page = payload.get("page", 1)
        perpage = payload.get("perpage", 1000)
        offset = (page - 1) * perpage

        latest_series_id_subquery = (
            db.session.query(
                Coordinate.call_sign,
                db.func.max(Coordinate.series_id).label("max_series_id"),
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
            .outerjoin(
                CoordinateGGA, Coordinate.id_coor_gga == CoordinateGGA.id_coor_gga
            )
            .outerjoin(
                CoordinateHDT, Coordinate.id_coor_hdt == CoordinateHDT.id_coor_hdt
            )
            .outerjoin(
                CoordinateVTG, Coordinate.id_coor_vtg == CoordinateVTG.id_coor_vtg
            )
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
            "message": "Data telah ditemukan",
            "status": 200,
            "perpage": perpage,
            "page": page,
            "total": kapal_coor.count(),
            "data": [
                {
                    "id_client": getattr(kapal, "id_client", None),
                    "call_sign": getattr(kapal, "call_sign", None),
                    "flag": getattr(kapal, "flag", None),
                    "kelas": getattr(kapal, "kelas", None),
                    "builder": getattr(kapal, "builder", None),
                    "status": getattr(kapal, "status", None),
                    "size": getattr(kapal, "size", None),
                    "year_built": getattr(kapal, "year_built", None),
                    "xml_file": getattr(kapal, "xml_file", None),
                    "coor": {
                        "id_coor": getattr(coor, "id_coor", None),
                        "default_heading": getattr(coor, "default_heading", None),
                        "coor_gga": {
                            "latitude": getattr(coor_gga, "latitude", None),
                            "longitude": getattr(coor_gga, "longitude", None),
                        },
                        "coor_hdt": {
                            "id_coor_hdt": getattr(coor_hdt, "id_coor_hdt", None),
                            "heading_degree": getattr(coor_hdt, "heading_degree", None),
                        },
                    },
                }
                for coor, kapal, coor_gga, coor_hdt, coor_vtg in (
                    kapal_coor_page.all()
                    if call_sign is None
                    else kapal_coor.filter(Kapal.call_sign == call_sign).all()
                )
                # for kapal,coor_gga,coor_hdt,coor_vtg in (kapal_coor_page.all() if call_sign is None else kapal_coor.filter(Kapal.call_sign == call_sign).all())
            ],
        }
        return data_json


user_mapping_session = {}


class MappingSocket:
    namespace = "/mapping"

    @socketio.on("connect", namespace=namespace)
    def handle_connect():
        with app.app_context():
            user_id = request.sid
            user_mapping_session[user_id] = {}
            user_mapping_session[user_id]["payload"] = {}

            name_event = request.args.get("name_event", "mapping")

            id_mapping = request.args.get("id_mapping", None)
            if id_mapping is not None:
                if Mapping.query.get(id_mapping) is None:
                    return False
                user_mapping_session[user_id]["payload"]["id_mapping"] = id_mapping

            join_room(user_id)

            MappingSocket.handle_mapping(
                user_mapping_session[user_id]["payload"], user_id, name_event
            )

            user_mapping_session[user_id]["job"] = scheduler.add_job(
                MappingSocket.handle_mapping,
                "interval",
                seconds=30,
                args=[user_mapping_session[user_id]["payload"], user_id, name_event],
            ).id

    @socketio.on("disconnect", namespace=namespace)
    def handle_disconnect():
        user_id = request.sid
        leave_room(user_id)
        scheduler.remove_job(user_mapping_session[user_id]["job"])
        del user_mapping_session[user_id]
        print(f"User {user_id} disconnected")

    @socketio.on("mapping", namespace=namespace)
    def handle_mapping(payload, user_id=None, name_event="mapping"):
        with app.app_context():
            if user_id is None:
                user_id = request.sid
            if payload is not None:
                user_mapping_session[user_id]["payload"] = payload
            socketio.emit(
                name_event,
                MappingSocket.mapping_data(user_mapping_session[user_id]["payload"]),
                room=user_id,
                namespace=MappingSocket.namespace,
            )

    def mapping_data(payload={}):
        if payload is None:
            payload = {}

        id_mapping = payload.get("id_mapping", None)
        page = payload.get("page", 1)
        perpage = payload.get("perpage", 1000)
        offset = (page - 1) * perpage

        mapping = Mapping.query

        mapping_page = mapping.offset(offset).limit(perpage)
        data_json = {
            "message": "Data telah ditemukan",
            "status": 200,
            "perpage": perpage,
            "page": page,
            "total": mapping.count(),
            "data": [
                {
                    "id_client": getattr(map, "id_client", None),
                    "id_mapping": getattr(map, "id_mapping", None),
                    "name": getattr(map, "name", None),
                    "file": getattr(map, "file", None),
                    "status": getattr(map, "status", None),
                }
                for map in (
                    mapping_page.all()
                    if id_mapping is None
                    else mapping.filter(Mapping.id_mapping == id_mapping).all()
                )
            ],
        }
        return data_json
