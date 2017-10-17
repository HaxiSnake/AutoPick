import os
import sys
import cv2
import time
import threading
import signal
#workdir = "G:\\AutoPickRobot\\AutoPick"
workdir = "/home/pi/SpeedUp"
#workdir = "E:\\WORKSPACE\\2_Haobbys\\AutoPickRobot\\AutoPick"
os.chdir(workdir)
sys.path.append(os.getcwd())
from Driver.Kobuki import *
from Driver.Dobot import *
from Tools.ParaSave import *
from Vision.FindObject import *
import glo


def systemInit():
    #glo.MODE_SELECT select the workmodel
    #1: TrackTest 2: BallTest 3: TogetherRun
    if glo.MODE_SELECT == 1:
        glo.TheKobuki = Kobuki(glo.KOBUKI_COM)
        #glo.TheDobot      = Dobot(glo.DOBOT_COM)
        glo.TheDirection = glo.PID(P=glo.TRACK_P, D=glo.TRACK_D)
        glo.TheThreadLock = threading.Lock()
        glo.TheTrackThread = TrackThread(1, "Track", 1)
        glo.TheTrackThread.start()
        glo.TheStrategyThread = StrategyThread(3, "Strategy", 3)
        glo.TheStrategyThread.start()
    elif glo.MODE_SELECT == 2:
        pass
    else:
        pass


def Control():
    #glo.MODE_SELECT select the workmodel
    #1: TrackTest 2: BallTest 3: TogetherRun
    if glo.MODE_SELECT == 1:
        if (glo.TURN_FLAG == True):
            goAndTurn()
            glo.TURN_FLAG = False
        else:
            glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
            if glo.TheTrackDelta == 0:
                radius = glo.TheDirection.control(10000)  # 1.0/0.0001
            else:
                radius = glo.TheDirection.control(1.0 / glo.TheTrackDelta)
            #print "Direction:", radius
            glo.TheKobuki.setDirection(radius)
            glo.TheKobuki.sendCommand()
    elif glo.MODE_SELECT == 2:
        pass
    else:
        pass

class TrackThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.img = None
        self.imgOrigin = None
        self.track = None
        #open and set capture
        self.trackCam = cv2.VideoCapture(glo.TRACK_CAM)
        i = 0
        while self.trackCam.isOpened() is False:
            self.trackCam.release()
            self.trackCam = cv2.VideoCapture(glo.TRACK_CAM)
            if i > 9 and self.trackCam.isOpened() is False:
                print("Can not open trackCam after 10 times!")
                self.trackCam.release()
                exit()
            i = i + 1
        #self.trackCam.set(cv2.CAP_PROP_FRAME_WIDTH,180)
        #self.trackCam.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
        ret = None
        ret, self.imgOrigin = self.trackCam.read()
        if ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,\
                                  fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            self.track = FindTrack(self.img, debugFlag=False)
            self.flag  = FindBall(self.img,debugFlag=False)
        else:
            print "Can not get track img!"
            self.trackCam.release()
            exit()
        #open and set capture
        #read para
        self.Para = None
        flagParaGet  = Parameter(configFile=glo.FLAG_CONFIG)
        trackParaGet = Parameter(configFile=glo.TRACK_CONFIG)
        namelistFlag, self.Para = trackParaGet.ReadConfig()
        if self.Para[7] % 2 == 0:  # special process for blur size
            self.Para[7] += 1
        namelist,self.ParaFlag = flagParaGet.ReadConfig()
        print "track config file:", glo.TRACK_CONFIG
        print namelist
        print self.Para
        print "flag config file:", glo.FLAG_CONFIG
        print namelistFlag
        print self.ParaFlag
        #read para

    def run(self):
        ret, self.imgOrigin = self.trackCam.read()
        while ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,\
                                  fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            tempDelta = processTrackImg(self.img, self.track, self.Para)
            tempCount = processFlagImg(self.img,self.flag,self.ParaFlag)
            #cv2.imshow("img",self.img)
            key = cv2.waitKey(1)
            if key == 27:
                break
            glo.TheThreadLock.acquire()
            glo.TheTrackDelta = tempDelta
            if tempCount > 0:
                glo.TheFlagCount += 1
            else:
                glo.TheFlagCount = 0
            glo.TheThreadLock.release()
            ret, self.imgOrigin = self.trackCam.read()
            if glo.MAIN_STOP_FLAG is True:
                print "track thread stop"
                break
        self.exitThread()

    def exitThread(self):
        self.trackCam.release()
        #print "trackCam release!"
        exit()


def processTrackImg(img, track, para):
    '''
    parameterList:
    lower_color     :para[0:3]
    upper_color     :para[3:6]
    threshold       :para[6]
    blurSize        :para[7]
    minVal          :para[8]
    maxVal          :para[8]*3
    linePointCount  :para[9]
    minLineLength   :para[10]
    maxLineGap      :para[11]

    '''
    track.updateImg(img)
    track.hsvFilter(tuple(para[0:3]), tuple(para[3:6]))
    track.converToBinary(para[6])
    track.getCenter(blurSize=para[7], minVal=para[8], maxVal=para[8] * 3,\
                    linePointCount=para[9], minLineLength=para[10], maxLineGap=para[11],\
                    slopeThreshold=math.tan(math.pi / 6),\
                    defaultPos=int(glo.TRACK_TARGET))
    tempDelta=track.getDelta(default=False,\
            prospect=glo.TRACK_PROSPECT,target=glo.TRACK_TARGET)
    if glo.DEBUG_FLAG is True:
        track.draw(DeltaFlag=True)
    return tempDelta


def processFlagImg(img, flag, para):
    flag.updateImg(img)
    flag.hsvFilter(tuple(para[0:3]), tuple(para[3:6]))
    flag.converToBinary(para[6])
    tempContour,tempCenter = flag.getCenter(contoursRange=tuple(para[7:9])\
    , ksize=(para[9], para[9]))
    count = 0
    for point in tempCenter:
        if point[0] > glo.POINTAREA_X_LOW \
            and point[0] < glo.POINTAREA_X_HIGH \
            and point[1] > glo.POINTAREA_Y:
            count = count + 1
    if glo.DEBUG_FLAG is True:
        flag.draw()
    return count

class StrategyThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            if glo.MODE_SELECT == 1:
                if glo.TheFlagCount > glo.TheFlagCountMin :
                     glo.TURN_FLAG = True
            elif glo.MODE_SELECT == 2:
                pass
            else:
                pass
            Control()
            if glo.MAIN_STOP_FLAG is True:
                print "strategy thread stop"
                break
        exit()


def goAndTurn():
    for k in range(2):
        glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
        glo.TheKobuki.setDirection(0)
        glo.TheKobuki.sendCommand()
        time.sleep(glo.FORWARD_TIME)
    for i in range(4):
        glo.TheKobuki.setSpeed(glo.TURN_SPEED)
        glo.TheKobuki.setDirection(1)
        glo.TheKobuki.sendCommand()
        time.sleep(glo.TURN_FLAG)
        glo.TheKobuki.setSpeed(0)
        glo.TheKobuki.setDirection(0)
        glo.TheKobuki.sendCommand()
def signal_handler(signum,frame):
    glo.MAIN_STOP_FLAG = True
    print "Receive the signal!!",glo.MAIN_STOP_FLAG
    cv2.destroyAllWindows()
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    systemInit()
    while True:
        time.sleep(1)
