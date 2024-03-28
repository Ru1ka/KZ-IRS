from funcs import getNearestPoints
import numpy as np
import cv2

def rotateImage(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

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

def binCenRobImage(img):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    HSVMin = (41, 99, 38)
    HSVMax = (157, 214, 84)  # - 170
    imgBinary1 = cv2.inRange(imgHSV[:170], HSVMin, HSVMax)

    HSVMin = (52, 89, 32)
    HSVMax = (147, 179, 79)  # 170 - 310
    imgBinary2 = cv2.inRange(imgHSV[170:310], HSVMin, HSVMax)

    HSVMin = (44, 107, 31)
    HSVMax = (151, 200, 100)  # 310 - 380
    imgBinary3 = cv2.inRange(imgHSV[310:380], HSVMin, HSVMax)

    HSVMin = (96, 156, 17)
    HSVMax = (145, 255, 38)  # 380 -
    imgBinary4 = cv2.inRange(imgHSV[380:], HSVMin, HSVMax)

    imgBinary = np.concatenate((imgBinary1, imgBinary2, imgBinary3, imgBinary4), axis=0)
    return imgBinary

def binOriPonImage(img, cntRobBin):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    HSVMin = (33, 38, 62)
    HSVMax = (202, 255, 228)  # - 170
    imgBinary1 = cv2.inRange(imgHSV[:170], HSVMin, HSVMax)

    HSVMin = (16, 31, 62)
    HSVMax = (228, 220, 173)  # 170 - 310
    imgBinary2 = cv2.inRange(imgHSV[170:310], HSVMin, HSVMax)

    HSVMin = (39, 34, 52)
    HSVMax = (185, 138, 110)  # 310 - 380
    imgBinary3 = cv2.inRange(imgHSV[310:380], HSVMin, HSVMax)

    HSVMin = (27, 52, 32)
    HSVMax = (190, 164, 94)  # 380 -
    imgBinary4 = cv2.inRange(imgHSV[380:], HSVMin, HSVMax)

    imgBinary = np.concatenate((imgBinary1, imgBinary2, imgBinary3, imgBinary4), axis=0)
    #imgBinary = cv2.bitwise_or(imgBinary, imgBinary, cv2.bitwise_not(cntRobBin, cntRobBin))
    return imgBinary

def getCenterRobot(img, show=False):
    imgBinary = binCenRobImage(img)
    if show:
        cv2.imshow('Bin', imgBinary)
        cv2.waitKey(1)
    contours, _ = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    if not contours: return None
    centerRobot = findContourCenter(contours[0])
    return imgBinary, centerRobot

def getOrientationPoints(img, cntRobBin, show=False):
    imgBinary = binOriPonImage(img, cntRobBin)

    if show:
        cv2.imshow('Bin2', imgBinary)
        cv2.waitKey(1)
    contours, _ = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if not contours: return None
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    directionPoints = [findContourCenter(cnt) for cnt in contours]
    directionPoints = directionPoints[:4]
    return directionPoints

def detectRobot(img, show=False):
    cntRobBin, centerRobot = getCenterRobot(img, show)
    if not centerRobot: return None, None
    orientationPoints = getOrientationPoints(img, cntRobBin, show)
    if not orientationPoints: return centerRobot, None
    nearestPoints = getNearestPoints(orientationPoints)
    directionPoint = ((nearestPoints[0][0] + nearestPoints[1][0]) // 2,
                      (nearestPoints[0][1] + nearestPoints[1][1]) // 2)
    if show:
        imgShow = img.copy()
        cv2.circle(imgShow, centerRobot, 3, (0, 0, 255), -1)
        [cv2.circle(imgShow, pnt, 3, (255, 255, 255), -1) for pnt in orientationPoints]
        showImage(imgShow)
    return centerRobot, directionPoint

def showImage(img, winName='Image'):
    while cv2.waitKey(1) != 27: cv2.imshow(winName, img)