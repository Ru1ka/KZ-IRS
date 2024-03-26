import numpy as np
import os
from copy import copy

class Camera:
    def __init__(self, matrix, distortion):
        self.matrix = np.array(matrix)
        self.distortion = np.array(distortion)

class Path:
    def __init__(self):
        self.images = os.path.join('solution', 'images')

class ConstPlenty:
    def __init__(self):
        self.cam1 = Camera(matrix=[[970.43302674, 0., 579.46567764],
                                   [0., 971.40059849, 441.66634744],
                                   [0., 0., 1.]],
                           distortion=[[-0.48618618, 0.36828116, 0.00429363, 0.00276907, -0.19681468]])
        self.cam2 = Camera(matrix=[[941.12297767, 0., 674.57711139],
                                   [0., 941.01682678, 415.87108226],
                                   [0., 0., 1.]],
                           distortion=[[-0.32409341, 0.21362774, 0.00232904, 0.00033955, -0.13665261]])
        self.path = Path()
