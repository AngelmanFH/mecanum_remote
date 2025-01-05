# https://stackoverflow.com/questions/56828353/how-to-know-if-a-non-blocking-socket-is-closed

# Client
import socket
import struct
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.0.0.254', 54000))

for i in range(5):
    time.sleep(0.3)
    data = str(i).encode('utf-8')
    length = struct.pack('!I', len(data))
    s.send(length + data)
s.close()
