import socket
import threading
import struct
import signal
import sys

# Global variable to keep track of running threads
threads = []
about2quit = False

def handle_client(client_socket):
    try:
        while not about2quit:
            # Read the size (4 bytes, unsigned integer)
            size_data = client_socket.recv(4)
            if not size_data:
                break
            size = struct.unpack('!I', size_data)[0]

            # Read the remaining bytes according to the size
            data = client_socket.recv(size)
            if not data:
                break

            print(f"Received data: {data.decode()}")

            # Echo the data back to the client
            client_socket.sendall(size_data + data)
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client_socket.close()

def send_messages(client_socket):
    try:
        while True:
            message = input("Enter message to send: ")
            message_data = message.encode()
            size = len(message_data)
            size_data = struct.pack('!I', size)
            client_socket.sendall(size_data + message_data)
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client_socket.close()

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")


    def signal_handler(sig, frame):
        print("\nGracefully shutting down...")
        global about2quit
        about2quit = True
        server_socket.close()
        for t in threads:
            t.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while not about2quit:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")

            # Start a thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
            client_thread.start()
            threads.append(client_thread)

            # Start a thread to send messages to the client
            #send_thread = threading.Thread(target=send_messages, args=(client_socket,))
            #send_thread.start()
            #threads.append(send_thread)
        except socket.error as e:
            print(f"Socket error: {e}")
            break

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 54000
    start_server(HOST, PORT)
