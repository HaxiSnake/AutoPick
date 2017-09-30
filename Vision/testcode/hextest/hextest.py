import binascii
import serial
import time
code = 'AA550601048000000000'
code1 = '\xAA\x55\x06\x01\x04\x80\x00\x00'
print "code:",code
print "hex code:", binascii.a2b_hex(code)
print "code1:",code1

def setSpeed(speed):
    head = "AA55060104"
    tail = "000000"
    sendStr = head + speed + tail
    sendBites = binascii.a2b_hex(sendStr)
    return sendBites
setSpeed("8000")
