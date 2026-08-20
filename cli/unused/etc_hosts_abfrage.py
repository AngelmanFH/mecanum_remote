import socket

hostname = 'anakin'
host_info = socket.gethostbyname_ex(hostname)

print("Primary hostname:", host_info[0])
print("Aliases:", host_info[1])
print("IP addresses:", host_info[2])
