def rotate_matrix_clockwise(matrix):
    # Получаем количество строк и столбцов в матрице
    num_rows = len(matrix)
    num_cols = len(matrix[0])

    # Создаем новую матрицу, в которую будем записывать повернутую матрицу
    rotated_matrix = [[0] * num_rows for _ in range(num_cols)]

    # Перебираем элементы исходной матрицы и записываем их в новую матрицу, повернутую на 90 градусов
    for i in range(num_rows):
        for j in range(num_cols):
            rotated_matrix[j][num_rows - 1 - i] = matrix[i][j]

    return rotated_matrix

# Пример использования
original_matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

rotated_matrix = rotate_matrix_clockwise(original_matrix)
for row in rotated_matrix:
    print(row)
