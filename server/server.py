import socket
import threading
import json
import websockets
import asyncio

HOST = ""
PORT = 9000

WSPORT = 8008

BUFSIZE = 1024
SCANRANGE = 100

boardSize = 11
messages = {}
obstacles = []
targets = {}
destinations = {"yellow": [[10, 0]], "red": [[0, 0]], "green": [[10, 10]], "blue": [[0, 10]]}
free = [[True for x in range(boardSize)] for y in range(boardSize)]
dist = [[-1 for x in range(boardSize)] for y in range(boardSize)]
locations = {}
movements = {}
clientCount = 0


async def handle_ws(websocket, uri):
    print(f"Connection accepted from {uri}")
    while True:
        try:
            data = await websocket.recv()
        except:
            print(f"Connection lost to {uri}")
            return
        if data == "request_messages":
            global destinations
            returnData = {
                "obstacles": obstacles,
                "targets": targets,
                "destinations": destinations,
                "locations": locations
            }
            await websocket.send(json.dumps(returnData))
        else:
            # print(data)
            data = json.loads(data)
            type = data["type"]
            if type == 0:
                name = data["name"]
                to = data["to"]
                if name in destinations:
                    destinations[name].append(to)
                else:
                    destinations[name] = [to]
            if type == 1:
                toCoords = data["to"]
                fromCoords = data["from"]
                if destinations != {}:
                    destinations[next(iter(destinations))].append(toCoords)
                    destinations[next(iter(destinations))].append(fromCoords)
                else:
                    destinations["yellow"] = [toCoords, fromCoords]
            if type == 2:
                for location in locations:
                    destinations[location] = [locations[location]]
            print(json.dumps(destinations))



def handle_s(sock):
    # Keep accepting connections.
    global clientCount
    while True:
        conn, addr = sock.accept()
        clientCount += 1
        print("Connection accepted from", addr)
        t = threading.Thread(target=echo, args=(conn,))
        t.start()


def inPath(x, y, path):
    for step in path:
        if step == [x, y]:
            return True
    return False


def genPath(name, target, dists, frees):
    x = target[0]
    y = target[1]
    distance = dists[x][y]
    path = [target]

    while distance > 0:
        distance = dists[x][y]
        if x < boardSize - 1:
            if dists[x + 1][y] < distance and dists[x + 1][y] != -1:
                path.append([x + 1, y])
                x = x + 1
                continue
        if x > 0:
            if dists[x - 1][y] < distance and dists[x - 1][y] != -1:
                path.append([x - 1, y])
                x = x - 1
                continue
        if y < boardSize - 1:
            if dists[x][y + 1] < distance and dists[x][y + 1] != -1:
                path.append([x, y + 1])
                y = y + 1
                continue
        if y > 0:
            if dists[x][y - 1] < distance and dists[x][y - 1] != -1:
                path.append([x, y - 1])
                y = y - 1
                continue

    targets[name] = path[len(path) - 2]

    for y in range(boardSize):
        for x in range(boardSize):
            distance = str(dists[x][y]).zfill(2)
            end = ""
            if x == boardSize - 1:
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
    dists = [[-1 for x in range(boardSize)] for y in range(boardSize)]
    dists[sX][sY] = 0
    frees[sX][sY] = False
    next_nodes = [[sX, sY]]
    for i in range(SCANRANGE):
        new_next = []
        for node in next_nodes:
            x = node[0]
            y = node[1]
            if x < boardSize - 1:
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
            if y < boardSize - 1:
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
    print("Could not plan route.")


def generateNextMove(dest):
    freeMap = [[True for x in range(boardSize)] for y in range(boardSize)]
    for obstacle in obstacles:
        if 0 <= obstacle[0] <= boardSize - 1 and 0 <= obstacle[1] <= boardSize - 1:
            freeMap[obstacle[0]][obstacle[1]] = False
    for y in range(boardSize):
        for x in range(boardSize):
            distance = str(dist[x][y]).zfill(2)
            end = ""
            if x == boardSize - 1:
                end = "\n"
            if freeMap[x][y]:
                print("\u001B[42m[" + distance + "]\u001B[0m", end=end)
            elif distance == "-1":
                print("\u001B[41m[" + distance + "]\u001B[0m", end=end)
            else:
                print("\u001B[45m[" + distance + "]\u001B[0m", end=end)
    print("---")
    if dest in locations and dest in destinations and locations[dest] != destinations[dest][0]:
        dijkstra(dest, locations[dest], destinations[dest][0], freeMap[:])
    elif locations[dest] == destinations[dest][0] and len(destinations[dest]) == 2:
        destinations[dest].pop(0)
        print(dest + " has arrived.")
    else:
        targets[dest] = locations[dest]
        print("Unit has arrived, awaiting orders.")


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
                    if msgData not in obstacles and not robotLocation(msgData) and 0 <= msgData[0] <= boardSize - 1 and 0 <= msgData[1] <= boardSize - 1:
                        obstacles.append(msgData)
                # Free places
                if msgType == 1:
                    if msgData in obstacles:
                        obstacles.remove(msgData)
            print("Got message from " + sender)
            # print(str(data) + "\n")
        except Exception as e:
            print(e)
            print("Invalid message from ", conn.getpeername())
            break

        # Try to send message buffer.
        try:
            generateNextMove(sender)
            print("Generated move.")
            conn.sendall(("{\"targets\":" + json.dumps(targets) + "}").encode("ascii"))
            print("Info sent.")
        except Exception as e:
            print(e)
            print("Could not send data to", conn.getpeername())
            break
    clientCount -= 1
    if clientCount == 0:
        print("All clients disconnected; resetting.")
        messages = {}


ws = websockets.serve(handle_ws, HOST, WSPORT)

# Create the server.
s = socket.create_server((HOST, PORT))
s.listen()

t = threading.Thread(target=handle_s, args=(s,))
t.start()

asyncio.get_event_loop().run_until_complete(ws)
asyncio.get_event_loop().run_forever()
