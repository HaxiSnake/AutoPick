import binascii
import serial
class Kobuki:
    def __init__(self,SerialPort):
        #self.ser = serial.Serial(port=SerialPort, baudrate=115200, bytesize=8, parity='E', stopbits=1, timeout=1)
        self.speed        = 0
        self.direction    = 0
        self.speedStr     = "0000"
        self.directionStr = "0000"
        self.head = "AA55060104"
        self.tail = "00"
        self.sendStr = None
    def checkSum(self,bytesteamStr):
        tempBites = 0
        tempBite  = 0
        for i in range(2,len(bytesteamStr)/2):
            tempBites ^= int(bytesteamStr[i*2:i*2+2],16)
        Bites = bin(tempBites)
        for i in range(2,len(Bites)):
            tempBite ^= int(Bites[i])
        return "00" if tempBite else "01"
    def setSpeed(self):
        pass
    def setDirection(self):
        pass
    def sendCommand(self):
        self.sendStr = self.head + self.speedStr + self.directionStr + self.tail
        pass
if __name__ == "__main__":
    print "Hello!"
    a = 1
    b = 4
    code = 'AA5506010480000000'
    print bin(a)
    print bin(b)
    print bin(a^b)
    testCode=binascii.a2b_hex(code)
    print testCode.encode('hex')
    kobuki = Kobuki("test")
    print kobuki.checkSum(code)
    
