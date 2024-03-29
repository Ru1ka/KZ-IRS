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
    rawImg1 = cam1.readRaw()
    binRawImg1 = np.zeros(list(rawImg1.shape[:2]) + [1], dtype=np.uint8)
    cv2.circle(binRawImg1, (347, 153), 6, (255, 255, 255), -1)
    img1 = getUndistortedImage(binRawImg1, const.cam1.matrix, const.cam1.distortion)
    k = 0.8035
    rightImg = cv2.resize(img1, (int(img1.shape[1] * k), int(img1.shape[0] * k)))
    rightImg = rightImg[:, 9:861]
    resImg = rotateImage(rightImg, 1.2)
    #resImg = cv2.rotate(resImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imshow('Image1', img1)
    cv2.imshow('Image2', binRawImg1)
    if cv2.waitKey(1) == 27: break