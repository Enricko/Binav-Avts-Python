from datetime import datetime, timedelta
import math
import telnetlib
import time
from app.extensions import app, db,checked_configs
from app.model.coordinate import Coordinate
from app.model.coordinate_gga import CoordinateGGA
from app.model.coordinate_hdt import CoordinateHDT
from app.model.coordinate_vtg import CoordinateVTG


def telnet_worker(ip, port, call_sign, type_ip):
    # Connect to telnet
    with app.app_context():
        while True:
            tn = telnetlib.Telnet(ip, port)
            try:
                if checked_configs != {} and (ip, port) not in [(ip, port) for config in checked_configs.keys()]:
                    checked_configs.pop((ip, port))
                    break
            
                gngga_received = False
                gnhdt_received = False
                gnvtg_received = False
                while True:
                    try:
                        if checked_configs != {} and (ip, port) not in [
                            (ip, port) for config in checked_configs.keys()
                        ]:
                            checked_configs.pop((ip, port))
                            break
                        
                        data = tn.read_until(b"\n").decode("ascii").strip()
                        # dt = datetime.now()
                        # dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")
                        # Here you can process the received data, for example, print it
                        if ("GGA" in data) and (type_ip == "gga" or type_ip == "all"):
                            handle_gngga_message(data, call_sign)
                            gngga_received = True
                        elif ("HDT" in data) and (type_ip == "hdt" or type_ip == "all"):
                            handle_gnhdt_message(data, call_sign)
                            gnhdt_received = True
                        elif ("VTG" in data) and (type_ip == "vtg" or type_ip == "all"):
                            handle_gnvtg_message(data, call_sign)
                            gnvtg_received = True
                        # Delay for 5 seconds before reading again
                        if gngga_received and gnhdt_received and gnvtg_received:
                            gngga_received = False
                            gnhdt_received = False
                            gnvtg_received = False
                    except Exception as e:
                        app.logger.debug(f"Error in telnet connection to {ip}:{port}: {e}")
                        tn.close()
                        break
                    finally:
                        gngga_received = False
                        gnhdt_received = False
                        gnvtg_received = False
            except Exception as e:
                app.logger.debug(f"Error in telnet connection to {ip}:{port}: {e}")
            finally:
                app.logger.debug(f"Error in telnet connection to {ip}:{port}")
                tn.close()
                time.sleep(30)


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
            latitude = degree2decimal(float(parts[2]),parts[3])
            direction_latitude = parts[3]
            longitude = degree2decimal(float(parts[4]),parts[5])
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
                ) + timedelta(minutes=5):
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
