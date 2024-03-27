import cv2
import time
import socket
import os
from const import ConstPlenty
from vision import *

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
    #robot.on()

    cam1 = Camera(0, const.cam1.matrix, const.cam1.distortion)
    cam2 = Camera(1, const.cam2.matrix, const.cam2.distortion)
    fullImg = getFullScene(cam1.read(), cam2.read())

    cv2.imwrite(os.path.join(const.path.images, f'{cam1}.png'), cam1.read())
    cv2.imwrite(os.path.join(const.path.images, f'{cam2}.png'), cam2.read())
    task.stop()


def load_task(n):
    pass


def init(debug=True):
    from vision import detectAruco, getMarkupPositions, detectRobot
    from buildGraph import getGraph, refactorGraph
    from algorithms import getRoadLines, extendLines, getResultPositions
    import saveImg as svimg

    # Получение точек от cv2
    markupArray = getMarkupPositions()
    dictAruco = detectAruco()
    robotPos = detectRobot()
    if debug:
        pass
        
    # Сборка и продление линий дороги
    roadLines = getRoadLines(markupArray)
    extendedRoadLines = extendLines(roadLines)
    # Сборка графа
    graph = getGraph(extendedRoadLines, distCrossroads=20)
    graph = refactorGraph(graph)  # Двухстороннее движение

    # graph = addArucos(img, graph, dictAruco, mainPoints)  # Связь графом с ArUco метками
    # graph = addPoints(img, graph, mainPoints)  # Связь графа c другими точками (веротяно не нужно)

    # path = getResultPositions(graph, robotPos)


if __name__ == '__main__':
    solve()