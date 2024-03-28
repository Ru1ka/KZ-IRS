import cv2
from cv2 import aruco
import numpy as np
# from ..server.vision import showImage
from math import hypot, atan2, degrees, radians
import math

ALL_ARUCO_KEYS = [1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26, 27, 28, 29, 30, 31, 33, 35, 37,
                  39, 41, 42, 43, 44, 45, 46, 47, 49, 51, 53, 55, 57, 58, 59, 60, 61, 62, 63, 69, 70, 71, 76, 77, 78,
                  79, 85, 86, 87, 92, 93, 94, 95, 97, 98, 99, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114,
                  115, 117, 118, 119, 121, 122, 123, 125, 126, 127, 141, 142, 143, 157, 158, 159, 171, 173, 175, 187,
                  189, 191, 197, 199, 205, 206, 207, 213, 215, 221, 222, 223, 229, 231, 237, 239, 245, 247, 253, 255,
                  327, 335, 343, 351, 367, 383]

def showImage(img):
    while cv2.waitKey(1) != 27: cv2.imshow('Image', img)

class ArucoDetector:
    def __init__(self, size, whitelist):
        self.size = size
        self.whitelist = whitelist
        self.dictionary = aruco.Dictionary(np.empty(shape=(384, 2, 4), dtype=np.uint8), size)
        self.fillDictionary()
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)

    def getBits(self, id):
        binId = bin(id)[2:].rjust(self.size**2, '0')
        bits = np.array(list(binId), dtype=np.uint8).reshape(-1, self.size)
        return bits

    def fillDictionary(self):
        for id in self.whitelist:
            bits = self.getBits(id)
            self.dictionary.bytesList[id] = aruco.Dictionary.getByteListFromBits(bits)

    def detectMarkers(self, imgGray):
        rawMarkerCorners, rawMarkerIds, rejectedCandidates = self.detector.detectMarkers(imgGray)
        markerCorners, markerIds = [], []
        if rawMarkerIds is None: return [], []
        for i, id in enumerate(rawMarkerIds):
            if id in self.whitelist:
                markerCorners.append(rawMarkerCorners[i])
                markerIds.append(rawMarkerIds[i])
        return markerCorners, markerIds

'''
# define an empty custom dictionary for markers of size 4
#Затем нам нужно создать трехмерный массив в объекте bytesList внутри словаря aruco:
arucoDict = aruco.Dictionary(np.empty(shape=(3, 2, 4), dtype=np.uint8), 3)
# add empty bytesList array to fill with 3 markers later

# Теперь мы можем создавать наши маркеры в виде массивов с битами, которые представляют черные (0) или белые (1) части маркера:
# add new marker(s)
mybits = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=np.uint8)

# Наконец, мы можем добавить байты маркера в объект bytesList:
arucoDict.bytesList[2] = aruco.Dictionary.getByteListFromBits(mybits)'''



def getDistanceBetweenPoints(point1, point2):
    return hypot(abs(point1[0] - point2[0]), abs(point1[1] - point2[1]))

def rotateMatrix(matrix):
    # Получаем количество строк и столбцов в матрице
    num_rows = len(matrix)
    num_cols = len(matrix[0])

    # Создаем новую матрицу, в которую будем записывать повернутую матрицу
    rotated_matrix = [[0] * num_rows for _ in range(num_cols)]

    # Перебираем элементы исходной матрицы и записываем их в новую матрицу, повернутую на 90 градусов
    for i in range(num_rows):
        for j in range(num_cols):
            rotated_matrix[j][num_rows - 1 - i] = matrix[i][j]

    return rotated_matrix


def angleBetweenPoints(point1, point2):
    """Вычисляет угол между двумя точками и горизонтальной осью."""
    return atan2(point2[1] - point1[1], point2[0] - point1[0])

