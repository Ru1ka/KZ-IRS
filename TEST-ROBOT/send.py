import socket

class Robot:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.sock.sendto(message, (self.ip, self.port))

    def sendPath(self, path):
        strPath = ';'.join([','.join(list(map(str, pos))) for pos in path])
        self.send(strPath.encode('utf-8'))

robot = Robot('10.128.73.116', 5005)

# s = '4234,23432,0.324;234,324,0.123;4123,52,1.342;'.encode('utf-8')
s = '9,9,0;4,9,0;4,4,0;'.encode('utf-8')
robot.send(s)