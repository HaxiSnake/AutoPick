import binascii
import serial
class Kobuki:
    def __init__(self,SerialPort):
        self.ser = serial.Serial(SerialPort,baudrate=115200,,bytesize=8,parity='E',stopbits=1,timeout=1)
        self.speed     = 0
        self.direction = 0
        self.speedStr  = "0000"
