import socket

def connect_to_host(hostname, port):
    try:
        # Get all IP addresses associated with the hostname
        host_info = socket.gethostbyname_ex(hostname)
        ip_addresses = host_info[2]

        for ip in ip_addresses:
            try:
                # Create a socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)  # Set a timeout for the connection attempt

                # Attempt to connect to the IP address
                sock.connect((ip, port))
                print(f"Successfully connected to {hostname} ({ip}) on port {port}")
                return sock  # Return the connected socket

            except socket.error as e:
                print(f"Failed to connect to {ip}: {e}")

            finally:
                sock.close()

        print(f"Could not connect to any IP addresses for {hostname}")
        return None

    except socket.gaierror as e:
        print(f"Error resolving hostname {hostname}: {e}")
        return None

# Example usage
hostname = 'anakin'
port = 54000
connected_socket = connect_to_host(hostname, port)

if connected_socket:
    # Use the connected socket
    connected_socket.close()
