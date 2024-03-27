import cv2
import numpy as np


def perpendicular_intersection(m1, b1, m2, b2):
    if m1 == 0:  # Проверка деления на ноль
        x = -b1 / m1
        y = m2 * x + b2
    elif m2 == 0:  # Проверка деления на ноль
        x = -b2 / m2
        y = m1 * x + b1
    else:
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1
    return x, y


def intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    print(p1, p2)
    print(p3, p4)
    scalar = (x2 - x1) * (x4 - x3) + (y2 - y1) * (y4 - y3)
    print(scalar)
    # Если прямая 1 вертикальная (x2 = x1)
    if x2 == x1:
        # Угловой коэффициент прямой 2
        m2 = (y4 - y3) / (x4 - x3)
        # x-координата точки пересечения будет равна x1
        x = x1
        # Находим y-координату точки пересечения
        y = m2 * (x - x3) + y3
        return x, y
    
    # Если прямая 2 вертикальная (x4 = x3)
    if x4 == x3:
        # Угловой коэффициент прямой 1
        m1 = (y2 - y1) / (x2 - x1)
        # x-координата точки пересечения будет равна x3
        x = x3
        # Находим y-координату точки пересечения
        y = m1 * (x - x1) + y1
        return x, y
    
    # Угловые коэффициенты прямых
    m1 = (y2 - y1) / (x2 - x1)
    m2 = (y4 - y3) / (x4 - x3)
    
    # Если прямые параллельны, то точки пересечения нет
    if m1 == m2:
        return None

    
    # Находим координаты точки пересечения
    x = ((x3 * y4 - y3 * x4) * (x1 - x2) - (x1 * y2 - y1 * x2) * (x3 - x4)) / ((y1 - y2) * (x3 - x4) - (y3 - y4) * (x1 - x2))
    y = ((y1 - y2) * (x * (x1 - x2) - x1 * y2 + y1 * x2) - (y3 - y4) * (x * (x3 - x4) - x3 * y4 + y3 * x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    
    return x, y


def perpendicular_line(point_on_line, slope, distance=1):
    def perpendicular_slope(slope):
        if slope == 0:
            return float('inf')  # Перпендикуляр к горизонтальной прямой - вертикальная прямая
        elif slope == float('inf'):
            return 0  # Перпендикуляр к вертикальной прямой - горизонтальная прямая
        else:
            return -1 / slope

    x1, y1 = point_on_line
    
    # Находим угловой коэффициент перпендикулярной прямой
    perp_slope = perpendicular_slope(slope)
    
    # Находим координаты двух точек на перпендикулярной прямой
    x2_up = x1 + distance
    y2_up = y1 + distance * perp_slope
    x2_down = x1 - distance
    y2_down = y1 - distance * perp_slope
    
    return (x2_up, y2_up), (x2_down, y2_down)

def slope_between_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    # Проверяем, чтобы не делить на ноль
    if x2 - x1 == 0:
        return float('inf')  # Возвращаем бесконечность, если прямая вертикальная
    
    return (y2 - y1) / (x2 - x1)


# Пример использования
p1 = (36, 463)
p2 = (48, 490)
points = [(47, 429), (55, 451), (70, 473), (96, 493)]
lp1 = points[1]
lp2 = points[2]
# Создаем пустое изображение
img = np.zeros((512, 512, 3), dtype=np.uint8)

# Рисуем ломаную
for i in range(len(points) - 1):
    cv2.line(img, points[i], points[i+1], (255, 255, 255), 2)

# Рисуем линию p1-p2
cv2.line(img, p1, p2, (0, 0, 255), 2)


def findIntersectionAruco(p1, p2, lp1, lp2):
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    p1, p2 = perpendicular_line(mid, slope_between_points(p1, p2), 50)
    p1, p2 = list(map(round, p1)), list(map(round, p2))
    cv2.line(img, p1, p2, (255, 255, 0), 2)
    cv2.line(img, lp1, lp2, (0, 255, 0), 2)
    return intersection(p1, p2, lp1, lp2)


point = findIntersectionAruco(p1, p2, lp1, lp2)
print(point)


# Отображаем точки пересечения на изображении
cv2.circle(img, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

# Отображаем изображение
cv2.imshow('Intersections', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
