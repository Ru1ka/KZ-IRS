import cv2
import numpy as np

def ab(p1: tuple, p2: tuple, points: list):
    # Находим серединную точку между p1 и p2
    mid_point = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    # Находим уравнение прямой, проходящей через mid_point и перпендикулярной отрезку p1-p2
    if p2[0] - p1[0] == 0:
        perp_slope = 0  # Вертикальная линия, бесконечный угловой коэффициент
    else:
        perp_slope = -(p2[1] - p1[1]) / (p2[0] - p1[0])

    # Находим уравнение прямой вида y = mx + b, проходящей через mid_point и перпендикулярной к p1-p2
    b = mid_point[1] - perp_slope * mid_point[0]

    # Находим точку пересечения серединного перпендикуляра с отрезком p1-p2
    if perp_slope != 0:
        x_intercept = (b - p1[1] + perp_slope * p1[0]) / (perp_slope - 1 / perp_slope)
        y_intercept = perp_slope * x_intercept + b
    else:
        # Если перпендикуляр вертикален, то его уравнение x = b, где b - x координата середины
        x_intercept = b
        y_intercept = mid_point[1]

    # Проверяем, лежит ли точка пересечения на отрезке p1-p2
    if min(p1[0], p2[0]) <= x_intercept <= max(p1[0], p2[0]) and \
       min(p1[1], p2[1]) <= y_intercept <= max(p1[1], p2[1]):
        return [(x_intercept, y_intercept)]
    else:
        return []

# Пример использования
p1 = (32, 470)
p2 = (47, 490)
points = [(47, 429), (55, 451), (70, 473), (96, 493)]
intersections = ab(p1, p2, points)

print(intersections)
