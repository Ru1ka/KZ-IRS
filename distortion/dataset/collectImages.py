import cv2
import os

def makeNewPhoto(img, path="cam/"):
    fileNum1 = len(os.listdir('cam/'))
    #fileNum2 = len(os.listdir('cam2/'))
    cv2.imwrite(f'{path}{fileNum1}.jpg', img)
    #cv2.imwrite(f'cam2/{fileNum2}.png', img2)
    print(f"saved in {path}{fileNum1}.jpg")

# cam1 = cv2.VideoCapture('http://student:nto2024@10.128.73.31/mjpg/video.mjpg')
# cam2 = cv2.VideoCapture('http://student:nto2024@10.128.73.38/mjpg/video.mjpg')
cam = cv2.VideoCapture(0)

while True:
    # success1, img1 = cam1.read()
    # success2, img2 = cam2.read()
    success, img = cam.read()
    # if success1: cv2.imshow('Camera1', img1)
    # if success2: cv2.imshow('Camera2', img2)
    if success: cv2.imshow("CameraFirst", img)
    match cv2.waitKey(1):
        case 27: break
        case 32: makeNewPhoto(img)


cam.release()
# cam1.release()
# cam2.release()
cv2.destroyAllWindows()