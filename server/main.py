import cv2
import time
import socket
import os
from const import ConstPlenty
from vision import *
from fastapi import FastAPI

from vision import detectAruco, getMarkupPositions, detectRobot
from buildGraph import getGraph, refactorGraph, addArucos, addPoints
from algorithms import getRoadLines, extendLines, getResultPositions, routeRefactor
import saveImg as svimg

app = FastAPI()

# вывести текущую директорию
const = ConstPlenty()

## Здесь должно работать ваше решение
def solve():
    from nto.final import Task

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

    task = Task()
    task.start()
    print(task.getTask())

    robot = Robot('10.128.73.81', 5005)
    robot.on()

    cam1 = Camera(0, const.cam1.matrix, const.cam1.distortion)
    cam2 = Camera(1, const.cam2.matrix, const.cam2.distortion)

    cv2.imwrite(os.path.join(const.path.images, f'{cam1}.png'), cam1.read())
    cv2.imwrite(os.path.join(const.path.images, f'{cam2}.png'), cam2.read())

    # cur = 0
    # path = init()

    @app.get("/robot_ping")
    def robot_ping():
        return {"position", detectRobot()}

    task.stop()


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


if __name__ == '__main__':
    solve()