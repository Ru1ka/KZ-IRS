import cv2
import numpy as np
from server.vision import showImage

ALL_ARUCO_KEYS = [1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26, 27, 28, 29, 30, 31, 33, 35, 37,
                  39, 41, 42, 43, 44, 45, 46, 47, 49, 51, 53, 55, 57, 58, 59, 60, 61, 62, 63, 69, 70, 71, 76, 77, 78,
                  79, 85, 86, 87, 92, 93, 94, 95, 97, 98, 99, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114,
                  115, 117, 118, 119, 121, 122, 123, 125, 126, 127, 141, 142, 143, 157, 158, 159, 171, 173, 175, 187,
                  189, 191, 197, 199, 205, 206, 207, 213, 215, 221, 222, 223, 229, 231, 237, 239, 245, 247, 253, 255,
                  327, 335, 343, 351, 367, 383]


def getMaskBinArray(mask):
    N = 5
    cell_width = mask.shape[1] / N
    cell_height = mask.shape[0] / N
    cell_cx = cell_width / 2
    cell_cy = cell_height / 2

    binarray = []
    is_border = True

    for i in range(N):
        for j in range(N):
            y = round(i*cell_width + cell_cx)
            x = round(j*cell_height + cell_cy)
            color = round(np.average(mask[y-1:y+1, x-1:x+1]) / 255)
            if (i == 0 or i == N - 1) or (j == 0 or j == N - 1):
                is_border = is_border and (color == 0)
                continue
            binarray.append(color)
    if not is_border: return []
    
def bin2Dec(binarray):
    marker_id = 0
    n = len(binarray)
    for i in range(n - 1, -1, -1): marker_id += binarray[i] * 2**(n-i-1)
    if marker_id in ALL_ARUCO_KEYS: return marker_id
    else: return -1

def detectAruco(img, areaRange=10000, margin=10):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBinary = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 181, 13)
    showImage(imgBinary)
    contours, hi = cv2.findContours(imgBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < areaRange: continue
        if hi[0][i][2] == -1 or hi[0][i][3] == -1: continue
        c, dim, ang = cv2.minAreaRect(cnt)
        if max(dim) < 50: continue
        if min(dim) / max(dim) < 0.95: continue

        x, y, w, h = cv2.boundingRect(cnt)
        mask = imgBinary[y - margin:y + h + margin, x - margin:x + w + margin]
        # rotation
        M = cv2.getRotationMatrix2D((mask.shape[0] / 2, mask.shape[1] / 2), ang, 1)
        mask = cv2.warpAffine(mask, M, (mask.shape[0], mask.shape[1]))
        # clip
        clip = [round((mask.shape[0] - dim[1]) / 2), round((mask.shape[1] - dim[0]) / 2)]
        mask = mask[clip[0]:-clip[0], clip[1]:-clip[1]]

        binArray = getMaskBinArray(mask)
        if len(binArray) == 0: continue
        return bin2Dec(binArray)

res = detectAruco(cv2.imread('../thresholding/fullImage.png'))
print(res)