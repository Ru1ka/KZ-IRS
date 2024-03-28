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
import show
from settings import settings


def debugLocal():
    DEBUG = settings().DEBUG

    img = cv2.imread("images/86.png")

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