import serial
import time
class Dobot:
    def __init__(self,SerialPort):
        self.ser = serial.Serial(SerialPort, baudrate=115200,timeout=1)
        if self.ser.isOpen() is not True:
            print("Dobot init failed.")
            exit()
        #self.ser.read(63)
        self.dobotInit()
        self.isOK = True 
    def waitDobot(self):
        while(True):
            buff = self.ser.read(63)
            #print buff
            if ("ok" in buff):
                break
            time.sleep(0.01)
    def dobotInit(self):
        print "dobot Init start"
        self.ser.write("G28 X0 Y0 Z0\n")
        self.waitDobot()
        self.ser.write("G91\n")
        self.waitDobot()
        print "dobot Init done!"
    def pickHigh(self):
        print "dobot pick high start"
        self.ser.write("G1 X60 F9999\n")
        self.ser.write("G1 Z50 F9999\n")
        self.ser.write("G1 X60 F9999\n")
        self.ser.write("G1 Z-120 F9999\n")
        self.ser.write("G28 Z0\n")
        self.waitDobot()
        print "dobot pick high done!"
    def pickLow(self):
        print "dobot pick low start"
        self.ser.write("G1 X120 F9999\n")
        self.ser.write("G1 Z-280 F9999\n")
        self.ser.write("G28 Z0\n")
        self.waitDobot()
        print "dobot pick low done!"
if __name__ == "__main__":
    print "Hello!I am Dobot!"
    dobot=Dobot('/dev/ttyUSB1')
    dobot.pickHigh()
    dobot.pickHigh()
    dobot.pickLow()
    dobot.pickLow()

