from datetime import datetime, timedelta
import math
import telnetlib
import time
from app.controller.socket import data_kapal_coor
from app.extensions import app, db, checked_configs
from app.model.coordinate import Coordinate
from app.model.coordinate_gga import CoordinateGGA
from app.model.coordinate_hdt import CoordinateHDT
from app.model.coordinate_vtg import CoordinateVTG
import logging

from app.model.kapal import Kapal


def telnet_worker(ip, port, call_sign, type_ip):
    while True:
        with app.app_context():
            try:
                if checked_configs != {} and (ip, port) not in checked_configs.keys():
                    checked_configs.pop((ip, port))
                    break
                set_kapal_coor_data(call_sign)
                with telnetlib.Telnet(ip, port) as tn:
                    while True:
                        try:
                            data = tn.read_until(b"\n").decode("ascii").strip()
                            if (
                                checked_configs != {}
                                and (ip, port) not in checked_configs.keys()
                            ):
                                checked_configs.pop((ip, port))
                                break
                            if not data:
                                break  # Exit the inner loop if no data is available
                            if ("GGA" in data) and (
                                type_ip == "gga" or type_ip == "all"
                            ):
                                handle_gngga_message(data, call_sign)
                                change_socket_data(call_sign, "coor_gga", data)
                            elif ("HDT" in data) and (
                                type_ip == "hdt" or type_ip == "all"
                            ):
                                handle_gnhdt_message(data, call_sign)
                                change_socket_data(call_sign, "coor_hdt", data)
                            elif ("VTG" in data) and (
                                type_ip == "vtg" or type_ip == "all"
                            ):
                                handle_gnvtg_message(data, call_sign)
                                change_socket_data(call_sign, "coor_vtg", data)
                        except Exception as e:
                            logging.info(
                                f"Error in telnet connection to {ip}:{port}: {e}"
                            )
                            break
            except EOFError:
                logging.info(f"Connection closed by the remote host: {ip}:{port}")
            except Exception as e:
                logging.info(f"Error in telnet connection to {ip}:{port}: {e}")
            time.sleep(5)  # Delay for 5 seconds before reading again


def set_kapal_coor_data(call_sign):
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

    coor, kapal, coor_gga, coor_hdt, coor_vtg = kapal_coor.filter(
        Kapal.call_sign == call_sign
    ).first()
    print(getattr(coor, "id_coor", None))
    data_kapal_coor[call_sign] = {
        "telnet_status": False,
        "id_client": getattr(kapal, "id_client", None),
        "call_sign": getattr(kapal, "call_sign", None),
        "flag": getattr(kapal, "flag", None),
        "kelas": getattr(kapal, "kelas", None),
        "builder": getattr(kapal, "builder", None),
        "status": getattr(kapal, "status", None),
        "size": getattr(kapal, "size", None),
        "year_built": getattr(kapal, "year_built", None),
        "xml_file": getattr(kapal, "xml_file", None),
        "image": getattr(kapal, "image", None),
        "coor": {
            "id_coor": getattr(coor, "id_coor", None),
            "default_heading": getattr(coor, "default_heading", None),
            "coor_gga": {
                "latitude": getattr(coor_gga, "latitude", None),
                "longitude": getattr(coor_gga, "longitude", None),
                "gps_quality_indicator": getattr(
                    coor_gga, "gps_quality_indicator", None
                ),
            },
            "coor_hdt": {
                "heading_degree": getattr(coor_hdt, "heading_degree", None),
            },
            "coor_vtg": {
                "speed_in_knots": getattr(coor_vtg, "speed_in_knots", None),
            },
        },
    }


