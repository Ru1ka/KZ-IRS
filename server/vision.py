import cv2
import numpy as np
import math
from functools import lru_cache

ALL_ARUCO_KEYS = [1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26, 27, 28, 29, 30, 31, 33, 35, 37,
                  39, 41, 42, 43, 44, 45, 46, 47, 49, 51, 53, 55, 57, 58, 59, 60, 61, 62, 63, 69, 70, 71, 76, 77, 78,
                  79, 85, 86, 87, 92, 93, 94, 95, 97, 98, 99, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114,
                  115, 117, 118, 119, 121, 122, 123, 125, 126, 127, 141, 142, 143, 157, 158, 159, 171, 173, 175, 187,
                  189, 191, 197, 199, 205, 206, 207, 213, 215, 221, 222, 223, 229, 231, 237, 239, 245, 247, 253, 255,
                  327, 335, 343, 351, 367, 383]

def getUndistortedImage(img, mtx, dist):
    h, w = img.shape[:2]
    newCameraMtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(img, mtx, dist, None, newCameraMtx)
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    return dst

def getStitcheredImage(img1, img2, mode=cv2.STITCHER_PANORAMA):
    # img1 = cv2.rotate(img1, cv2.ROTATE_90_CLOCKWISE)
    # img2 = cv2.rotate(img2, cv2.ROTATE_90_CLOCKWISE)
    stitcher = cv2.Stitcher().create(mode)
    status, pano = stitcher.stitch([img1, img2])
    pano = cv2.rotate(pano, cv2.ROTATE_90_CLOCKWISE)
    return pano

