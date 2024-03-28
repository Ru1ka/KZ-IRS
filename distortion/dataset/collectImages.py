import cv2
import os

def makeNewPhoto(img1):
    folder = 'arucos'
    fileNum1 = len(os.listdir(f'{folder}/'))
    #fileNum2 = len(os.listdir('cam2/'))
    cv2.imwrite(f'{folder}/{fileNum1}.png', img1)
    #cv2.imwrite(f'cam2/{fileNum2}.png', img2)

cam1 = cv2.VideoCapture(2)
cam2 = cv2.VideoCapture('http://student:nto2024@10.128.73.38/mjpg/video.mjpg')

while True:
    success1, img1 = cam1.read()
    if success1: cv2.imshow('Camera1', img1)
    match cv2.waitKey(1):
        case 27: break
        case 32: makeNewPhoto(img1)

cam1.release()
cv2.destroyAllWindows()