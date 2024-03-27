from server.vision import *

fullImg = cv2.imread('test.png')

markupPositions = getMarkupPositions(fullImg)
print(markupPositions)