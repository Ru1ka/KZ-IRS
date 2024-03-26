import cv2
import time
import socket
from nto.final import Task

## Здесь должно работать ваше решение
def solve():
    '''## Пример отправки сообщения на робота по протоколу udp
    UDP_IP = '192.168.2.137'
    UDP_PORT = 5005
    MESSAGE = b'Hello, World!'

    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))'''

    ## Запуск задания и таймера (внутри задания)
    task = Task()
    task.start()
    print(task.getTask())

    sceneImg = task.getTaskScene()
    cv2.imwrite('images/Camera1.png', sceneImg[0])
    cv2.imwrite('images/Camera2.png', sceneImg[1])
    task.stop()

if __name__ == '__main__':
    solve()