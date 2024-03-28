import socket
import os
import time
import math

from const import ConstPlenty
from aruco import findArucoMarkers, detectAruco
from vision import detectRobot, binOriPonImage, binCenRobImage
from funcs import getDistanceBetweenPoints, getErrorByPoints, angleToPoint
import numpy as np
import cv2

const = ConstPlenty()

class Robot:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop()

    def send(self, message):
        self.sock.sendto(message, (self.ip, self.port))

    def turnRight(self, speed):
        strPath = ':'.join(['0', str(speed)])
        self.send(strPath.encode('utf-8'))

    def turnLeft(self, speed):
        strPath = ':'.join(['1', str(speed)])
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

# CONST
oldError = 0

def saveImage(img):
    cv2.imwrite(os.path.join(const.path.images, f'Camera.png'), img)

def showImage(img, scale=2, winName='ImageScene'):
    shape = img.shape[:2]
    imgShow = cv2.resize(img, list(map(lambda x: int(x * scale), shape[::-1])))
    cv2.imshow(winName, imgShow)
    if cv2.waitKey(1) == 27:
        robot.stop()
        raise ValueError('Exit by user')

def resetRegulator():
    global oldError
    oldError = 0

def angleRegulator(error, maxSpeed, kp, kd):
    global oldError
    if abs(error) < math.radians(8): speed = maxSpeed
    else: speed = 0
    u = error * kp + (error - oldError) * kd
    oldError = error
    print(speed + u, speed - u)
    robot.turnRight(speed + u)
    robot.turnLeft(speed - u)

def rotate360(speedR, speedL, timer=2.5, show=False):
    lastTime = time.time()
    robot.turnRight(speedR)
    robot.turnLeft(speedL)
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
    for numAruco, arucoMarker in enumerate(path):
        print(numAruco, arucoMarker)
        posAruco, angleAruco = arucoMarker
        print('SEARCHING...')
        while True:
            imgScene = cam.read()
            centerRobot, directionPoint = detectRobot(imgScene, show=True)
            if centerRobot and directionPoint: break
            if show: showImage(imgScene)
        print('DONE')
        resetRegulator()
        print('ARRIVE')
        while True:
            imgScene = cam.read()
            if show:
                imgShow = imgScene.copy()
                imgBB = binCenRobImage(imgShow)
                imgB = binOriPonImage(imgShow, imgBB)
                showImage(imgB, winName='FFFFF')
                showImage(imgBB, winName='FFFFF2')
            centerRobot, directionPoint = detectRobot(imgScene)
            if not centerRobot or not directionPoint: continue
            if show:
                cv2.line(imgShow, list(map(int, directionPoint)), list(map(int, centerRobot)), (0, 0, 255), 2)
                cv2.line(imgShow, list(map(int, centerRobot)), list(map(int, posAruco)), (255, 0, 0), 2)
            distance = getDistanceBetweenPoints(centerRobot, posAruco)
            print(f'[DISTANCE]: {distance}')
            if distance < 10: break
            error = getErrorByPoints(directionPoint, posAruco, centerRobot)
            print(f'[ERROR]: {error}, {math.degrees(error)}')
            angleRegulator(error, speed, kp=4, kd=10)
            if show: showImage(imgShow)
        robot.stop()
        time.sleep(1)
        print('DONE')
        directionArucoPoint = angleToPoint(posAruco, angleAruco)
        resetRegulator()
        print('ROTATE')
        while True:
            imgScene = cam.read()
            if show: imgShow = imgScene.copy()
            centerRobot, directionPoint = detectRobot(imgScene)
            if not centerRobot or not directionPoint: continue
            '''if show:
                cv2.line(imgShow, list(map(int, directionPoint)), list(map(int, centerRobot)), (0, 0, 255), 2)
                cv2.line(imgShow, list(map(int, centerRobot)), list(map(int, directionArucoPoint)), (255, 0, 0), 2)'''
            error = getErrorByPoints(directionPoint, directionArucoPoint, centerRobot)
            angleRegulator(error, 0, kp=4, kd=10)
            if show: showImage(imgShow)
            print(f'[ERROR ANLGLE]: {error}')
            if abs(error) < math.radians(10): break
        robot.stop()
        time.sleep(1)
        print('DONE')
        rotate360(60, -55, show=show)

def solve():
    from nto.final import Task
    #task = Task()

    #task.start()
    #route = task.getTask()
    imgScene = cam.read()
    saveImage(imgScene)
    route = None
    resultPath = getResultPath(imgScene, route, show=True)
    print(resultPath)
    driveToArucoMarkers(resultPath, speed=60, show=True)
    #task.stop()

if __name__ == '__main__':
    solve()