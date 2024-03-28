import cv2
from aruco import findArucoMarkers, detectAruco
from vision import showImage
import numpy as np
cap = cv2.VideoCapture(2)
import math

def angleToPoint(centralPoint, angle, d=1):
    angle = math.radians(360 - (math.degrees(angle) + 90))
    x, y = centralPoint
    nx = x + d * math.cos(angle)
    ny = y + d * math.sin(angle)
    return nx, ny

#cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)
#cap.set(cv2.CAP_PROP_FOCUS, 0)
#cap.set(cv2.CAP_PROP_SATURATION, 0)

while True:
    success, img = cap.read()
    markerCorners, markerIds = findArucoMarkers(img, timer=0.01, show=True)
    arucos = detectAruco(img, markerCorners, markerIds)
    for ar, cors in arucos.items():
        print(cors)
        anglePoint = angleToPoint(cors[:2], cors[2], d=20)
        print(anglePoint)
        cv2.line(img, list(map(int, cors[:2])), list(map(int, anglePoint)), (0, 200, 0), 2)
        cv2.putText(img, str(round(math.degrees(cors[2]), 2)), list(map(int, cors[:2])), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
    cv2.imshow('Image', img)
    cv2.waitKey(1)
print(arucos)