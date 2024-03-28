import socket
import os
from const import ConstPlenty
from vision import *
from fastapi import FastAPI
import cv2

from nto.final import Task

const = ConstPlenty()
task = Task()

class Camera:
    def __init__(self, index, matrix, distortion):
        self.index = index
        self.matrix = matrix
        self.distortion = distortion

    def read(self):
        sceneImages = task.getTaskScene()
        rawImg = sceneImages[self.index]
        return rawImg

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
        strPath = ';'.join([','.join(list(map(str, pos))) for pos in path])
        self.send(strPath.encode('utf-8'))

robot = Robot('10.128.73.81', 5005)
cam = Camera(0, const.cam.matrix, const.cam.distortion)

## Здесь должно работать ваше решение
def solve():
    task.start()
    saveImage()
    path = getResultPath(eval(task.getTask()))
    robot.sendPath(path)
    task.stop()
    runWebhook()

def saveImage():
    cv2.imwrite(os.path.join(const.path.images, f'{cam}.png'), cam.read())

def getResultPath(route):
    imgScene = cam.read()
    arucoPositions = detectAruco(imgScene)
    resultPath = []
    for aruco in route:
        markerId = aruco['marker_id']
        if f'p_{markerId}' in arucoPositions:
            resultPath.append(arucoPositions[f'p_{markerId}'])
    print(resultPath)
    return resultPath

app = FastAPI()

@app.get("/robot/pos")
def robotPing():
    imgScene = cam.read()
    centerRobot, directionPoint = detectRobot(imgScene)
    return {'centerRobot': centerRobot, 'directionPoint': directionPoint}

def runWebhook():
    import uvicorn
    uvicorn.run("main:app",
                reload=False,
                host="0.0.0.0",
                port=5400)


if __name__ == '__main__':
    solve()