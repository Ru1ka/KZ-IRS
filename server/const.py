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
        self.cam2 = Camera(matrix=[[951.47517581, 0., 687.49009612],
                                   [0., 951.62381268, 412.51000724],
                                   [0., 0., 1.]],
                           distortion=[[-0.3343925, 0.23063358, 0.00185695, -0.00096984, -0.15177394]])
        self.path = Path()
