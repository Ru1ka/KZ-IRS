from server.vision import *

fullImg = cv2.imread('71.png')

res = detectAruco(fullImg, 3, show=True)
print(res)