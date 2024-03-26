import cv2
import time
import socket


## Здесь должно работать ваше решение
def solve():
    from nto.final import Task
    '''## Пример отправки сообщения на робота по протоколу udp
    UDP_IP = '192.168.2.137'
    UDP_PORT = 5005
    MESSAGE = b'Hello, World!'

    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))'''

    ## Запуск задания и таймера (внутри задания)
    task = Task()
    task.start()
    print(task.getTask())

    sceneImg = task.getTaskScene()
    cv2.imwrite('images/Camera1.png', sceneImg[0])
    cv2.imwrite('images/Camera2.png', sceneImg[1])
    task.stop()


def load_task(n):
    pass


def init():
    from vision import detectAruco, getMarkupPositions, detectRobot
    from buildGraph import getGraph, refactorGraph
    from algorithms import getRoadLines, extendLines, getResultPositions

    # Получение точек от cv2
    markupArray = getMarkupPositions()
    dictAruco = detectAruco()
    robotPos = detectRobot()
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