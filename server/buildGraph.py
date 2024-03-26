from graph import Line, Point
from algorithms import getDistanceBetweenPoints, getPosRightSideSegment

def addCrossroads(points, lines, dist):
    # PS тут много квадратичных сложностей, но концов точек меньше 200 штук, а перекрестков еще меньше
    # поэтому можно не париться

    startsEndsPoints = []
    for line in lines.values():
        startsEndsPoints.append(line.startPos)
        startsEndsPoints.append(line.endPos)

    # minDistBetweenLines = float('+inf')
    # for point1, point2 in combinations(startsEndsPoints, 2):
    #     minDistBetweenLines = min(getDistanceBetweenPoints(point1.pos, point2.pos), minDistBetweenLines)
    minRoadDist = float('+inf')
    for line in lines.values():
        if getDistanceBetweenPoints(line.points[0].pos, line.points[-1].pos) > dist:
            minRoadDist = min(minRoadDist, getDistanceBetweenPoints(line.points[0].pos, line.points[-1].pos))

    crossroads = []
    while startsEndsPoints:
        query = [startsEndsPoints.pop()]
        crossroad = []
        while query:
            point = query.pop()
            crossroad += [point]
            for i in range(len(startsEndsPoints) - 1, -1, -1):
                point2 = startsEndsPoints[i]
                if getDistanceBetweenPoints(point.pos, point2.pos) < minRoadDist * 0.9995:
                    query.append(point2)
                    startsEndsPoints.pop(i)

        # Если 2 точки принадлежат одной линии, то выбираем ту, которая ближе к остальным точкам
        # for point1 in crossroad:
        #     for point2 in crossroad:
        #         if point1 == point2: continue
        #         elif point1.line == point2.line:
        #             dist1 = sum([getDistanceBetweenPoints(point1.pos, point.pos) for point in crossroad])
        #             dist2 = sum([getDistanceBetweenPoints(point2.pos, point.pos) for point in crossroad])
        #             if dist1 < dist2:
        #                 crossroad.remove(point1)
        #             else:
        #                 crossroad.remove(point2)
        crossroads.append(crossroad)

    crossroadId = len(points) + 10000
    newCrossroads = []
    for crossroad in crossroads:
        x = round(sum([point.pos[0] for point in crossroad]) / len(crossroad))
        y = round(sum([point.pos[1] for point in crossroad]) / len(crossroad))
        pos = (x, y)
        point = Point(crossroadId, pos, isCrossroad=True, neighbours=crossroad)
        points[crossroadId] = point

        for p in crossroad:
            p.addNeighbour(point)

        crossroadId += 1
        newCrossroads.append(point)
    crossroads = newCrossroads

    # Если расстояние между 2 центрами меньше минимальной длины принадлежащих им линий, то соединяем их в один перекресток
    # to_merge = []
    # for point1 in crossroads:
    #     for point2 in crossroads:
    #         if point1 == point2 or getDistanceBetweenPoints(point1.pos, point2.pos) > 20: continue
    #         minDistance = float('+inf')
    #         for neighbour in point1.neighbours + point2.neighbours:
    #             dist = getDistanceBetweenPoints(neighbour.line.startPos.pos, neighbour.line.endPos.pos)
    #             minDistance = min(minDistance, dist)
    #         if minDistance * 1.1 > getDistanceBetweenPoints(point1.pos, point2.pos):
    #             to_merge.append((point1, point2))

    # print(to_merge)
    # for point1, point2 in to_merge:
    #     point1.merge(point2)
    #     points.pop(point2.id)
    #     crossroads.remove(point2)

    # # Удаляем крайние точки линий
    # print(len(points))
    # for line in lines.values():
    #     p1 = line.points.pop(0)
    #     p2 = line.points.pop(-1)
    #     line.startPos = line.points[0]
    #     line.endPos = line.points[-1]

    #     points.pop(p1.id)
    #     points.pop(p2.id)

    #     for point in p1.neighbours:
    #         point.neighbours.remove(p1)
    #         for point2 in p1.neighbours:
    #             if point2 == point: continue
    #             if point2 not in point.neighbours:
    #                 point.neighbours.append(point2)
    #                 point2.neighbours.append(point)
    #     for point in p2.neighbours:
    #         point.neighbours.remove(p2)
    #         for point2 in p2.neighbours:
    #             if point2 == point: continue
    #             if point2 not in point.neighbours:
    #                 point.neighbours.append(point2)
    #                 point2.neighbours.append(point)

    # print(len(points))

    return points