def change_socket_data(call_sign, type_coor, data):
    parts = data.split(",")
    gga_quality_indicator = [
        "Fix not valid",
        "GPS fix",
        "Differential GPS fix (DGNSS), SBAS, OmniSTAR VBS, Beacon, RTX in GVBS mode",
        "Not applicable",
        "RTK Fixed, xFill",
        "RTK Float, OmniSTAR XP/HP, Location RTK, RTX",
        "INS Dead reckoning",
    ]

    data_kapal_coor[call_sign]["telnet_status"] = True
    if type_coor == "coor_gga":
        latitude = degree2decimal(float(parts[2]), parts[3])
        longitude = degree2decimal(float(parts[4]), parts[5])
        gps_quality_indicator = int(parts[6])

        data_kapal_coor[call_sign]["coor"][type_coor]["latitude"] = latitude
        data_kapal_coor[call_sign]["coor"][type_coor]["longitude"] = longitude
        data_kapal_coor[call_sign]["coor"][type_coor]["gps_quality_indicator"] = (
            gga_quality_indicator[gps_quality_indicator]
        )

    if type_coor == "coor_hdt":
        heading_degree = float(parts[1])
        data_kapal_coor[call_sign]["coor"][type_coor]["heading_degree"] = heading_degree

    if type_coor == "coor_vtg":
        speed_in_knots = float(parts[5])
        data_kapal_coor[call_sign]["coor"][type_coor]["speed_in_knots"] = speed_in_knots


# Function to handle $GNGGA messages
def handle_gngga_message(data, call_sign):
    # Parse the data and extract relevant information
    # Example: $GNGGA,125622.00,0113.52630995,S,11646.23419754,E,5,18,0.6,18.491,M,53.197,M,8.0,1015*70
    # db.session

    with app.app_context():
        try:
            quality_indicator = [
                "Fix not valid",
                "GPS fix",
                "Differential GPS fix (DGNSS), SBAS, OmniSTAR VBS, Beacon, RTX in GVBS mode",
                "Not applicable",
                "RTK Fixed, xFill",
                "RTK Float, OmniSTAR XP/HP, Location RTK, RTX",
                "INS Dead reckoning",
            ]
            parts = data.split(",")
            message_id = parts[0]
            utc_position = parts[1]
            latitude = degree2decimal(float(parts[2]), parts[3])
            direction_latitude = parts[3]
            longitude = degree2decimal(float(parts[4]), parts[5])
            direction_longitude = parts[5]
            gps_quality_indicator = int(parts[6])
            number_sv = int(parts[7])
            hdop = float(parts[8])
            orthometric_height = float(parts[9])
            unit_measure = parts[10]
            geoid_separation = float(parts[11])
            geoid_measure = parts[12]
            coor = (
                Coordinate.query.order_by(Coordinate.id_coor.desc())
                .filter_by(call_sign=call_sign)
                .first()
            )
            coor_hdt = (
                CoordinateHDT.query.order_by(CoordinateHDT.id_coor_hdt.desc())
                .filter_by(call_sign=call_sign)
                .first()
            )
            coor_gga = CoordinateGGA(
                call_sign=call_sign,
                message_id=message_id,
                utc_position=utc_position,
                latitude=latitude,
                direction_latitude=direction_latitude,
                longitude=longitude,
                direction_longitude=direction_longitude,
                gps_quality_indicator=quality_indicator[gps_quality_indicator],
                number_sv=number_sv,
                hdop=hdop,
                orthometric_height=orthometric_height,
                unit_measure=unit_measure,
                geoid_separation=geoid_separation,
                geoid_measure=geoid_measure,
            )
            coordinate = Coordinate(
                call_sign=call_sign,
                series_id=coor.series_id + 1 if coor else 1,
                default_heading=coor_hdt.heading_degree if coor_hdt else 0,
            )
            if not coor:
                db.session.add(coor_gga)
                db.session.flush()
                coordinate.id_coor_gga = coor_gga.id_coor_gga
                db.session.add(coordinate)
            else:
                if datetime.now() >= datetime.strptime(
                    str(coor.created_at), "%Y-%m-%d %H:%M:%S"
                ) + timedelta(minutes=1):
                    db.session.add(coor_gga)
                    db.session.flush()
                    coordinate.id_coor_gga = coor_gga.id_coor_gga
                    db.session.add(coordinate)

            db.session.commit()
        except Exception as e:
            app.logger.debug(f"Insert GGA error : {e}")
            db.session.rollback()
        finally:
            db.session.close()


