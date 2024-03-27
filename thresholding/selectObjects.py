from server.vision import *

fullImg = cv2.imread('fullImage.png')

markupPositions = getMarkupPositions(fullImg, show=True)
print(markupPositions)