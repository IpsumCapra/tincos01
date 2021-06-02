import socket
import threading
import json

HOST = ""
PORT = 9000

BUFSIZE = 1024

messages = {}
obstacles = []
locations = {}
movements = {}
clientCount = 0


def robotLocation(pos):
    for loc in locations:
        if locations[loc] == pos:
            return True
    return False


def echo(conn):
    global messages, clientCount
    while True:
        # Receive information.
        data = conn.recv(BUFSIZE).decode()
        # Disconnect if empty.
        if data == "":
            print("Could not read data from", conn.getpeername())
            break

        # Try to convert received data into JSON, Sort, and store.
        try:
            data = json.loads(data)
            sender = data["sender"]
            messages[sender] = data
            for msg in data["body"]:
                msgType = msg["type"]
                msgData = msg["data"]
                # Bot location.
                if msgType == 2:
                    locations[sender] = msgData
                # Planned movement direction.
                if msgType == 3:
                    movements[sender] = msgData
                # Static obstacles
                if msgType == 0:
                    if msgData not in obstacles and not robotLocation(msgData):
                        obstacles.append(msgData)

            print("Got message from " + sender)
            # print(str(data) + "\n")
        except Exception as e:
            print(e)
            print("Invalid message from ", conn.getpeername())
            break

        # Try to send message buffer.
        try:
            conn.sendall(("{\"locations\":" + str(locations) + ",\"obstacles\":" + str(obstacles)).encode("ascii"))
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
