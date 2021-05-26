import socket
import threading
import json

HOST = ""
PORT = 9000

BUFSIZE = 1024

messages = {}
clientCount = 0


def echo(conn):
    global messages, clientCount
    while True:
        # Receive information.
        data = conn.recv(BUFSIZE).decode()
        # Disconnect if empty.
        if data == "":
            print("Could not read data from", conn.getpeername())
            break

        # Try to convert received data into JSON, store in messages buffer.
        try:
            data = json.loads(data)
            messages[data["sender"]] = data
            print("Got message from " + data["sender"])
            print(str(data) + "\n")
        except Exception as e:
            print(e)
            print("Invalid message from ", conn.getpeername())
            break

        # Try to send message buffer.
        try:
            conn.sendall(str(messages).encode("ascii"))
        except:
            print("Could not send data to", conn.getpeername())
            break
    clientCount -= 1
    if clientCount == 0:
        print("All clients disconnected; resetting.")
        messages = {}


# Create the server.
s = socket.create_server((HOST, PORT))
s.listen()

# Keep accepting connections.
while True:
    conn, addr = s.accept()
    clientCount += 1
    print("Connection accepted from", addr)
    t = threading.Thread(target=echo, args=(conn,))
    t.start()
