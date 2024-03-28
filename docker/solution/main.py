import time
import math
import os

from const import ConstPlenty
from aruco import findArucoMarkers, detectAruco
from vision import detectRobot, binOriPonImage, binCenRobImage
from funcs import getDistanceBetweenPoints, getErrorByPoints, angleToPoint
from devices import Camera, Robot
import numpy as np
import cv2

const = ConstPlenty()
robot = Robot('10.128.73.116', 5005)
cam = Camera(index=2)

def saveImage(img):
    cv2.imwrite(os.path.join(const.path.images, f'Camera.png'), img)

def showImage(img, scale=2, winName='ImageScene'):
    shape = img.shape[:2]
    imgShow = cv2.resize(img, list(map(lambda x: int(x * scale), shape[::-1])))
    cv2.imshow(winName, imgShow)
    if cv2.waitKey(1) == 27:
        robot.stop()
        raise ValueError('Exit by user')

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
        robot.resetRegulator()
        while True:
            imgScene = cam.read()
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
            robot.angleRegulator(error, speed)
            if show: showImage(imgShow)
        robot.stop()
        time.sleep(1)
        print('DONE')
        directionArucoPoint = angleToPoint(posAruco, angleAruco)
        robot.resetRegulator()
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
            robot.angleRegulator(error, 0, kp=4, kd=10)
            if show: showImage(imgShow)
            print(f'[ERROR ANLGLE]: {error}')
            if abs(error) < math.radians(10): break
        robot.stop()
        time.sleep(1)
        print('DONE')
        rotate360(60, -55, show=show)

def solve():
    from nto.final import Task
    task = Task()

    task.start()
    route = task.getTask()
    imgScene = cam.read()
    saveImage(imgScene)
    resultPath = getResultPath(imgScene, route, show=True)
    print(resultPath)
    driveToArucoMarkers(resultPath, speed=60, show=True)
    task.stop()

if __name__ == '__main__':
    solve()