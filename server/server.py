import socket
import threading
import json

HOST = ""
PORT = 9000

BUFSIZE = 1024
SCANRANGE = 10

messages = {}
obstacles = []
targets = {}
destinations = {"Sherman": [0, 4]}
free = [[True for x in range(10)] for y in range(10)]
dist = [[-1 for x in range(10)] for y in range(10)]
locations = {}
movements = {}
clientCount = 0


def inPath(x, y, path):
    for step in path:
        if step == [x, y]:
            return True
    return False


def genMap():
    free = [[True for x in range(10)] for y in range(10)]
    for obstacle in obstacles:
        free[obstacle[0]][obstacle[1]] = False


def genPath(name, target, dists, frees):
    x = target[0]
    y = target[1]
    distance = dists[x][y]
    path = [target]

    while distance > 0:
        distance = dists[x][y]
        if x < 9:
            if dists[x + 1][y] < distance and dists[x + 1][y] != -1:
                path.append([x + 1, y])
                x = x + 1
                continue
        if x > 0:
            if dists[x - 1][y] < distance and dists[x - 1][y] != -1:
                path.append([x - 1, y])
                x = x - 1
                continue
        if y < 9:
            if dists[x][y + 1] < distance and dists[x][y + 1] != -1:
                path.append([x, y + 1])
                y = y + 1
                continue
        if y > 0:
            if dists[x][y - 1] < distance and dists[x][y - 1] != -1:
                path.append([x, y - 1])
                y = y - 1
                continue

    targets[name] = path[len(path) - 1]

    for y in range(10):
        for x in range(10):
            distance = str(dists[x][y]).zfill(2)
            end = ""
            if x == 9:
                end = "\n"
            if frees[x][y]:
                print("\u001B[42m[" + distance + "]\u001B[0m", end=end)
            elif inPath(x, y, path):
                print("\u001B[44m[" + distance + "]\u001B[0m", end=end)
            elif distance == "-1":
                print("\u001B[41m[" + distance + "]\u001B[0m", end=end)
            else:
                print("\u001B[45m[" + distance + "]\u001B[0m", end=end)


def dijkstra(name, start, target, frees):
    sX = start[0]
    sY = start[1]
    dists = [[-1 for x in range(10)] for y in range(10)]
    dists[sX][sY] = 0
    frees[sX][sY] = False
    next_nodes = [[sX, sY]]
    for i in range(SCANRANGE):
        new_next = []
        for node in next_nodes:
            x = node[0]
            y = node[1]
            if x < 9:
                if frees[x + 1][y]:
                    frees[x + 1][y] = False
                    dists[x + 1][y] = i + 1
                    if [x + 1, y] == target:
                        genPath(name, target, dists, frees)
                        return
                    new_next.append([x + 1, y])
            if x > 0:
                if frees[x - 1][y]:
                    frees[x - 1][y] = False
                    dists[x - 1][y] = i + 1
                    if [x - 1, y] == target:
                        genPath(name, target, dists, frees)
                        return
                    new_next.append([x - 1, y])
            if y < 9:
                if frees[x][y + 1]:
                    frees[x][y + 1] = False
                    dists[x][y + 1] = i + 1
                    if [x, y + 1] == target:
                        genPath(name, target, dists, frees)
                        return
                    new_next.append([x, y + 1])
            if y > 0:
                if frees[x][y - 1]:
                    frees[x][y - 1] = False
                    dists[x][y - 1] = i + 1
                    if [x, y - 1] == target:
                        genPath(name, target, dists, frees)
                        return
                    new_next.append([x, y - 1])
        next_nodes = new_next


def generateNextMove():
    genMap()
    for dest in destinations:
        if dest in locations and dest in destinations:
            dijkstra(dest, locations[dest], destinations[dest], free[:])


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
            generateNextMove()
            conn.sendall(("{\"targets\":" + json.dumps(targets) + "}").encode("ascii"))
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
