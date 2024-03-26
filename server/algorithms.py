from functools import lru_cache
from math import hypot, ceil, acos, pi
# Подготовка к построению графа:

@lru_cache(maxsize=200)
def getDistanceBetweenPoints(point1, point2):
    return hypot(abs(point1[0] - point2[0]), abs(point1[1] - point2[1]))


def getRoadLines(points):
    # кластеризация точек
    ACCURATE = 1.2  # для baseDistance

    roadLines = []
    sortedPoints = sorted(points)
    baseDistance = min(
        [getDistanceBetweenPoints(sortedPoints[0], sortedPoints[i]) for i in range(1, len(sortedPoints))])
    sortedPoints = sorted(sortedPoints, key=lambda x: getDistanceBetweenPoints(sortedPoints[0], x))
    while sortedPoints:
        start = sortedPoints.pop()
        roadLines += [[start]]
        leftAdd, rightAdd = True, True
        while leftAdd or rightAdd:
            leftAdd, rightAdd = False, False
            left = roadLines[-1][0]
            right = roadLines[-1][-1]
            for i in range(len(sortedPoints) - 1, -1, -1):
                cur = sortedPoints[i]
                if not leftAdd and getDistanceBetweenPoints(left, cur) < baseDistance * ACCURATE:
                    roadLines[-1].insert(0, sortedPoints.pop(i))
                    leftAdd = True
                elif not rightAdd and getDistanceBetweenPoints(right, cur) < baseDistance * ACCURATE:
                    roadLines[-1].append(sortedPoints.pop(i))
                    rightAdd = True
                elif leftAdd and rightAdd:
                    break
    return roadLines


def getUnitVector(point1, point2):
    return [(point2[axis] - point1[axis]) / getDistanceBetweenPoints(point1, point2) for axis in range(2)]


def extendLines(lines, k=2):
    extendLines = []

    distance = getDistanceBetweenPoints(lines[0][0], lines[0][1]) * k
    for line in lines:
        # продлеваем конец линии
        unitVector = getUnitVector(line[-2], line[-1])
        x, y = distance * unitVector[0] + line[-1][0], distance * unitVector[1] + line[-1][1]
        line.append((ceil(x), ceil(y)))
        # продлеваем начало линии
        vector = getUnitVector(line[1], line[0])
        x, y = line[0][0] + distance * vector[0], line[0][1] + distance * vector[1]
        line.insert(0, (ceil(x), ceil(y)))

        extendLines.append(line)
    return extendLines



# Остальное:
def getAngleBetweenLineAndAxis(line):
    startPosLine, endPosLine = line
    vector = [(endPosLine[axis] - startPosLine[axis]) for axis in range(2)]
    angles = {'x': pi, 'y': pi}
    for i, axis in enumerate(angles):
        scalarProduct = vector[i]
        lengthsProduct = hypot(vector[0], vector[1])
        if lengthsProduct == 0: continue
        resAngle = acos(scalarProduct / lengthsProduct) if axis == 'x' else acos(scalarProduct / lengthsProduct)
        if scalarProduct < 0: resAngle *= -1
        angles[axis] = resAngle
    return angles


def getPosRightSideSegment(startPosLine, endPosLine, deviationLen=60):
    if startPosLine[0] < 20 or endPosLine[0] < 20:
        print(startPosLine, endPosLine)
    vectorAB = [(endPosLine[axis] - startPosLine[axis]) for axis in range(2)]
    lengthVector = hypot(abs(vectorAB[0]), abs(vectorAB[1]))
    centerPoint = ((startPosLine[0] + endPosLine[0]) / 2, (startPosLine[1] + endPosLine[1]) / 2)
    if lengthVector > 0:
        resultVector = [(deviationLen * vectorAB[1]) / lengthVector,
                        (deviationLen * vectorAB[0]) / lengthVector]
    else:
        resultVector = [0, 0]
    for pr in [1, -1]:
        angles = getAngleBetweenLineAndAxis((startPosLine, endPosLine))
        needPosX, needPosY = (resultVector[0] * pr), (resultVector[1] * pr)
        if angles['x'] > 0 and angles['y'] > 0:
            needPosX, needPosY = needPosX * 1, needPosY * -1
        elif angles['x'] < 0 and angles['y'] > 0:
            needPosX, needPosY = needPosX * 1, needPosY * -1
        elif angles['x'] < 0 and angles['y'] < 0:
            needPosX, needPosY = needPosX * 1, needPosY * -1
        elif angles['x'] > 0 and angles['y'] < 0:
            needPosX, needPosY = needPosX * -1, needPosY * 1
        needPos = (round(centerPoint[0] + needPosX), round(centerPoint[1] + needPosY))
        vectorAC = [(needPos[axis] - startPosLine[axis]) for axis in range(2)]
        deviation = vectorAB[0] * vectorAC[1] - vectorAB[1] * vectorAC[0]
        if deviation > 0:
            return needPos
    return (ceil(centerPoint[0]), ceil(centerPoint[1]))


def findPathBFS(start, end):
    queue = [(start, [start])]
    while queue:
        vertex, path = queue.pop(0)
        for nxt in vertex.neighbours:
            if nxt in path: continue
            if nxt == end:
                return path + [nxt]
            else:
                queue.append((nxt, path + [nxt]))
    return None


def getResultPositions(graph, robotPos, mainPoints):
    plist = list(graph.values())
    plist.sort(key=lambda p: getDistanceBetweenPoints(p.pos, tuple(robotPos)))
    start = plist[0]
    mainPoints = [i["name"] for i in mainPoints]
    last = start
    resultPositions = [start.pos]
    for point in mainPoints:
        point = graph[point]
        path = findPathBFS(last, point)
        last = point
        resultPositions += [p.pos for p in path[1:]]
    return resultPositions