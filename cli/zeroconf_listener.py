from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange
import socket

class MyListener:
    def __init__(self):
        self.ip_address = None

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            self.ip_address = socket.inet_ntoa(info.addresses[0])
            print(f"IP address of {name}: {self.ip_address}")

zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "54000._tcp.local.", listener)

try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()
