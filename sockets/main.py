import datetime
import telnetlib3
import mysql.connector
import asyncio
import database as db
import controller as ctrl
import psutil

# Define the maximum CPU usage threshold (e.g., 80%)
max_cpu_usage = 85.0
activation = {}
# Function to handle a single socket connection and fetch messages
async def fetch_messages(call_sign, ip, port, type_ip):
    global activation
    closed = False
    # while True:
    while True:
        try:
            get_active = activation.get(call_sign, None)
            # print(call_sign not in activation or get_active != (ip, port))
            if call_sign not in activation or get_active != (ip, port, type_ip):
                print(activation)
                break
            reader, writer = await telnetlib3.open_connection(ip, port)

            print(f"[{datetime.datetime.now()}] Connected to {call_sign} = {ip}:{port}")

            while True:
                try:
                    await asyncio.sleep(10)
                    get_active = activation.get(call_sign, None)
                    buffer = ""
                    if call_sign not in activation or get_active != (ip, port, type_ip):
                        print("stop")
                        break
                    data = await reader.read(1024)
                    buffer += data
                    messages = buffer.split('\r\n')
                    buffer = messages.pop()
                    # print(f"{call_sign} {ip} {port} = {messages} {len(messages)}")
                    # print(f"{call_sign} {ip} {port} = {messages[0]} {len(messages)}")
                    if len(messages) == 0:
                        # print("No data avaliable")
                        break
                    else:
                        for message in messages:
                            if message != messages[-1] :
                                if ctrl.socket_handler(message,call_sign)[0][0] == 1:
                                    # print(f"Finish : {call_sign}")
                                    break
                            # print(f"Received message from {call_sign} = {ip}:{port}: {message}")
                    # break
                except ConnectionResetError:
                    # Handle connection reset (e.g., server closed the connection)
                    print(f'Connection to {call_sign} = {ip}:{port} reset. Reconnecting...')
                    break
            await asyncio.sleep(10)  # Wait for 10 seconds before reconnecting
            
        except ConnectionRefusedError:
            print(f"Connection to {call_sign} = {ip}:{port} refused. Retrying...")
            await asyncio.sleep(10)  # Wait for 10 seconds before retrying
        except asyncio.TimeoutError:
            print(f"Connection to {call_sign} = {ip}:{port} timed out. Retrying...")
            await asyncio.sleep(10)  # Wait for 10 seconds before retrying
        except OSError as e:
            print(f"OSError: {e} {call_sign} = {ip}:{port} Retrying...")  # Add this line to print OSError
            await asyncio.sleep(10)  # Wait for 10 seconds before retrying
        except Exception as e:
            print(f"An error occurred: {str(e)} {call_sign} = {ip}:{port}. Restarting...")
            await asyncio.sleep(10)  # Wait for 10 seconds before restarting

async def task_manager():
    reload_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    global activation
    # Get the list of IP and port pairs from the database
    while True:
        try:
            ip_port_list = db.fetch_socket()
            current_active = {}
            time_now = datetime.datetime.now()
            
            cpu_usage = psutil.cpu_percent(interval=1)
            print(f"Current CPU usage: {cpu_usage}%")
            if cpu_usage > max_cpu_usage:
                activation = {}
                print("CPU usage exceeds the maximum threshold. Cooling down...")
                await asyncio.sleep(60)
            else:
                for call_sign, ip, port, type_ip in ip_port_list:
                    get_active = activation.get(call_sign, None)
                    current_active[call_sign] = (ip, port,type_ip)
                    stat = db.fetch_query(f"SELECT status FROM kapals WHERE call_sign = '{call_sign}'")
                    if stat[0][0] == 1:
                        if call_sign not in activation or get_active != (ip, port, type_ip):
                            asyncio.create_task(fetch_messages(call_sign, ip, port, type_ip))
                            print(f"[{time_now}] Added task for {ip}:{port}")
                        
                activation = current_active
                
                if time_now > reload_time:
                    activation = {}
                    print("Reload")
                    reload_time = time_now + datetime.timedelta(minutes=30)
                    await asyncio.sleep(60)
                        
                await asyncio.sleep(60)
        except OSError as e:
            print(f"[{datetime.datetime.now()}] OSError: {e}. Retrying...")  # Add this line to print OSError
            await asyncio.sleep(10)  # Wait for 10 seconds before retrying
        except Exception as e:
            print(f"[{datetime.datetime.now()}] An error occurred: {str(e)}. Restarting...")
            await asyncio.sleep(10)  # Wait for 10 seconds before restarting

if __name__ == "__main__":
    asyncio.run(task_manager())