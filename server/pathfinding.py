free = [[True for x in range(10)] for y in range(10)]
dist = [[-1 for x in range(10)] for y in range(10)]
path = [[False for x in range(10)] for y in range(10)]

free[3][0] = False
free[3][1] = False

free[7][0] = False
free[7][1] = False

free[5][1] = False

free[6][2] = False

size = 7
dist[3][3] = 0
free[3][3] = False
next_nodes = [[3, 3]]
for i in range(size):
    new_next = []
    for node in next_nodes:
        x = node[0]
        y = node[1]
        if x < 9:
            if free[x+1][y]:
                free[x + 1][y] = False
                dist[x + 1][y] = i + 1
                new_next.append([x + 1, y])
        if x > 0:
            if free[x-1][y]:
                free[x - 1][y] = False
                dist[x - 1][y] = i + 1
                new_next.append([x - 1, y])
        if y < 9:
            if free[x][y + 1]:
                free[x][y + 1] = False
                dist[x][y + 1] = i + 1
                new_next.append([x, y + 1])
        if y > 0:
            if free[x][y - 1]:
                free[x][y - 1] = False
                dist[x][y - 1] = i + 1
                new_next.append([x, y - 1])
    next_nodes = new_next

x = 6
y = 1

distance = dist[x][y]
path[x][y] = True

while distance > 0:
    distance = dist[x][y]
    if x < 9:
        if dist[x+1][y] < distance and dist[x+1][y] != -1:
            path[x+1][y] = True
            x = x + 1
            continue
    if x > 0:
        if dist[x-1][y] < distance and dist[x-1][y] != -1:
            path[x-1][y] = True
            x = x - 1
            continue
    if y < 9:
        if dist[x][y+1] < distance and dist[x][y+1] != -1:
            path[x][y+1] = True
            y = y + 1
            continue
    if y > 0:
        if dist[x][y-1] < distance and dist[x][y-1] != -1:
            path[x][y-1] = True
            y = y - 1
            continue

for y in range(10):
    for x in range(10):
        distance = str(dist[x][y]).zfill(2)
        end = ""
        if x == 9:
            end = "\n"
        if free[x][y]:
            print("\u001B[42m[" + distance + "]\u001B[0m", end=end)
        elif path[x][y]:
            print("\u001B[44m[" + distance + "]\u001B[0m", end=end)
        elif distance == "-1":
            print("\u001B[41m[" + distance + "]\u001B[0m", end=end)
        else:
            print("\u001B[45m[" + distance + "]\u001B[0m", end=end)