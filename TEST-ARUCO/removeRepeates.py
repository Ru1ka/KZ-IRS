
ALL_ARUCO_KEYS = [1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26, 27, 28, 29, 30, 31, 33, 35, 37,
                  39, 41, 42, 43, 44, 45, 46, 47, 49, 51, 53, 55, 57, 58, 59, 60, 61, 62, 63, 69, 70, 71, 76, 77, 78,
                  79, 85, 86, 87, 92, 93, 94, 95, 97, 98, 99, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114,
                  115, 117, 118, 119, 121, 122, 123, 125, 126, 127, 141, 142, 143, 157, 158, 159, 171, 173, 175, 187,
                  189, 191, 197, 199, 205, 206, 207, 213, 215, 221, 222, 223, 229, 231, 237, 239, 245, 247, 253, 255,
                  327, 335, 343, 351, 367, 383]

arucoBinKeys = [bin(id)[2:].rjust(9, '0') for id in ALL_ARUCO_KEYS]
for binKey in arucoBinKeys:
    rBinKey = binKey
    for k in range(4):
        if rBinKey in arucoBinKeys: break
        rBinKey = rBinKey[6]+rBinKey[3]+rBinKey[0]+rBinKey[7]+rBinKey[4]+rBinKey[1]+rBinKey[8]+rBinKey[5]+rBinKey[2]
    else: continue
    if binKey == rBinKey: (int(binKey, 2), int(rBinKey, 2))