def rotateImage(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def rotateImageByPoint(img, rotationPoint, theta, width, height):
    shape = (img.shape[1], img.shape[0])
    matrix = cv2.getRotationMatrix2D(center=rotationPoint, angle=math.degrees(theta), scale=1)
    resultImg = cv2.warpAffine(src=img, M=matrix, dsize=shape)
    x = int(rotationPoint[0] - width / 2)
    y = int(rotationPoint[1] - height / 2)
    resultImg = resultImg[y:y + height, x:x + width]
    return resultImg

def detectRobot():
    "-> central point, [(x, y), ...]"
    pass

def getFullScene(leftImg, rightImg):
    k = 0.8035
    rightImg = cv2.resize(rightImg, (int(rightImg.shape[1] * k), int(rightImg.shape[0] * k)))
    offsetCenter = -55
    leftImg = leftImg[68 + offsetCenter:]
    rightImg = rightImg[:-150 + offsetCenter, 9:861]
    resImg = np.concatenate((rightImg, leftImg), axis=0)
    resImg = rotateImage(resImg, 1.2)
    resImg = resImg[37:-37, 208:-93]
    resImg = cv2.rotate(resImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return resImg

def findContourCenter(cnt):
    cx, cy = None, None
    moment = cv2.moments(cnt)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
    return (cx, cy)

def adaptiveThresholdImage(imgGray, blockSize, C):
    imgBinary = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize, C)
    kernel = np.ones((9, 9), np.uint8)
    imgBinary = cv2.morphologyEx(imgBinary, cv2.MORPH_CLOSE, kernel)
    return imgBinary

def getRoadMask(img, show=False):
    #HSVMin = (93, 0, 50)
    #HSVMax = (134, 120, 164)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    imgBinary1 = cv2.inRange(imgHSV[:imgHSV.shape[0]*2//3], (98, 32, 74), (130, 107, 163))
    imgBinary2 = cv2.inRange(imgHSV[imgHSV.shape[0]*2//3:], (83, 25, 56), (136, 123, 113))
    imgBinary = np.concatenate((imgBinary1, imgBinary2), axis=0)
    if show: showImage(imgBinary)
    kernel = np.ones((9, 9), np.uint8)
    imgBinary = cv2.morphologyEx(imgBinary, cv2.MORPH_OPEN, kernel)
    if show: showImage(imgBinary)
    kernel = np.ones((17, 17), np.uint8)
    imgBinary = cv2.morphologyEx(imgBinary, cv2.MORPH_CLOSE, kernel)
    if show: showImage(imgBinary)
    kernel = np.ones((9, 9), np.uint8)
    imgBinary = cv2.erode(imgBinary, kernel, iterations=4)
    if show: showImage(imgBinary)
    return imgBinary

def getGreenMask(img, show=False):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    imgBinary = cv2.inRange(imgHSV, (68, 53, 170), (90, 89, 255))
    if show: showImage(imgBinary)
    kernel = np.ones((12, 12), np.uint8)
    imgBinary = cv2.morphologyEx(imgBinary, cv2.MORPH_CLOSE, kernel)
    if show: showImage(imgBinary)
    kernel = np.ones((4, 9), np.uint8)
    imgBinary = cv2.dilate(imgBinary, kernel, iterations=4)
    if show: showImage(imgBinary)
    return imgBinary

def markupThresholdImage(img, show=False):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, imgBinary1 = cv2.threshold(imgGray[:100], 130, 255, cv2.THRESH_BINARY)
    _, imgBinary2 = cv2.threshold(imgGray[100:200], 140, 255, cv2.THRESH_BINARY)
    _, imgBinary3 = cv2.threshold(imgGray[200:300], 130, 255, cv2.THRESH_BINARY)
    _, imgBinary4 = cv2.threshold(imgGray[300:400], 115, 255, cv2.THRESH_BINARY)
    _, imgBinary5 = cv2.threshold(imgGray[400:], 80, 255, cv2.THRESH_BINARY)
    if show:
        showImage(imgBinary1)
        showImage(imgBinary2)
        showImage(imgBinary3)
        showImage(imgBinary4)
        showImage(imgBinary5)
    imgBinary = np.concatenate((imgBinary1, imgBinary2, imgBinary3, imgBinary4, imgBinary5), axis=0)
    if show: showImage(imgBinary)
    kernel = np.ones((2, 2), np.uint8)
    imgBinary = cv2.dilate(imgBinary, kernel, iterations=2)
    if show: showImage(imgBinary)
    imgRoadMask = getRoadMask(img, show=show)
    imgGreenMask = getGreenMask(img, show=show)
    imgBinary = cv2.bitwise_and(imgBinary, imgBinary, mask=imgRoadMask)
    if show: showImage(imgBinary)
    resultImgBinary = cv2.bitwise_and(imgBinary, imgBinary, mask=cv2.bitwise_not(imgGreenMask))
    if show: showImage(resultImgBinary)
    return resultImgBinary

def getMarkupPositions(img, squareRange=(10, 115), adaptive=False, custom=True, show=False):
    if adaptive: imgBinary = adaptiveThresholdImage(img, 151, 1)
    elif custom: imgBinary = markupThresholdImage(img, show=show)
    else:  _, imgBinary = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)
    if show: showImage(imgBinary)
    contours, _ = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    markupContours = [cnt for cnt in contours if squareRange[0] < cv2.contourArea(cnt) < squareRange[1]]
    markupArray = [findContourCenter(cnt) for cnt in markupContours]
    if show:
        imgContours = img.copy()
        cv2.drawContours(imgContours, markupContours, -1, (255, 0, 0), 1)
        [cv2.putText(imgContours, str(i), (center[0] - 4, center[1] - 4), cv2.FONT_HERSHEY_COMPLEX, 0.3, (100, 0, 255),0)
         for i, center in enumerate(markupArray)]
        showImage(imgContours)
    return markupArray

def arucoThresholdImage(img, show=False):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, imgBinary1 = cv2.threshold(imgGray[:100], 217, 255, cv2.THRESH_BINARY)
    _, imgBinary2 = cv2.threshold(imgGray[100:200], 223, 255, cv2.THRESH_BINARY)
    _, imgBinary3 = cv2.threshold(imgGray[200:300], 210, 255, cv2.THRESH_BINARY)
    _, imgBinary4 = cv2.threshold(imgGray[300:400], 200, 255, cv2.THRESH_BINARY)
    _, imgBinary5 = cv2.threshold(imgGray[400:], 175, 255, cv2.THRESH_BINARY)
    if show:
        showImage(imgBinary1)
        showImage(imgBinary2)
        showImage(imgBinary3)
        showImage(imgBinary4)
        showImage(imgBinary5)
    imgBinary = np.concatenate((imgBinary1, imgBinary2, imgBinary3, imgBinary4, imgBinary5), axis=0)
    if show: showImage(imgBinary)
    return imgBinary

@lru_cache(None)
def getDistanceBetweenPoints(point1, point2):
    return math.hypot(abs(point1[0] - point2[0]), abs(point1[1] - point2[1]))


def minDistanceBetweenLines(line1, line2):
    return min([getDistanceBetweenPoints(point1, point2) for point1 in line1 for point2 in line2])

def getPointOnSameLineOnSquare(vertexes, minDist, maxDist):
    limitDist = minDist + (minDist + maxDist) // 2
    for i, pos1 in enumerate(vertexes[:-1]):
        for j, pos2 in enumerate(vertexes[i + 1:]):
            if math.hypot(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1])) < limitDist:
                return pos1, pos2

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

