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

    img = cv2.imread("images/86.png")

    # route = ...  # загрузить из task

    # Получение точек от cv2
    markupArray = getMarkupPositions(img)
    markerCorners, markerIds = findArucoMarkers(img)
    dictAruco = detectAruco(img, markerCorners, markerIds, 100)
    # dictAruco = detectAruco(img, 150, show=True)

    # robotPos, angle = detectRobot()
    # Сборка и продление линий дороги
    roadLines = getRoadLines(markupArray)
    show.showLines(img, roadLines)
    extendedRoadLines = extendLines(roadLines)
    show.showLines(img, extendedRoadLines)

    # Сборка графа
    graph = getGraph(extendedRoadLines, distCrossroads=40)
    show.showGraph(img, graph)

    graph = refactorGraph(graph)  # Двухстороннее движение
    graph = deletePoints(graph, 275, 300)
    show.showGraph(img, graph)
    graph = addArucos(graph, dictAruco)
    show.showGraph(img, graph)
    # graph = addPoints(img, graph, route)

    # path = getResultPositions(graph, robotPos)

    # return path


if __name__ == '__main__':
    if settings().LOCAL:
        debugLocal()
    else:
        solve()