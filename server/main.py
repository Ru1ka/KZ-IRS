import cv2
import time
import socket
import os
import math
import numpy as np
from const import ConstPlenty
from vision import *

# from detectAruco import detectAruco
from graph import serialize, deserialize
from funcs import getDistanceBetweenPoints, getErrorByPoints, angleToPoint
from aruco import findArucoMarkers, detectAruco
from vision import getMarkupPositions, detectRobot, binOriPonImage, binCenRobImage
from buildGraph import getGraph, refactorGraph, addArucos, addPoints, deletePoints
from algorithms import getRoadLines, extendLines, getResultPositions, routeRefactor
import show
import saveImg as svImg
from settings import settings


from const import ConstPlenty
from vision import detectRobot, binOriPonImage, binCenRobImage


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

if not settings().LOCAL:
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

def solve(filename="data.json"):
    from nto.final import Task
    task = Task()

    task.start()
    route = task.getTask()
    imgScene = cam.read()
    saveImage(imgScene)
    route = None
    resultPath = getResultPath(imgScene, route, show=True)
    print(resultPath)
    driveToArucoMarkers(resultPath, speed=60, show=True)
    #task.stop()


def initServer(img, route, filename="data.json"):
    robotPos, angle = detectRobot(img)
    graph, dictAruco = deserialize(filename)
    graph = addArucos(graph, dictAruco, route)
    svImg.saveGraph(graph)
    graph = addPoints(img, graph, route)
    svImg.saveGraph(graph)
    path = getResultPositions(graph, robotPos, route)

    return path

def debugLocal():
    img = cv2.imread(settings().IMAGEFILE)

    # route = ...  # загрузить из task
    from random import shuffle
    route = [
        {"name":"p_1","marker_id":"125"},
        {"name":"p_2","marker_id":"229"},
        {"name":"p_3","marker_id":"97"},
        {"name":"p_4","marker_id":"205"},
        {"name":"p_5","marker_id":"21"},
        # {"name":"p_6","marker_id":"61"},
        # {"name":"p_7","marker_id":"215"},
        # {"name":"p_8","marker_id":"191"},
        # {"name":"p_9","marker_id":"247"},
        # {"name":"p_10","marker_id":"343"},
        # {"name":"p_11","marker_id":"102"},
        # {"name":"p_12","marker_id":"13"},
        # {"name":"p_13","marker_id":"2"},
        # {"name":"p_14","marker_id":"115"},
        # {"name":"p_15","marker_id":"33"},
        # {"name":"p_16","marker_id":"44"},
        # {"name":"p_17","marker_id":"143"},
        # {"name":"p_18","marker_id":"79"},
        # {"name":"p_19","marker_id":"118"},
    ]
    # shuffle(route)
    # route *= 3
    # route = route[:50]
    # Получение точек от cv2
    markupArray = getMarkupPositions(img)
    markerCorners, markerIds = findArucoMarkers(img)
    
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

    dictAruco = detectAruco(img, markerCorners, markerIds, 90)
    
    serialize(graph, dictAruco)

    # -----////----- #
    if settings().DEBUG:
        graph = addArucos(graph, dictAruco, route)
        show.showGraph(img, graph)
        # graph = addPoints(img, graph, route)
        # show.showGraph(img, graph)

        path = getResultPositions(graph, robotPos, route)
        show.showResult(img, path, route, dictAruco)
        print(len(path))
     # -----////----- #

    return path


def InitLocal(filename="data.json"):
    route = [
        {"name":"p_1","marker_id":"125"},
        {"name":"p_2","marker_id":"229"},
        {"name":"p_3","marker_id":"97"},
        {"name":"p_4","marker_id":"205"},
        {"name":"p_5","marker_id":"21"},
        # {"name":"p_6","marker_id":"61"},
        # {"name":"p_7","marker_id":"215"},
        # {"name":"p_8","marker_id":"191"},
        # {"name":"p_9","marker_id":"247"},
        # {"name":"p_10","marker_id":"343"},
        # {"name":"p_11","marker_id":"102"},
        # {"name":"p_12","marker_id":"13"},
        # {"name":"p_13","marker_id":"2"},
        # {"name":"p_14","marker_id":"115"},
        # {"name":"p_15","marker_id":"33"},
        # {"name":"p_16","marker_id":"44"},
        # {"name":"p_17","marker_id":"143"},
        # {"name":"p_18","marker_id":"79"},
        # {"name":"p_19","marker_id":"118"},
    ]
    img = cv2.imread(settings().IMAGEFILE)
    robotPos = (0, 0)
    graph, dictAruco = deserialize(filename)
    graph = addArucos(graph, dictAruco, route)
    # show.showGraph(img, graph)
    # graph = addPoints(img, graph, route)
    show.showGraph(img, graph)
    path = getResultPositions(graph, robotPos, route)
    show.showResult(img, path, route, dictAruco)
    return path

if __name__ == '__main__':
    if settings().DEBUG:
        debugLocal()
    else:
        if settings().LOCAL:
            InitLocal()
        else:
            solve()