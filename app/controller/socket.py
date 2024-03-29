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

data_kapal_coor = {}


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
        # offset = (page - 1) * perpage

        
        data_json = {
            "message": "Data telah ditemukansfsfd",
            "status": 200,
            "perpage": perpage,
            "page": page,
            "data": [kapal for kapal in (data_kapal_coor.values() if call_sign is None else [data_kapal_coor.get(call_sign)])],
        }
        return data_json


user_kapal_latlong_session = {}


class KapalLatlongSocket:
    namespace = "/kapal-latlong"

    @socketio.on("connect", namespace=namespace)
    def handle_connect():
        with app.app_context():
            user_id = request.sid
            user_kapal_latlong_session[user_id] = {}
            user_kapal_latlong_session[user_id]["payload"] = {}

            name_event = request.args.get("name_event", "kapal_latlong")

            call_sign = request.args.get("call_sign", None)
            if call_sign is not None:
                if Kapal.query.get(call_sign) is None:
                    return False
                user_kapal_latlong_session[user_id]["payload"]["call_sign"] = call_sign

            join_room(user_id)

            KapalLatlongSocket.handle_kapal_latlong(
                user_kapal_latlong_session[user_id]["payload"], user_id, name_event
            )

            user_kapal_latlong_session[user_id]["job"] = scheduler.add_job(
                KapalLatlongSocket.handle_kapal_latlong,
                "interval",
                seconds=5,
                args=[
                    user_kapal_latlong_session[user_id]["payload"],
                    user_id,
                    name_event,
                ],
            ).id

    @socketio.on("disconnect", namespace=namespace)
    def handle_disconnect():
        user_id = request.sid
        leave_room(user_id)
        scheduler.remove_job(user_kapal_latlong_session[user_id]["job"])
        del user_kapal_latlong_session[user_id]
        print(f"User {user_id} disconnected")

    @socketio.on("kapal_latlong", namespace=namespace)
    def handle_kapal_latlong(payload, user_id=None, name_event="kapal_latlong"):
        with app.app_context():
            if user_id is None:
                user_id = request.sid
            if payload is not None:
                user_kapal_latlong_session[user_id]["payload"] = payload
            socketio.emit(
                name_event,
                KapalLatlongSocket.kapal_latlong_data(
                    user_kapal_latlong_session[user_id]["payload"]
                ),
                room=user_id,
                namespace=KapalLatlongSocket.namespace,
            )

    def kapal_latlong_data(payload={}):
        if payload is None:
            payload = {}

        call_sign = payload.get("call_sign", None)
        page = payload.get("page", 1)
        perpage = payload.get("perpage", 1000)
        offset = (page - 1) * perpage

        query_result = (
            db.session.query(Coordinate, CoordinateGGA, CoordinateHDT)
            .join(CoordinateGGA, Coordinate.id_coor_gga == CoordinateGGA.id_coor_gga)
            .join(CoordinateHDT, Coordinate.id_coor_hdt == CoordinateHDT.id_coor_hdt)
            .filter(Coordinate.series_id % 2 != 0)
        )
        if call_sign is not None:
            query_result = query_result.filter(Coordinate.call_sign == call_sign)

        kapal_latlong_page = query_result.offset(offset).limit(perpage)
        data_json = {
            "message": "Data telah ditemukan",
            "status": 200,
            "perpage": perpage,
            "page": page,
            "total": query_result.count(),
            "call_sign": call_sign,
            "data": [
                {
                    "id_coor": getattr(coor, "id_coor", None),
                    "default_heading": getattr(coor, "default_heading", None),
                    "latitude": getattr(coor_gga, "latitude", None),
                    "longitude": getattr(coor_gga, "longitude", None),
                    "heading_degree": getattr(coor_hdt, "heading_degree", None),
                    # "coor_hdt": {
                    #     "id_coor_hdt": getattr(coor_hdt, "id_coor_hdt", None),
                    # },
                }
                for coor, coor_gga, coor_hdt in (kapal_latlong_page.all())
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

