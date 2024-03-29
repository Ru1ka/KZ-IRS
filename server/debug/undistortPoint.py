from camera import Camera, getUndistortedImage
from server.solution.const import ConstPlenty
import cv2
import numpy as np

def rotateImage(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

const = ConstPlenty()

cam1 = Camera(0, const.cam1.matrix, const.cam1.distortion)
cam2 = Camera(1, const.cam2.matrix, const.cam2.distortion)

while True:
    rawImgLeft = cam1.readRaw()
    rawImgRight = cam2.readRaw()
    rawBinLeft = np.zeros(rawImgLeft.shape, dtype=np.uint8)
    rawBinRight = np.zeros(rawImgRight.shape, dtype=np.uint8)

    cv2.circle(rawBinLeft, (347, 153), 6, (255, 255, 255), -1)

    binLeft = getUndistortedImage(rawBinLeft, const.cam1.matrix, const.cam1.distortion)
    binRight = getUndistortedImage(rawBinRight, const.cam2.matrix, const.cam2.distortion)

    k = 0.8035
    binRight = cv2.resize(binRight, (int(binRight.shape[1] * k), int(binRight.shape[0] * k)))
    offsetCenter = -55
    binLeft = binLeft[68 + offsetCenter:]
    binRight = binRight[:-150 + offsetCenter, 9:861]

    resImg = np.concatenate((binRight, binLeft), axis=0)
    resImg = rotateImage(resImg, 1.2)
    resImg = resImg[37:-37, 208:-93]
    resImg = cv2.rotate(resImg, cv2.ROTATE_90_COUNTERCLOCKWISE)

    cv2.imshow('Image', resImg)
    if cv2.waitKey(1) == 27: break