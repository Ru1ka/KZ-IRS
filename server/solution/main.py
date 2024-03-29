import os
from vision import *

# from detectAruco import detectAruco
from graph import serialize, deserialize
from aruco import findArucoMarkers, detectAruco
from vision import getMarkupPositions
from buildGraph import getGraph, refactorGraph, addArucos, deletePoints, addPoints
from algorithms import getRoadLines, extendLines, getResultPositions
from funcs import getDistanceBetweenPoints, getErrorByPoints, angleToPoint
import show
import saveImg as svImg
# from settings import settings

import time

from devices import Camera, Robot


from const import ConstPlenty
from vision import detectRobot

const = ConstPlenty()
LOCAL = True
DEBUG = True
IMAGE_FILE = "88.png"

if not LOCAL and not DEBUG:
    from nto.final import Task
    task = Task()

    robot = Robot('10.128.73.116', 5005)
    cam1 = Camera('http://student:nto2024@10.128.73.31/mjpg/video.mjpg', const.cam1.matrix, const.cam1.distortion)
    cam2 = Camera('http://student:nto2024@10.128.73.38/mjpg/video.mjpg', const.cam2.matrix, const.cam2.distortion)

def saveImage(img, fileName='Camera.png'):
    cv2.imwrite(os.path.join(const.path.images, fileName), img)

def showImage(img, scale=2, winName='ImageScene'):
    shape = img.shape[:2]
    imgShow = cv2.resize(img, list(map(lambda x: int(x * scale), shape[::-1])))
    cv2.imshow(winName, imgShow)
    if cv2.waitKey(1) == 27:
        robot.stop()
        raise ValueError('Exit by user')

def getScene():
    return getFullScene(cam1.read(), cam2.read())

def solve(fileName='/solution/data.json'):
    task.start()

    route = eval(task.getTask())[1:]
    # route = [{'name': 'p_2', 'marker_id': '2'}, {'name': 'p_3', 'marker_id': '247'}, {'name': 'p_6', 'marker_id': '215'}, {'name': 'p_7', 'marker_id': '97'}]
    imgScene = getScene()
    saveImage(imgScene)
    resultPath = initServer(imgScene, route, fileName)
    driveByPath(resultPath, speed=60, show=False, debug=True)

    robot.stop()
    task.stop()

def driveForwardToPoint(posPoint, speed, show=False, debug=False):
    robot.resetRegulator()
    while True:
        imgScene = getScene()
        centerRobot, directionPoint = detectRobot(imgScene)
        if not centerRobot or not directionPoint: continue
        distance = getDistanceBetweenPoints(centerRobot, posPoint)
        if debug: print(f'[DISTANCE]: {distance}')
        if distance < 10: break
        error = getErrorByPoints(directionPoint, posPoint, centerRobot)
        if debug: print(f'[ERROR ANGLE]: {error}, {math.degrees(error)}')
        robot.angleRegulator(error, speed)
        if show:
            imgShow = imgScene.copy()
            cv2.line(imgShow, list(map(int, directionPoint)), list(map(int, centerRobot)), (0, 0, 255), 2)
            cv2.line(imgShow, list(map(int, centerRobot)), list(map(int, posPoint)), (255, 0, 0), 2)
            showImage(imgShow)
    robot.stop()

def driveRotateToAngle(anglePoint, angleLimit, show=False, debug=False):
    imgScene = getScene()
    centerRobot, directionPoint = detectRobot(imgScene, show=show)
    directionArucoPoint = angleToPoint(centerRobot, anglePoint, d=35)
    robot.resetRegulator()
    while True:
        imgScene = getScene()
        centerRobot, directionPoint = detectRobot(imgScene)
        if not centerRobot or not directionPoint: continue
        error = getErrorByPoints(directionPoint, directionArucoPoint, centerRobot)
        if debug: print(f'[ERROR ANGLE]: {error}')
        if abs(error) < math.radians(angleLimit): break
        robot.angleRegulator(error, 0, kp=4, kd=10)
        if show:
            imgShow = imgScene.copy()
            cv2.line(imgShow, list(map(int, directionPoint)), list(map(int, centerRobot)), (0, 0, 255), 2)
            cv2.line(imgShow, list(map(int, centerRobot)), list(map(int, directionArucoPoint)), (255, 0, 0), 2)
            cv2.circle(imgShow, list(map(int, directionArucoPoint)), 3, (0, 255, 0), -1)
            showImage(imgShow)
    robot.stop()

