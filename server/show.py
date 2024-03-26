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