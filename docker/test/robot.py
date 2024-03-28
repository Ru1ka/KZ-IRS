import cv2
from docker.solution.vision import *
from docker.solution.algorithms import *

img = cv2.imread('../solution/images/Camera_0.png')
centerRobot, directionPoint = detectRobot(img, show=True)
print(unitVectorRobot)