def detectAruco(img, size=3, areaRange=(800, 1300), coefApprox=0.03, show=False):
    imgBinary = arucoThresholdImage(img, show=show)
    contours, _ = cv2.findContours(imgBinary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # [print(i, cv2.contourArea(cnt)) for i, cnt in enumerate(sorted(contours, key=cv2.contourArea, reverse=True))]

    arucoContours = [cnt for cnt in contours if areaRange[0] < cv2.contourArea(cnt) < areaRange[1]]
    if not arucoContours: return {}
    dictAruco = {}

    if show: imgContours = img.copy()
    for cnt in arucoContours:
        epsilon = coefApprox * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        contourVertexes = [(pos[0][0], pos[0][1]) for pos in approx]
        centerContour = (round(sum([pos[0] for pos in contourVertexes]) / 4),
                         round(sum([pos[1] for pos in contourVertexes]) / 4))
        allDistBetweenPoints = [round(math.hypot(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1])))
                                for i, pos1 in enumerate(contourVertexes[:-1])
                                for j, pos2 in enumerate(contourVertexes[i + 1:])]
        widthContour, heightContour = sorted(allDistBetweenPoints)[:2]
        pointContour1, pointContour2 = getPointOnSameLineOnSquare(contourVertexes, min(allDistBetweenPoints), max(allDistBetweenPoints))
        angleBetweenContourAndAbscissa = getAngleBetweenLines((pointContour2, pointContour1), (pointContour1, (10, pointContour1[1])))
        imgAruco = rotateImageByPoint(img, centerContour, angleBetweenContourAndAbscissa, widthContour, heightContour)
        imgAruco = cv2.cvtColor(imgAruco, cv2.COLOR_BGR2GRAY)
        shapeImgAruco = imgAruco.shape[:2]
        sizeOneCell = (shapeImgAruco[1] / (size + 2), shapeImgAruco[0] / (size + 2))
        arucoArray = np.zeros((size, size), dtype=np.uint8)
        for i in range(size):
            for j in range(size):
                basePosX, basePosY = sizeOneCell[0] * 1.5, sizeOneCell[1] * 1.5
                posX, posY = round(basePosX + sizeOneCell[0] * j), round(basePosY + sizeOneCell[1] * i)
                valueCell = imgAruco[posY, posX]
                arucoArray[i, j] = valueCell > 100
                if show: cv2.circle(imgAruco, (posX, posY), 1, (100, 100, 100), 2)
        if show: showImage(imgAruco)
        for i in range(4):
            cpArucoArray = arucoArray.copy()
            cpArucoArray.resize(size ** 2)
            numberAruco = int(''.join(list(map(str, cpArucoArray))), 2)
            if numberAruco in ALL_ARUCO_KEYS: break
            arucoArray = np.rot90(arucoArray)
        else: continue
        dictAruco[f'p_{numberAruco}'] = (centerContour, angleBetweenContourAndAbscissa, contourVertexes)
        if show: cv2.putText(imgContours, str(numberAruco), contourVertexes[1], cv2.FONT_HERSHEY_COMPLEX, 1, (100, 0, 255), 2)
    if show:
        cv2.destroyWindow('Aruco')
        cv2.drawContours(imgContours, arucoContours, -1, (0, 0, 255), 1)
        showImage(imgContours)
    return dictAruco


def transformCords(x, y, cam):
    # x, y for full img
    pass

def showImage(img):
    while cv2.waitKey(1) != 27: cv2.imshow('Image', img)