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

def getCenterRobot(img):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    HSVMin = (18, 103, 34)
    HSVMax = (151, 216, 108)
    imgBinary = cv2.inRange(imgHSV, HSVMin, HSVMax)
    contours, _ = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    if not contours: return None
    centerRobot = findContourCenter(contours[0])
    return centerRobot

def getOrientationPoints(img):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    HSVMin1 = (24, 32, 68)
    HSVMax1 = (143, 219, 209)
    imgBinary1 = cv2.inRange(imgHSV, HSVMin1, HSVMax1)
    HSVMin2 = (126, 67, 61)
    HSVMax2 = (221, 143, 136)
    imgBinary2 = cv2.inRange(imgHSV, HSVMin2, HSVMax2)
    imgBinary = cv2.bitwise_or(imgBinary1, imgBinary2)
    contours, _ = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if not contours: return None
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    directionPoints = [findContourCenter(cnt) for cnt in contours]
    directionPoints = directionPoints[:4]
    return directionPoints

def detectRobot(img, show=False):
    centerRobot = getCenterRobot(img)
    if not centerRobot: return None, None
    orientationPoints = getOrientationPoints(img)
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