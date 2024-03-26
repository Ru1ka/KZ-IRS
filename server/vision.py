import cv2


def getImages():
    cam1 = cv2.VideoCapture('http://student:nto2024@10.128.73.31/mjpg/video.mjpg')
    cam2 = cv2.VideoCapture('http://student:nto2024@10.128.73.38/mjpg/video.mjpg')
    ...



# МНЕ НУЖНО:
def detectAruco(areaRange=[2000, 4000], coefApprox=0.03, show=False) -> dict:
    # -> {f"aruco_{id}": tuple(x, y)}
    pass

def getMarkupPositions(squareRange=[0, 120], show=False) -> list:
    # -> [центр линии разметки, ...]
    pass