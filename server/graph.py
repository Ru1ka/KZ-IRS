class Line:
    def __init__(self, id, startPos=None, endPos=None):
        self.id = id
        self.startPos = startPos
        self.endPos = endPos
        self.points = []

    def addPoint(self, point):
        if not self.startPos:
            self.startPos = point
        self.endPos = point
        self.points.append(point)


class Point:
    def __init__(self, id, pos, line=None, isCrossroad=False, isAruco=False, arucoAngle=None, neighbours=[]):
        self.id = id
        self.pos = pos
        self.line = line
        self.isCrossroad = isCrossroad
        self.isAruco = isAruco
        self.arucoAngle = arucoAngle
        self.isEnd = False
        if not neighbours:
            self.neighbours = []
        else:
            self.neighbours = neighbours

    def addNeighbour(self, point):
        self.neighbours.append(point)

    def isNeighbour(self, point):
        return point in self.neighbours

    def merge(self, point):  # Слияние двух точек (перекрестков)
        self.pos = ((self.pos[0] + point.pos[0]) // 2, (self.pos[1] + point.pos[1]) // 2)
        self.neighbours += point.neighbours