import cv2
import time
import socket
import os
from const import ConstPlenty
from vision import *
from fastapi import FastAPI

# from detectAruco import detectAruco
from aruco import findArucoMarkers, detectAruco
from vision import getMarkupPositions, detectRobot
from buildGraph import getGraph, refactorGraph, addArucos, addPoints, deletePoints
from algorithms import getRoadLines, extendLines, getResultPositions, routeRefactor
import saveImg as svimg
import show
import saveImg as svImg
from settings import settings

# from nto.final import Task

# const = ConstPlenty()
# task = Task()

class Camera:
    def __init__(self, index, matrix, distortion):
        self.index = index
        self.matrix = matrix
        self.distortion = distortion

    def readRaw(self):
        sceneImages = task.getTaskScene()
        rawImg = sceneImages[self.index]
        return rawImg

    def read(self):
        rawImg = self.readRaw()
        cameraImg = getUndistortedImage(rawImg, self.matrix, self.distortion)
        return cameraImg

    def __str__(self):
        return f'Camera_{self.index}'


class Robot:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.sock.sendto(message, (self.ip, self.port))

    def on(self):
        self.send(b'on')

# robot = Robot('10.128.73.81', 5005)
# cam1 = Camera(0, const.cam1.matrix, const.cam1.distortion)
# cam2 = Camera(1, const.cam2.matrix, const.cam2.distortion)

def solve():
    task = Task()
    task.start()
    print(task.getTask())

    fullImg = getFullScene(cam1.read(), cam2.read())
    cv2.imwrite(os.path.join(const.path.images, f'{cam1}.png'), cam1.read())
    cv2.imwrite(os.path.join(const.path.images, f'{cam2}.png'), cam2.read())
    cv2.imwrite(os.path.join(const.path.images, 'fullImage.png'), fullImg)

    task.stop()
    runWebhook()


def init_task_1(task):
    route = ...
    dictAruco = detectAruco()
    points, route = routeRefactor(route, dictAruco)

def init(task, debug=True):
    img = ...

    route = ...  # загрузить из task

    # Получение точек от cv2
    contours, markupArray = getMarkupPositions()
    dictAruco = detectAruco()
    robotPos = detectRobot()
    if debug:
        svimg.markupPositions(img, contours, markupArray)
        svimg.dictAruco(img, dictAruco)
        svimg.robotPos(img, detectRobot)
        
    # Сборка и продление линий дороги
    roadLines = getRoadLines(markupArray)
    extendedRoadLines = extendLines(roadLines)
    if debug:
        svimg.roadLines(img, roadLines)
        svimg.extendLines(img, extendedRoadLines)
    # Сборка графа
    graph = getGraph(extendedRoadLines, distCrossroads=20)
    if debug:
        svimg.saveGraph(img, graph)

    graph = refactorGraph(graph)  # Двухстороннее движение
    if debug:
        svimg.saveGraph(img, graph)
    graph = addArucos(img, graph, dictAruco, route)
    graph = addPoints(img, graph, route)

    path = getResultPositions(graph, robotPos)
    if debug:
        svimg.savePath(img, path)

    return path

app = FastAPI()

@app.get("/robot_ping")
def robotPing():
    fullImg = getFullScene(cam1.read(), cam2.read())
    centerRobot, directionPoint = detectRobot(fullImg)
    return {'centerRobot': centerRobot, 'directionPoint': directionPoint}

def runWebhook():
    import uvicorn
    uvicorn.run("main:app",
                reload=False,
                host="0.0.0.0",
                port=5400)

def init(task):
    DEBUG = settings().DEBUG

    img = ...

    # route = ...  # загрузить из task

    # Получение точек от cv2
    contours, markupArray = getMarkupPositions()
    dictAruco = detectAruco()
    robotPos, angle = detectRobot()
    if DEBUG:
        svImg.markupPositions(img, contours, markupArray)
        svImg.dictAruco(img, dictAruco)
        svImg.robotPos(img, detectRobot)
        
    # Сборка и продление линий дороги
    roadLines = getRoadLines(markupArray)
    extendedRoadLines = extendLines(roadLines)
    if DEBUG:
        svImg.roadLines(img, roadLines)
        svImg.extendLines(img, extendedRoadLines)
    # Сборка графа
    graph = getGraph(extendedRoadLines, distCrossroads=20)
    if DEBUG: svImg.saveGraph(img, graph)


    graph = refactorGraph(graph)  # Двухстороннее движение
    if DEBUG: svImg.saveGraph(img, graph)
    # graph = addArucos(img, graph, dictAruco, route)
    # graph = addPoints(img, graph, route)

    path = getResultPositions(graph, robotPos)
    if DEBUG: svImg.savePath(img, path)

    return path


def debugLocal():
    DEBUG = settings().DEBUG

    img = cv2.imread("images/87.png")

    # route = ...  # загрузить из task
    route = [
        {"name":"p_1","marker_id":"143"},
        {"name":"p_3","marker_id":"61"},
        {"name":"p_5","marker_id":"21"},
        {"name":"p_6","marker_id":"79"},
    ]

    # Получение точек от cv2
    markupArray = getMarkupPositions(img)
    markerCorners, markerIds = findArucoMarkers(img)
    dictAruco = detectAruco(img, markerCorners, markerIds, 100)
    print(dictAruco)
    # dictAruco = detectAruco(img, 150, show=True)

    # robotPos, angle = detectRobot(img)
    robotPos = (0, 0)
    # Сборка и продление линий дороги
    roadLines = getRoadLines(markupArray)
    show.showLines(img, roadLines)
    extendedRoadLines = extendLines(roadLines)
    show.showLines(img, extendedRoadLines)

    # Сборка графа
    graph = getGraph(extendedRoadLines, distCrossroads=40)
    show.showGraph(img, graph)
    
    graph = refactorGraph(graph)  # Двухстороннее движение
    graph = deletePoints(graph, 270, 300)
    show.showGraph(img, graph)
    graph = addArucos(graph, dictAruco, route)
    show.showGraph(img, graph)
    # graph = addPoints(img, graph, route)

    path = getResultPositions(graph, robotPos, route)
    # show.showResult(img, path, route, dictAruco)
    print(len(path))

    return path


if __name__ == '__main__':
    if settings().LOCAL:
        debugLocal()
    else:
        solve()

'''
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

'''