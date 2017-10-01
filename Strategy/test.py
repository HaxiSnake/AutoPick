import os
import sys
import cv2
import time
os.chdir("G:\\AutoPickRobot\\AutoPick")
sys.path.append(os.getcwd())
from Driver.Kobuki import *
from Driver.Dobot   import *
from Tools.ParaSave import *
import glo

#global flags
#global flags

def systemInit():
    #glo.TheTrackCam  = cv2.VideoCapture(0)
    #glo.TheBallCam  = cv2.VideoCapture(1)
    glo.TheKobuki    = Kobuki(glo.KOBUKI_COM)
    #glo.TheDobot     = Dobot(glo.DOBOT_COM)
    glo.TheDirection = glo.PID(P=1.0,D=0.0) 
    trackParaGet     = Parameter(configFile=glo.TRACK_CONFIG)
    ballParaGet      = Parameter(configFile=glo.BALL_CONFIG)
    trackNameList,glo.TheTrackPara = trackParaGet.ReadConfig()
    ballNameList ,glo.TheBallPara  = ballParaGet.ReadConfig()
    if glo.TheTrackPara[7]%2 == 0:#special process for blur size
        glo.TheTrackPara[7] +=1
    print "track config file:",glo.TRACK_CONFIG
    print trackNameList
    print glo.TheTrackPara
    print "ball config file:",glo.BALL_CONFIG
    print ballNameList
    print glo.TheBallPara
def KobukiControl():
    glo.TheKobuki.setSpeed(0x80)
    glo.TheKobuki.setDirection(0)
    glo.TheKobuki.sendCommand()
def grub():
    pass


if __name__ == "__main__":
    systemInit()
    count = 0
    while True:
        KobukiControl()
        time.sleep(0.020)
        count += 1
        if count > 500:
            break
