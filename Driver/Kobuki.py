# -*- coding: utf-8 -*-
import binascii
import serial
import time
class Kobuki:
    def __init__(self,SerialPort):
        self.ser = serial.Serial(SerialPort, baudrate=115200, bytesize=8, parity=serial.PARITY_EVEN, stopbits=1, timeout=1)
        self.speed        = 0
        self.direction    = 0
        self.speedStr     = "0000"
        self.directionStr = "0000"
        self.head = "AA55060104"
        self.tail = "00"
        self.sendStr = None
        if self.ser.isOpen() is not True:
            print("Kobuki init failed.")
            exit()
        self.isOK = True 
    def checkSum(self,bytesteamStr):
        tempBites = 0
        tempBite  = 0
        for i in range(2,len(bytesteamStr)/2):
            tempBites ^= int(bytesteamStr[i*2:i*2+2],16)
        Bites = bin(tempBites)
        for i in range(2,len(Bites)):
            tempBite ^= int(Bites[i])
        return "00" if tempBite else "01"
    def setSpeed(self,speed):
        newspeed = None
        if speed > 32767:
            speed = 32767
        if speed < -32767:
            spee = -32767
        if speed >= 0:
            newspeed = speed
        else:
            newspeed = 0xffff+speed
        tempStr = str(hex(newspeed))[2:]
        #补0
        self.speedStr='{:0>4s}'.format(tempStr)
        #反序列化
        self.speedStr= self.speedStr[2:]+self.speedStr[:2]
    def setDirection(self,direction):
        newdirection = None
        direction = int(direction)
        if direction > 32767:
            direction = 32767
        if direction < -32767:
            direction = -32767
        if direction >= 0:
            newdirection = direction
        else:
            newdirection = 0xffff+direction
        tempStr = str(hex(newdirection))[2:]
        #补0
        self.directionStr='{:0>4s}'.format(tempStr)
        #反序列化
        self.directionStr= self.directionStr[2:]+self.directionStr[:2]
    def sendCommand(self):
        self.sendStr = self.head + self.speedStr + self.directionStr
        self.tail = self.checkSum(self.sendStr)
        self.sendStr = self.sendStr + self.tail
        sendBites = binascii.a2b_hex(self.sendStr)
        if self.ser.isOpen():
            self.ser.write(sendBites)
    def destorySerial(self):
        self.ser.close()
if __name__ == "__main__":
    print "Hello!"
    kobuki=Kobuki('COM5')
    direction = 400
    for i in range(4):
        kobuki.setSpeed(256)
        kobuki.setDirection(direction)
        kobuki.sendCommand()
        direction = direction*-1
        time.sleep(2)
    kobuki.destorySerial()

