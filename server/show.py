import cv2


def showImage(img, winName='Image'):
    while cv2.waitKey(1) != 27: cv2.imshow(winName, img)


def buildGraphShow(img, points, lines):
    imgLines = img.copy()
    for line in lines.values():
        for i in range(len(line.points) - 1):
            cv2.line(imgLines, line.points[i].pos, line.points[i + 1].pos, (0, 0, 255), 2)
    for point in points.values():
        if point.isCrossroad:
            cv2.circle(imgLines, point.pos, 5, (255, 255, 0), 2)
    showImage(imgLines)


def showGraph(img, points):
    imgLines = img.copy()
    # рисуем граф
    for point in points.values():
        for neighbour in point.neighbours:
            cv2.line(imgLines, point.pos, neighbour.pos, (76, 235, 23), 2)
            cv2.circle(imgLines, point.pos, 5, (153, 0, 204), 2)

    showImage(imgLines)


def showLines(img, lines):
    imgLines = img.copy()
    colorA = (0, 0, 255)
    colorB = (0, 100, 255)
    isA = True
    for line in lines:
        for i in range(len(line) - 1):
            if isA:
                color = colorA
            else:
                color = colorB
            isA = not isA
            cv2.line(imgLines, line[i], line[i + 1], color, 2)
    showImage(imgLines)