def getGraph(lines, distCrossroads=20):
    # Рефакторим данные, тк на данном этапе требуется двухсторонняя связь
    points = {}
    newLines = {}
    idLines = 0
    idPoints = 0
    for line in lines:
        newLine = Line(idLines)
        isFirst = True
        for pos in line:
            point = Point(idPoints, pos, newLine)
            points[idPoints] = point
            newLine.addPoint(point)
            if not isFirst:
                points[idPoints - 1].addNeighbour(point)
                point.addNeighbour(points[idPoints - 1])
            idPoints += 1
            isFirst = False
        newLines[idLines] = newLine
        idLines += 1
    lines = newLines

    points = addCrossroads(points, lines, distCrossroads)

    for line in lines.values():
        line.endPos.isEnd = True
        line.startPos.isEnd = True

    return points


def refactorGraph(points):
    crossroads = list(filter(lambda p: p.isCrossroad, points.values()))
    newPoints = {}
    congruence = {}
    idInt = 0
    for crossroad in crossroads:
        newCrossroad = Point(idInt, crossroad.pos, isCrossroad=True)
        newPoints[idInt] = newCrossroad
        congruence[crossroad.id] = newCrossroad
        idInt += 1

    for crossroad in crossroads:
        newCrossroad = congruence[crossroad.id]
        for point in crossroad.neighbours:
            last = crossroad
            cur = point
            lastNewPoint = newCrossroad
            first = True
            while True:
                if cur.isCrossroad:
                    lastNewPoint.addNeighbour(congruence[cur.id])
                    break
                if not first:
                    newPos = getPosRightSideSegment(last.pos, cur.pos)
                else:
                    newPos = cur.pos
                    first = False
                newPoint = Point(idInt, newPos)
                lastNewPoint.addNeighbour(newPoint)
                newPoints[idInt] = newPoint
                idInt += 1
                if cur.isCrossroad:
                    break
                for nxt in cur.neighbours:
                    if nxt != last:
                        last = cur
                        cur = nxt
                        lastNewPoint = newPoint
                        break

    return newPoints


def addArucos(points, arucos, mainPoints):
    acucoId2PointId = {}
    for point in mainPoints:
        if "marker_id" in point:
            acucoId2PointId[f'p_{point["marker_id"]}'] = point["name"]

    pointsList = list(points.values())
    for arucoId, aruco in arucos.items():
        pointsList.sort(key=lambda p: getDistanceBetweenPoints(p.pos, aruco))
        # Берем 3 точки, сортируем по ходу движения
        closest = pointsList[:3]
        first = closest
        for i in closest:
            for neighbour in i.neighbours:
                if neighbour in closest:
                    first.remove(neighbour)
        first = first[0]
        closest2 = [first]
        for i in range(2):
            closest2.append(closest2[-1].neighbours[0])
        closest = closest2
        if arucoId in acucoId2PointId:
            pointId = acucoId2PointId[arucoId]
        else:
            pointId = f'p_{arucoId}'
        arucoPoint = Point(pointId, aruco, isAruco=True, neighbours=[closest[2]])
        points[pointId] = arucoPoint
        closest[0].addNeighbour(arucoPoint)

    return points


def addPoints(points, addPoints):
    pointsList = list(points.values())
    for pointData in addPoints:
        if "coordinates" in pointData and pointData["name"] not in points:
            pointsList.sort(key=lambda p: getDistanceBetweenPoints(p.pos, tuple(pointData["coordinates"])))
            closest = pointsList[0]
            if closest.isCrossroad:
                newPoint = Point(pointData["name"], tuple(pointData["coordinates"]), neighbours=[closest])
                points[pointData["name"]] = newPoint
                closest.addNeighbour(newPoint)
            else:
                closest.pos = tuple(pointData["coordinates"])
                points.pop(closest.id)
                closest.id = pointData["name"]
                points[pointData["name"]] = closest

    return points