import socket

HOST = "145.24.222.80"
PORT = 9000

BUFSIZE = 1024

s = socket.socket()
try:
    s.connect((HOST, PORT))
except:
    print("Connection refused.")
    exit()

data = "{ello ello ello}"

s.send(data.encode("ascii"))

print(s.recv(BUFSIZE).decode())
