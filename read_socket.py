import socket
import select
import errno


def create_client_socket(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
    except Exception as e:
        print(e)


def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)
        if data:
            # Process the received data
            print(f"Received data: {data.decode('utf-8')}")
        else:
            # Connection closed by the server
            print("Connection closed by the server")
            client_socket.close()
    except socket.error as e:
        if e.errno == errno.ECONNRESET:
            # Handle connection reset by peer
            print("Connection reset by peer")
        elif e.errno == errno.ECONNREFUSED:
            # Handle connection refused
            print("Connection refused")
        else:
            # Handle other socket errors
            print(f"Socket error: {e}")
        client_socket.close()


def main():
    try:
        # List of IP addresses and ports
        servers = [("127.0.0.1", 8888), ("example.com", 8888), ("192.168.1.1", 8888)]

        client_sockets = [create_client_socket(host, port) for host, port in servers]

        while True:
            try:
                # Use select to wait for readable sockets
                readable, _, _ = select.select(client_sockets, [], [])

                for sock in readable:
                    # Existing client socket has data
                    handle_client(sock)

            except KeyboardInterrupt:
                # Handle keyboard interrupt (Ctrl+C) to gracefully exit
                break
            except Exception as e:
                # Handle other exceptions
                print(f"Error: {e}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
