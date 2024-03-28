import socket
import os
from const import ConstPlenty
from vision import *
from aruco import findArucoMarkers, detectAruco
from fastapi import FastAPI
import cv2
import time

from nto.final import Task

const = ConstPlenty()
task = Task()

class Camera:
    def __init__(self, index, matrix, distortion):
        self.index = index
        self.matrix = matrix
        self.distortion = distortion
        self.cap = cv2.VideoCapture(2)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)
        self.cap.set(cv2.CAP_PROP_FOCUS, 0)
        self.cap.set(cv2.CAP_PROP_SATURATION, 0)

    def read(self):
        success, rawImg = self.cap.read()
        return rawImg if success else None

    def __str__(self):
        return f'Camera_{self.index}'


class Robot:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.sock.sendto(message, (self.ip, self.port))

    def sendPath(self, path):
        strPath = ';'.join([','.join(list(map(str, pos))) for pos in path])+';'
        print(strPath)
        self.send(strPath.encode('utf-8'))

robot = Robot('10.128.73.116', 5005)
cam = Camera(0, const.cam.matrix, const.cam.distortion)

## Здесь должно работать ваше решение
def solve():
    task.start()
    saveImage()
    path = getResultPath(eval(task.getTask()))
    robot.sendPath(path)
    runWebhook()
    task.stop()

def saveImage():
    cv2.imwrite(os.path.join(const.path.images, f'{cam}.png'), cam.read())

def getResultPath(route):
    imgScene = cam.read()
    markerCorners, markerIds = findArucoMarkers(imgScene, show=False)
    arucoPositions = detectAruco(imgScene, markerCorners, markerIds)
    print(len(arucoPositions), arucoPositions)
    resultPath = []
    route = [{'marker_id': 2}, {'marker_id': 55}, {'marker_id': 205}]
    for aruco in route:
        markerId = aruco['marker_id']
        if f'p_{markerId}' in arucoPositions:
            resultPath.append(arucoPositions[f'p_{markerId}'])
    print(resultPath)
    return resultPath

app = FastAPI()

@app.get("/robot/pos")
def robotPos():
    imgScene = cam.read()
    centerRobot, directionPoint = detectRobot(imgScene)
    positions = '0,0,0;'
    positions += ','.join(list(map(str, centerRobot))+['0'])+';'
    positions += ','.join(list(map(str, directionPoint))+['0'])+';'
    return positions

"""p1 = '9,4,1488;10,4,1488;'
p2 = '9,9,1488;9,10,1488;'
p3 = '4,9,1488;3,9,1488;'"""

def runWebhook():
    import uvicorn
    uvicorn.run("main:app",
                reload=False,
                host="0.0.0.0",
                port=5400)


if __name__ == '__main__':
    solve()