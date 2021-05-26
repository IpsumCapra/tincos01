import socket

HOST = "145.24.222.80"
PORT = 9000

BUFSIZE = 1024

# Connect to server, exit with failure.
s = socket.socket()
try:
    s.connect((HOST, PORT))
except:
    print("Connection refused.")
    exit()

# Set data.
data = "{\"sender\":\"test\"}"

# Send data.
s.send(data.encode("ascii"))

# Print received info.
print(s.recv(BUFSIZE).decode())
