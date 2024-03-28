import cv2
from docker.solution.aruco import findArucoMarkers, detectAruco
import numpy as np
cap = cv2.VideoCapture(2)

cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)
cap.set(cv2.CAP_PROP_FOCUS, 0)
cap.set(cv2.CAP_PROP_SATURATION, 0)

success, img = cap.read()
markerCorners, markerIds = findArucoMarkers(img, show=True)
arucos = detectAruco(img, markerCorners, markerIds)

print(arucos)