import os
import sys
import cv2
import time
import threading
import signal
#workdir = "G:\\AutoPickRobot\\AutoPick"
workdir = "/home/pi/Classify"
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
        glo.TheKobuki = Kobuki(glo.KOBUKI_COM)
        glo.TheThreadLock = threading.Lock()
        glo.TheBallThread = BallThread(2, "Ball", 2)
        glo.TheBallThread.start()
        glo.TheStrategyThread = StrategyThread(3, "Strategy", 3)
        glo.TheStrategyThread.start()
    else:
        time.sleep(1)
        glo.TheKobuki = Kobuki(glo.KOBUKI_COM)
        glo.TheDirection = glo.PID(P=glo.TRACK_P, D=glo.TRACK_D)
        glo.TheThreadLock = threading.Lock()
        glo.TheTrackThread = TrackThread(1, "Track", 1)
        glo.TheTrackThread.start()
        glo.TheBallThread = BallThread(2, "Ball", 2)
        glo.TheBallThread.start()
        glo.TheDobot = Dobot(glo.DOBOT_COM)
        glo.TheStrategyThread = StrategyThread(3,"Strategy",3)
        glo.TheStrategyThread.start()
        time.sleep(0.5)


def Control():
    #glo.MODE_SELECT select the workmodel
    #1: TrackTest 2: BallTest 3: TogetherRun
    if glo.MODE_SELECT == 1:
        glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
        if glo.TheTrackDelta == 0:
            radius = glo.TheDirection.control(10000)  # 1.0/0.0001
        else:
            radius = glo.TheDirection.control(1.0 / glo.TheTrackDelta)
        #print "Direction:", radius
        glo.TheKobuki.setDirection(radius)
        glo.TheKobuki.sendCommand()
    elif glo.MODE_SELECT == 2:
        if glo.PICK_FLAG is False:
            glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
            glo.TheKobuki.setDirection(0.0)
            glo.TheKobuki.sendCommand()
        else:
            glo.TheKobuki.setSpeed(0)
            glo.TheKobuki.setDirection(0.0)
            glo.TheKobuki.sendCommand()
            if glo.CHOOSEBIG_FLAG is True and glo.TheBigFlag is True:
                push()
            elif glo.CHOOSEBIG_FLAG is False and glo.TheBigFlag is False:
                push()
            glo.PICK_FLAG = False
    else:
        if glo.PICK_FLAG is False:
            glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
            if glo.TheTrackDelta == 0:
                radius = glo.TheDirection.control(10000)  # 1.0/0.0001
            else:
                radius = glo.TheDirection.control(1.0 / glo.TheTrackDelta)
            glo.TheKobuki.setDirection(radius)
            glo.TheKobuki.sendCommand()
        else:
            glo.TheKobuki.setSpeed(0)
            glo.TheKobuki.setDirection(0.0)
            glo.TheKobuki.sendCommand()
            if glo.CHOOSEBIG_FLAG is True and glo.TheBigFlag is True:
                push()
            elif glo.CHOOSEBIG_FLAG is False and glo.TheBigFlag is False:
                push()
            glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
            if glo.TheTrackDelta == 0:
                radius = glo.TheDirection.control(10000)  # 1.0/0.0001
            else:
                radius = glo.TheDirection.control(1.0 / glo.TheTrackDelta)
            glo.TheKobuki.setDirection(radius)
            glo.TheKobuki.sendCommand()
            time.sleep(glo.GOSTR_TIME)
            glo.PICK_FLAG = False


def grub(HighFlag):
    if HighFlag is True:
        print("Pick High!")
        glo.TheDobot.pickHigh()
    else:
        print("Pick Low!")
        glo.TheDobot.pickLow()
    time.sleep(glo.GRUB_TIME)
