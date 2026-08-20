from zeroconf import Zeroconf, ServiceInfo
import socket

# Define the service type and name
service_type = "_customservice._tcp.local."
service_name = "My Custom Service._customservice._tcp.local."
service_port = 54000

# Create the service info
service_info = ServiceInfo(
    service_type,
    service_name,
    addresses=[socket.inet_aton("192.168.1.2")],  # Replace with your IP address
    port=service_port,
    properties={},
)

# Register the service
zeroconf = Zeroconf()
zeroconf.register_service(service_info)

print(f"Service {service_name} registered on port {service_port}")

try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.unregister_service(service_info)
    zeroconf.close()
