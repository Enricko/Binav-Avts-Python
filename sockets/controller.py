import datetime
import math
import database as db

def socket_handler(data,call_sign):
    try:
        parts = data.split(',')
        sentence_type = parts[0][3:]
        if sentence_type == "GGA":
            data_coor = db.fetch_query(f"SELECT * FROM coordinates WHERE call_sign = '{call_sign}' ORDER BY id_coor DESC LIMIT 1")
            if len(data_coor) <= 0:
                insert_gga(call_sign,data)
            else:
                date_result = datetime.datetime.strptime(str(data_coor[0][-2]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=5)
                current_date = datetime.datetime.now()
                if current_date > date_result:
                    insert_gga(call_sign,data)
        elif sentence_type == "HDT":
            data_coor = db.fetch_query(f"SELECT id_coor_hdt FROM coordinates WHERE call_sign = '{call_sign}' ORDER BY id_coor DESC LIMIT 1")
            if data_coor[0][0] is None:
                insert_hdt(call_sign,data)
        else:
            return 0
        return db.fetch_query(f"SELECT CASE WHEN id_coor_gga IS NULL OR id_coor_hdt IS NULL THEN 0 ELSE 1 END AS has_data FROM coordinates WHERE call_sign = '{call_sign}' ORDER BY id_coor DESC LIMIT 1")
    except Exception as e:
        print(f"An error occurred: {str(e)} {call_sign} in Function socket_handler()")
        
def insert_gga(call_sign : str,data_gga:str):
    try:
        split_gga = data_gga.split(',')
        gps_quality = [
            'Fix not valid','GPS fix',
            'Differential GPS fix (DGNSS), SBAS, OmniSTAR VBS, Beacon, RTX in GVBS mode',
            'Not applicable',
            'RTK Fixed, xFill',
            'RTK Float, OmniSTAR XP/HP, Location RTK, RTX',
            'INS Dead reckoning'
        ]
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        latitude = degree2decimal(float(split_gga[2]),split_gga[3])
        longitude = degree2decimal(float(split_gga[4]),split_gga[5])
        data_to_insert = {
            'call_sign': call_sign,
            'message_id' : split_gga[0],
            'utc_position' : split_gga[1],
            'latitude' : latitude,
            'direction_latitude' : split_gga[3],
            'longitude' : longitude,
            'direction_longitude' : split_gga[5],
            'gps_quality_indicator' : gps_quality[int(split_gga[6])],
            'number_sv' : split_gga[7],
            'hdop' : split_gga[8],
            'orthometric_height' : split_gga[9],
            'unit_measure' : split_gga[10],
            'geoid_seperation' : split_gga[11],
            'geoid_measure' : split_gga[12],
            'created_at' : created_at
        }
        connection = db.connect_to_database()
        cursor = connection.cursor()
        
        # Construct the SQL INSERT statement
        insert_query = """
        INSERT INTO coordinate_ggas
        (call_sign, message_id, utc_position, latitude, direction_latitude, longitude, direction_longitude, gps_quality_indicator, number_sv, hdop, orthometric_height, unit_measure, geoid_seperation, geoid_measure, created_at)
        VALUES
        (%(call_sign)s, %(message_id)s, %(utc_position)s, %(latitude)s, %(direction_latitude)s, %(longitude)s, %(direction_longitude)s, %(gps_quality_indicator)s, %(number_sv)s, %(hdop)s, %(orthometric_height)s, %(unit_measure)s, %(geoid_seperation)s,%(geoid_measure)s, %(created_at)s)
        """
        
        # Execute the INSERT statement
        cursor.execute(insert_query, data_to_insert)
        
        # Commit the transaction
        connection.commit()

        # Retrieve the ID of the last inserted record
        last_inserted_id = cursor.lastrowid
        series_id_query = (
            "SELECT COUNT(*) + 1 FROM coordinates WHERE call_sign = %s"
        )
        series_id_values = (call_sign,)
        cursor.execute(series_id_query, series_id_values)
        series_id = cursor.fetchone()[0]
        
        heading = 0.0
        if series_id == 1:
            heading = heading
        else:
            coor = db.fetch_query(f"SELECT * FROM coordinate_ggas WHERE call_sign = '{call_sign}' ORDER BY id_coor_gga DESC LIMIT 1 OFFSET 1")
            heading = heading_degree(coor[0][4],coor[0][6],latitude,longitude)
                    
        data_to_insert_coor = (call_sign, series_id, last_inserted_id, heading, created_at)
        insert_query_coor = """
        INSERT INTO coordinates
        (call_sign, series_id, id_coor_gga,default_heading,created_at)
        VALUES
        (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query_coor, data_to_insert_coor)
        connection.commit()

        # print("Data inserted successfully")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"An error occurred: {str(e)} {call_sign} in Function insert_gga()")

def insert_hdt(call_sign:str,data_hdt:str):
    try:
        split_hdt = data_hdt.split(',')
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_to_insert = {
            'call_sign' : call_sign,
            'message_id' : split_hdt[0],
            'heading_degree' : split_hdt[1],
            'checksum' : split_hdt[2],
            'created_at': created_at
        }
        connection = db.connect_to_database()
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO coordinate_hdts
        (call_sign, message_id, heading_degree, checksum, created_at)
        VALUES
        (%(call_sign)s, %(message_id)s, %(heading_degree)s, %(checksum)s, %(created_at)s)
        """
        
        # Execute the INSERT statement
        cursor.execute(insert_query, data_to_insert)
        
        # Commit the transaction
        connection.commit()

        # Retrieve the ID of the last inserted record
        last_inserted_id = cursor.lastrowid
        
        series_id_query = (
            "SELECT COUNT(*) FROM coordinates WHERE call_sign = %s"
        )
        series_id_values = (call_sign,)
        cursor.execute(series_id_query, series_id_values)
        series_id = cursor.fetchone()[0]
        
        data_to_insert_coor = (last_inserted_id,created_at,call_sign,series_id)
        insert_query_coor = """
        UPDATE coordinates
        SET id_coor_hdt = %s, updated_at = %s 
        WHERE call_sign = %s AND series_id = %s
        """
        
        cursor.execute(insert_query_coor, data_to_insert_coor)
        connection.commit()

        # print("Data inserted successfully")
        cursor.close()
        connection.close()
        
        
    except Exception as e:
        print(f"An error occurred: {str(e)} {call_sign} in Function insert_hdt()")
  

def heading_degree(old_lat, old_lon, new_lat, new_lon):
    try:
        delta_lon = new_lon - old_lon
        y = math.sin(math.radians(delta_lon)) * math.cos(math.radians(new_lat))
        x = math.cos(math.radians(old_lat)) * math.sin(math.radians(new_lat)) - math.sin(math.radians(old_lat)) * math.cos(math.radians(new_lat)) * math.cos(math.radians(delta_lon))
        
        heading = math.degrees(math.atan2(y, x))
        heading = (heading + 360) % 360  # Convert heading to the range [0, 360)
        
        return heading
    except Exception as e:
        print(f"An error occurred: {str(e)} in Function heading_degree()")
    
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
        print(f"An error occurred: {str(e)} in Function degree2decimal()")