def getAngleBetweenLines(line1, line2):
    startPosLine1, endPosLine1 = line1
    startPosLine2, endPosLine2 = line2
    vector1 = [(endPosLine1[axis] - startPosLine1[axis]) for axis in range(2)]
    vector2 = [(endPosLine2[axis] - startPosLine2[axis]) for axis in range(2)]
    scalarProduct = np.dot(vector1, vector2)
    lengthVector1 = math.hypot(abs(vector1[0]), abs(vector1[1]))
    lengthVector2 = math.hypot(abs(vector2[0]), abs(vector2[1]))
    lengthsProduct = lengthVector1 * lengthVector2
    if lengthsProduct == 0: return math.pi
    angle = math.acos(scalarProduct / lengthsProduct)
    return angle

def findArucoMarkers(img, threshold, size=3, show=False):
    detector = ArucoDetector(size, ALL_ARUCO_KEYS)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    markerCorners, markerIds = detector.detectMarkers(gray)
    if show:
        imgShow = img.copy()
        aruco.drawDetectedMarkers(imgShow, markerCorners)
        aruco.drawDetectedMarkers(imgShow, markerCorners)
        for cnr, id in zip(markerCorners, markerIds):
            pos = list(map(int, list(cnr[0][0])))
            cv2.putText(imgShow, str(id), pos, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('Image', imgShow)
    result = {}
    for cnr, id in zip(markerCorners, markerIds):
        corners = np.array(list(map(np.array, cnr[0])))
        imgWrapped = fourPointTransform(img, corners)
        imgWGray = cv2.cvtColor(imgWrapped, cv2.COLOR_BGR2GRAY)
        matrix = getMatrixFromAruco(imgWGray, threshold, size)
        center_x = sum([i[0] for i in corners]) / 4
        center_y = sum([i[1] for i in corners]) / 4
        a, b = list(sorted(corners, key=lambda x: x[1]))[:2]
        if b[0] < a[0]:
            c = [a[0] + 5, a[1]]
            angle = degrees(getAngleBetweenLines([b, a], [a, c]))
        else:
            c = [a[0] - 5, a[1]]
            angle = -degrees(getAngleBetweenLines([b, a], [a, c]))
            
        corners.sort()
        n = 0
        while True:
            markerId = 0
            for i in range(9):
                x = i % 3
                y = i // 3
                markerId += matrix[y][x] * 2**(8 - i)
            
            if markerId in ALL_ARUCO_KEYS:
                angle += n * 90
                if angle < 0:
                    angle += 360
                print(angle)
                result[f"p_{id}"] = (center_x, center_y, radians(angle))
                break
            else:
                n += 1
                matrix = rotateMatrix(matrix)
            
            if n >= 4:
                break        
        # print(angle)
        # print(markerId)
        # print("___")

        if show:
            cv2.imshow('Aruco', imgWrapped)
    if show:
        cv2.waitKey(1)
    
    return result


def angleToPoint(centralPoint, angle, d=1):
    angle = radians(degrees(angle) + 180)
    x, y = centralPoint
    nx = x + d * math.cos(angle)
    ny = y + d * math.sin(angle)
    return nx, ny


def getMatrixFromAruco(imgGray, threshold, sizeAruco, show=False):
    height, width = imgGray.shape[:2]
    stepH, stepW = height // (sizeAruco+1), width // (sizeAruco+1)
    matrix = [[0] * sizeAruco for _ in range(sizeAruco)]
    for i in range(1, sizeAruco+1):
        for j in range(1, sizeAruco+1):
            y = stepH * i
            x = stepW * j
            matrix[i-1][j-1] = int(imgGray[y][x] > threshold)
            if show:
                cv2.circle(imgGray, (x, y), 5, (255, 255, 255), -1)
                cv2.circle(imgGray, (x, y), 3, (0, 0, 0), -1)
    return matrix


def orderPoints(points):
    rect = np.zeros((4, 2), dtype='float32')
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]
    return rect

def fourPointTransform(image, corners):
    rect = orderPoints(corners)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype='float32')
    M = cv2.getPerspectiveTransform(rect, dst)
    imgWraped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return imgWraped

cap = cv2.VideoCapture(0)
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    
    success, img = cap.read()
    img = cv2.flip(img, 1)
    findArucoMarkers(img, 150, show=True)