def driveByPath(path, speed, show=False, debug=False):
    for numPoint, point in enumerate(path):
        posPoint, anglePoint = point
        if debug: print(f'[ARUCO]: {posPoint} | {anglePoint}')
        if debug: print('SEARCHING ROBOT...')
        while True:
            imgScene = getScene()
            centerRobot, directionPoint = detectRobot(imgScene, show=show)
            if centerRobot and directionPoint: break
            if show: showImage(imgScene)
        if debug: print('FORWARD')
        driveForwardToPoint(posPoint, speed, show, debug)
        if anglePoint is None: continue
        time.sleep(1)
        if debug: print('ROTATE')
        driveRotateToAngle(anglePoint, angleLimit=7, show=show, debug=debug)
        time.sleep(1)
        if debug: print('ROTATE 360')
        robot.rotate360()

def initServer(img, route, fileName):
    robotPos, angle = detectRobot(img)
    graph, dictAruco = deserialize(fileName)
    graph = addArucos(graph, dictAruco, route)
    # graph = addPoints(img, graph, route)
    path = getResultPositions(graph, robotPos, route)

    res = []
    for point in path:
        if point.isAruco:
            res += [(point.pos, point.arucoAngle)]
        else:
            res += [(point.pos, None)]

    return res

def debugLocal():
    img = cv2.imread('Camera.png')

    # route = ...  # загрузить из tasks
    route = [
        {"name":"p_1","marker_id":"125"},
        {"name":"p_2","marker_id":"229"},
        {"name":"p_3","marker_id":"97"},
        {"name":"p_4","marker_id":"205"},
        {"name":"p_5","marker_id":"21"},
        {"name":"p_6","marker_id":"61"},
        {"name":"p_7","marker_id":"215"},
        {"name":"p_8","marker_id":"191"},
        {"name":"p_9","marker_id":"247"},
        {"name":"p_10","marker_id":"343"},
        {"name":"p_11","marker_id":"102"},
        {"name":"p_12","marker_id":"13"},
        {"name":"p_13","marker_id":"2"},
        {"name":"p_14","marker_id":"115"},
        {"name":"p_15","marker_id":"33"},
        {"name":"p_16","marker_id":"44"},
        {"name":"p_17","marker_id":"143"},
        {"name":"p_18","marker_id":"79"},
        {"name":"p_12","marker_id":"13"},
        {"name":"p_19","marker_id":"118"},
    ]
    route = [{
        "name":"p_1","marker_id":"143"},{"name":"p_2","coordinates":[361,523]},
        {"name":"p_3","marker_id":"61"},{"name":"p_4","coordinates":[977,217]},
        {"name":"p_5","marker_id":"21"},{"name":"p_6","marker_id":"79"},
        {"name":"p_7","coordinates":[347,153]},
        {"name":"p_8","coordinates":[863,496]},
        {"name":"p_9","coordinates":[565,501]},
        {"name":"p_10","coordinates":[393,227]}]
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
    extendedRoadLines = extendLines(roadLines)

    # Сборка графа
    graph = getGraph(extendedRoadLines, distCrossroads=40)
    
    graph = refactorGraph(graph)  # Двухстороннее движение
    graph = deletePoints(graph, 270, 300)
    show.showGraph(img, graph)

    dictAruco = detectAruco(img, markerCorners, markerIds, 100)
    
    serialize(graph, dictAruco)

    # -----////----- #
    if DEBUG:
        graph = addArucos(graph, dictAruco, route)
        graph = addPoints(graph, route)
        show.showGraph(img, graph)


        path = getResultPositions(graph, robotPos, route)
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
        {"name":"p_12","marker_id":"13"},
        # {"name":"p_13","marker_id":"2"},
        # {"name":"p_14","marker_id":"115"},
        # {"name":"p_15","marker_id":"33"},
        # {"name":"p_16","marker_id":"44"},
        # {"name":"p_17","marker_id":"143"},
        {"name":"p_18","marker_id":"79"},
        {"name":"p_12","marker_id":"13"},
        # {"name":"p_19","marker_id":"118"},
    ]
    img = cv2.imread(IMAGE_FILE)
    robotPos = (0, 0)
    graph, dictAruco = deserialize(filename)
    graph = addArucos(graph, dictAruco, route)
    # graph = addPoints(img, graph, route)
    path = getResultPositions(graph, robotPos, route)
    return path

if __name__ == '__main__':
    if DEBUG:
        debugLocal()
    else:
        if LOCAL:
            InitLocal()
        else:
            solve()