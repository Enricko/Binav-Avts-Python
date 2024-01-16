import mysql.connector

# Create a MySQL connection
db_config = {
    # 'host':'154.26.128.195',
    # 'user':'binavavt_binavavt',
    # 'password': ']HFbMEeV~cWL',
    # 'database':'binavavt_avts'
    
    # "host":'localhost',
    # "user":'binavavt_binavavt',
    # "password":']HFbMEeV~cWL',
    # "database":'binavavt_avts'
    
    'host':'82.180.152.1',
    'user':'u537134036_kapal',
    'password': 'wOu~^S2J~E7',
    'database':'u537134036_pemantau_kapal'
}

def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            # print("Connected to MySQL database")
            return connection
    except mysql.connector.Error as e:
        print("Error:", e)
        return None
    
def fetch_query(query):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
def fetch_socket():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT call_sign, ip, port, type_ip FROM ip_kapals')
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()