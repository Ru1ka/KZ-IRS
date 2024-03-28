import socket
import os
import time
import math

from const import ConstPlenty
from aruco import findArucoMarkers, detectAruco
from vision import detectRobot
from funcs import getDistanceBetweenPoints, getErrorByPoints, angleToPoint
import numpy as np
import cv2

from nto.final import Task

const = ConstPlenty()
task = Task()

class Robot:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop()

    def send(self, message):
        self.sock.sendto(message, (self.ip, self.port))

    def turnRight(self, speed):
        strPath = ':'.join(['1', str(speed)])
        self.send(strPath.encode('utf-8'))

    def turnLeft(self, speed):
        strPath = ':'.join(['0', str(speed)])
        self.send(strPath.encode('utf-8'))

    def stop(self):
        for dir in '01':
            strPath = ':'.join([dir, '0'])
            self.send(strPath.encode('utf-8'))


class Camera:
    def __init__(self, index):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)
        self.cap.set(cv2.CAP_PROP_FOCUS, 0)
        self.cap.set(cv2.CAP_PROP_SATURATION, 0)

    def read(self):
        success, img = self.cap.read()
        return img if success else None

    def release(self):
        self.cap.release()

robot = Robot('10.128.73.116', 5005)
cam = Camera(index=2)

def saveImage(img):
    cv2.imwrite(os.path.join(const.path.images, f'Camera.png'), img)

def showImage(img, winName='ImageScene'):
    cv2.imshow(winName, img)
    if cv2.waitKey(1) == 27: raise ValueError('Exit by user')

def angleRegulator(error, maxSpeed, kp=1):
    if abs(error) < math.radians(20): speed = maxSpeed
    else: speed = 0
    u = error * kp
    print(speed + u, speed - u)
    robot.turnRight(speed + u)
    robot.turnLeft(speed - u)

def rotate360(speed, timer=16, show=False):
    lastTime = time.time()
    robot.turnRight(speed)
    robot.turnLeft(-speed)
    while lastTime + timer > time.time():
        if show:
            imgScene = cam.read()
            showImage(imgScene)
    robot.stop()

def getResultPath(img, route, show=False):
    markerCorners, markerIds = findArucoMarkers(img, show=show)
    arucoPositions = detectAruco(img, markerCorners, markerIds)
    resultPath = []
    route = [{'marker_id': 2}, {'marker_id': 55}, {'marker_id': 205}]
    for aruco in route:
        markerId = aruco['marker_id']
        if f'p_{markerId}' in arucoPositions:
            resultPath.append(arucoPositions[f'p_{markerId}'])
    return resultPath

def driveToArucoMarkers(path, speed, show=False):
    for arucoMarker in path:
        imgScene = cam.read()
        posAruco, angleAruco = arucoMarker
        centerRobot, directionPoint = detectRobot(imgScene)
        while getDistanceBetweenPoints(centerRobot, posAruco) < 10:
            imgScene = cam.read()
            centerRobot, directionPoint = detectRobot(imgScene)
            error = getErrorByPoints(directionPoint, posAruco, centerRobot)
            angleRegulator(error, speed)
            if show: showImage(imgScene)
        robot.stop()
        directionArucoPoint = angleToPoint(posAruco, angleAruco)
        while True:
            imgScene = cam.read()
            centerRobot, directionPoint = detectRobot(imgScene)
            error = getErrorByPoints(directionPoint, directionArucoPoint, centerRobot)
            angleRegulator(error, 0)
            if show: showImage(imgScene)
            if abs(error) < math.radians(10): break
        robot.stop()
        rotate360(speed, show=show)

def solve():
    task.start()
    route = task.getTask()
    imgScene = cam.read()
    saveImage(imgScene)
    resultPath = getResultPath(imgScene, route, show=True)
    print(resultPath)
    driveToArucoMarkers(resultPath, speed=120, show=True)
    task.stop()

if __name__ == '__main__':
    solve()