# Function to handle $GNHDT messages
def handle_gnhdt_message(data, call_sign):
    # Parse the data and extract relevant information
    # Example: $GNHDT,302.182,T*21
    with app.app_context():
        try:
            parts = data.split(",")
            message_id = parts[0]
            heading_degree = float(parts[1])
            checksum = parts[2]
            coor = (
                Coordinate.query.order_by(Coordinate.id_coor.desc())
                .filter_by(call_sign=call_sign)
                .first()
            )
            coor_hdt = CoordinateHDT(
                message_id=message_id,
                call_sign=call_sign,
                heading_degree=heading_degree,
                checksum=checksum,
            )
            if coor.id_coor_hdt is None:
                db.session.add(coor_hdt)
                db.session.flush()
                coor.id_coor_hdt = coor_hdt.id_coor_hdt
                db.session.commit()
        except Exception as e:
            app.logger.debug(f"Insert HDT error : {e}")
            db.session.rollback()
        finally:
            db.session.close()


# Function to handle $GNVTG messages
def handle_gnvtg_message(data, call_sign):
    # Parse the data and extract relevant information
    # Example: $GNVTG,98.51,T,98.54,M,0.01,N,0.02,K,D*3E
    with app.app_context():
        try:
            mode = {
                "A": "Autonomous mode",
                "D": "Differential mode",
                "E": "Estimated (dead reckoning) mode",
                "M": "Manual Input mode",
                "S": "Simulator mode",
                "N": "Data not valid",
            }
            parts = data.split(",")
            message_id = parts[0]
            track_degree_true = float(parts[1])
            true_north = parts[2]
            track_degree_magnetic = float(parts[3])
            magnetic_north = parts[4]
            speed_in_knots = float(parts[5])
            measured_knots = parts[6]
            kph = float(parts[7])
            measured_kph = parts[8]
            mode_indicator = parts[9]
            coor = (
                Coordinate.query.order_by(Coordinate.id_coor.desc())
                .filter_by(call_sign=call_sign)
                .first()
            )
            coor_vtg = CoordinateVTG(
                call_sign=call_sign,
                track_degree_true=track_degree_true,
                true_north=true_north,
                track_degree_magnetic=track_degree_magnetic,
                magnetic_north=magnetic_north,
                speed_in_knots=speed_in_knots,
                measured_knots=measured_knots,
                kph=kph,
                measured_kph=measured_kph,
                mode_indicator=mode[(mode_indicator[0])],
                checksum=mode_indicator,
            )
            if coor.id_coor_vtg is None:
                db.session.add(coor_vtg)
                db.session.flush()
                coor.id_coor_vtg = coor_vtg.id_coor_vtg
                db.session.commit()
        except Exception as e:
            app.logger.debug(f"Insert VTG error : {e}")
            db.session.rollback()
        finally:
            db.session.close()


def heading_degree(old_lat, old_lon, new_lat, new_lon):
    try:
        delta_lon = new_lon - old_lon
        y = math.sin(math.radians(delta_lon)) * math.cos(math.radians(new_lat))
        x = math.cos(math.radians(old_lat)) * math.sin(
            math.radians(new_lat)
        ) - math.sin(math.radians(old_lat)) * math.cos(
            math.radians(new_lat)
        ) * math.cos(
            math.radians(delta_lon)
        )

        heading = math.degrees(math.atan2(y, x))
        heading = (heading + 360) % 360  # Convert heading to the range [0, 360)

        return heading
    except Exception as e:
        app.logger.debug(f"An error occurred: {str(e)} in Function heading_degree()")


def degree2decimal(deg_coord, direction, precision=10) -> float:
    try:
        degree = int(deg_coord / 100)
        minutes = deg_coord - (degree * 100)
        dotdegree = minutes / 60
        decimal = degree + dotdegree
        if direction in ("S", "W"):
            decimal = decimal * -1
        decimal = round(decimal, precision)
        return decimal
    except Exception as e:
        app.logger.debug(f"An error occurred: {str(e)} in Function degree2decimal()")
