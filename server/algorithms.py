from functools import lru_cache
from math import hypot, ceil

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