def push():
    glo.TheDobot.push()

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
        #self.trackCam.set(cv2.CAP_PROP_FRAME_WIDTH,320)
        #self.trackCam.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        ret = None
        ret, self.imgOrigin = self.trackCam.read()
        if ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,\
                                  fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            self.track = FindTrack(self.img, debugFlag=False)
        else:
            print "Can not get track img!"
            self.trackCam.release()
            exit()
        #open and set capture
        #read para
        self.Para = None
        trackParaGet = Parameter(configFile=glo.TRACK_CONFIG)
        namelist, self.Para = trackParaGet.ReadConfig()
        if self.Para[7] % 2 == 0:  # special process for blur size
            self.Para[7] += 1
        print "track config file:", glo.TRACK_CONFIG
        print namelist
        print self.Para
        #read para

    def run(self):
        ret, self.imgOrigin = self.trackCam.read()
        while ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,\
                                  fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            tempDelta = processTrackImg(self.img, self.track, self.Para)
            #cv2.imshow("img",self.img)
            key = cv2.waitKey(1)
            if key == 27:
                break
            glo.TheThreadLock.acquire()
            glo.TheTrackDelta = tempDelta
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

class BallThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.img = None
        self.imgOrigin = None
        self.ball = None
        #open and set capture
        self.ballCam = cv2.VideoCapture(glo.BALL_CAM)
        i = 0
        while self.ballCam.isOpened() is False:
            self.ballCam.release()
            self.ballCam = cv2.VideoCapture(glo.TRACK_CAM)
            if i > 9 and self.ballCam.isOpened() is False:
                print("Can not open ballCam after 10 times!")
                self.ballCam.release()
                exit()
            i = i + 1
        #self.ballCam.set(cv2.CAP_PROP_FRAME_WIDTH,320)
        #self.ballCam.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        ret = None
        ret, self.imgOrigin = self.ballCam.read()
        self.tempImg = self.imgOrigin[:,0:320]
        if ret is True:
           # self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,\
            self.img = cv2.resize(self.tempImg, None, fx=glo.IMG_SCALE,\
                                  fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            self.ball = FindBall(self.img, debugFlag=False)
        else:
            print "Can not get ball img!"
            self.ballCam.release()
            exit()
        
        #open and set capture
        #read para
        self.Para = None
        ballParaGet = Parameter(configFile=glo.BALL_CONFIG)
        namelist, self.Para = ballParaGet.ReadConfig()
        print "Ball config file:", glo.TRACK_CONFIG
        print namelist
        print self.Para
        #read para

    def run(self):
        ret, self.imgOrigin = self.ballCam.read()
        while ret is True:
            #self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,\
            self.tempImg = self.imgOrigin[:,0:320]
            self.img = cv2.resize(self.tempImg, None, fx=glo.IMG_SCALE,\
                                  fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            tempDistance, tempBigFlag = processBallImg(\
                self.img, self.ball, self.Para)
            key = cv2.waitKey(1)
            if key == 27:
                break
            glo.TheThreadLock.acquire()
            glo.TheDistance = tempDistance
            glo.TheBigFlag = tempBigFlag
            glo.TheThreadLock.release()
            ret, self.imgOrigin = self.ballCam.read()
            if glo.MAIN_STOP_FLAG is True:
                print "Ball thread stop"
                break
        self.exitThread()

    def exitThread(self):
        self.ballCam.release()
        exit()


def processBallImg(img, ball, para):
    ball.updateImg(img)
    ball.hsvFilter(tuple(para[0:3]), tuple(para[3:6]))
    ball.converToBinary(para[6])
    ball.getCenter(contoursRange=tuple(para[7:9]), ksize=(para[9], para[9]))
    Distance, BigFlag = ball.BigOrSmall(\
        PickPosition=glo.PICK_POSITION, BallSize=glo.BALL_SIZE)
    if glo.DEBUG_FLAG is True:
        ball.draw(calFlag=True)
    return Distance, BigFlag

class StrategyThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            if glo.MODE_SELECT == 1:
                print "Track Delta:", glo.TheTrackDelta
            elif glo.MODE_SELECT == 2:
                if glo.TheDistance is not None and glo.TheBigFlag is not None:
                    print "Distance:", glo.TheDistance
                    print "HighFlag:", glo.TheBigFlag
                    if glo.TheDistance < glo.PICK_RANGE_HIGH \
                        and glo.TheDistance > glo.PICK_RANGE_LOW:
                        glo.PICK_FLAG = True
                else:
                    print "NONE BALL!"
            else:
                if glo.TheDistance is not None and glo.TheBigFlag is not None:
                    if glo.TheDistance < glo.PICK_RANGE_HIGH \
                       and glo.TheDistance > glo.PICK_RANGE_LOW:
                        glo.PICK_FLAG = True
            Control()
            if glo.MAIN_STOP_FLAG is True:
                print "strategy thread stop"
                break
        exit()
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
