import socket

HOST = ""
PORT = 9000

BUFSIZE = 1024

# Create the server.
s = socket.create_server((HOST, PORT))
s.listen()

# Get a connection.
conn, addr = s.accept()

# Receive data.
data = conn.recv(BUFSIZE).decode()

# Send data.
conn.sendall(data.encode("ascii"))

print(data)
