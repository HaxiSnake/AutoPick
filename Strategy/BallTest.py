import os
import sys
import cv2
import time
import threading
#workdir = "G:\\AutoPickRobot\\AutoPick"
workdir = "/home/pi/AutoPick"
#workdir = "E:\\WORKSPACE\\2_Haobbys\\AutoPickRobot\\AutoPick"
os.chdir(workdir)
sys.path.append(os.getcwd())
from Driver.Kobuki     import *
from Driver.Dobot      import *
from Tools.ParaSave    import *
from Vision.FindObject import *
import glo

def systemInit():
    glo.TheKobuki     = Kobuki(glo.KOBUKI_COM)
    #glo.TheDobot     = Dobot(glo.DOBOT_COM)
    glo.TheDirection  = glo.PID(P=glo.TRACK_P,D=glo.TRACK_D) 
    glo.TheThreadLock = threading.Lock()
    glo.TheTrackThread= TrackThread(1,"Track",1)
    glo.TheTrackThread.start()
def Control():
    if glo.PICK_FLAG is False:
        glo.TheKobuki.setSpeed(glo.KOBUKI_SPEED)
        #glo.TheKobuki.setDirection(glo.TheDirection.control(glo.TheTrackDelta))
        glo.TheKobuki.setDirection(0.0)
        glo.TheKobuki.sendCommand()
    else:
        glo.TheKobuki.setSpeed(0)
        glo.TheKobuki.setDirection(0.0)
        glo.TheKobuki.sendCommand()
        grub(glo.TheHighFlag)
        glo.PICK_FLAG = False
    glo.TheKobuki.sendCommand()
def grub(HighFlag):
    if HighFlag is True:
        print("Pick High!")
    else:
        print("Pick Low!")
    time.sleep(2)
class TrackThread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name     = name
        self.counter  = counter
        self.img      = None
        self.imgOrigin= None
        self.track    = None
        #open and set capture
        self.trackCam = cv2.VideoCapture(glo.TRACK_CAM)
        if self.trackCam.isOpened() is False:
            print "Can not open trackCam!"
            self.trackCam.release()
            exit()
        #self.trackCam.set(cv2.CAP_PROP_FRAME_WIDTH,180)
        #self.trackCam.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
        ret = None
        ret,self.imgOrigin =self.trackCam.read()
        if ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            self.track = FindTrack(self.img,debugFlag=False)
        else:
            print "Can not get track img!"
            self.trackCam.release()
            exit()
        #open and set capture
        #read para
        self.Para = None
        trackParaGet = Parameter(configFile=glo.TRACK_CONFIG)
        namelist,self.Para=trackParaGet.ReadConfig()
        if self.Para[7]%2 == 0:#special process for blur size
            self.Para[7] +=1
        print "Track config file:",glo.TRACK_CONFIG
        print namelist
        print self.Para
        #read para
    def run(self):
        ret, self.imgOrigin = self.trackCam.read()
        while ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            tempDelta = processTrackImg(self.img,self.track,self.Para)
            #cv2.imshow("img",self.img)
            key = cv2.waitKey(1)
            if key == 27:
                break
            glo.TheThreadLock.acquire()
            glo.TheTrackDelta = tempDelta
            glo.TheThreadLock.release()
            ret, self.imgOrigin = self.trackCam.read()
            if glo.MAIN_STOP_FLAG is True:
                self.exitThread()
                print "Track thread stop"
                break
    def exitThread(self):
        self.trackCam.release()


def processTrackImg(img,track,para):
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
    track.hsvFilter(tuple(para[0:3]),tuple(para[3:6]))
    track.converToBinary(para[6])
    track.getCenter(blurSize=para[7],minVal=para[8],maxVal=para[8]*3,\
                    linePointCount=para[9],minLineLength=para[10],maxLineGap=para[11],\
                    slopeThreshold=math.tan(math.pi/6))
    if glo.DEBUG_FLAG is True:
        track.draw()
    return track.getDelta()
    
class BallThread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name     = name
        self.counter  = counter
        self.img      = None
        self.imgOrigin= None
        self.ball    = None
        #open and set capture
        self.ballCam = cv2.VideoCapture(glo.BALL_CAM)
        if self.ballCam.isOpened() is False:
            print "Can not open ballCam!"
            self.ballCam.release()
            exit()
        #self.ballCam.set(cv2.CAP_PROP_FRAME_WIDTH,180)
        #self.ballCam.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
        ret = None
        ret, self.imgOrigin = self.ballCam.read()
        if ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            self.ball = FindBall(self.img,debugFlag=False)
        else:
            print "Can not get ball img!"
            self.ballCam.release()
            exit()
        #open and set capture
        #read para
        self.Para = None
        ballParaGet = Parameter(configFile=glo.BALL_CONFIG)
        namelist,self.Para=ballParaGet.ReadConfig()
        print "Ball config file:",glo.TRACK_CONFIG
        print namelist
        print self.Para
        #read para
    def run(self):
        ret, self.imgOrigin = self.ballCam.read()
        while ret is True:
            self.img = cv2.resize(self.imgOrigin, None, fx=glo.IMG_SCALE,fy=glo.IMG_SCALE, interpolation=cv2.INTER_AREA)
            processBallImg(self.img,self.ball,self.Para)
            if glo.TheHighFlag is not None and glo.TheDistance is not None:
                print "Distance:",glo.TheDistance
                print "HighFlag:",glo.TheHighFlag
            else:
                print "IS NONE!"
            key = cv2.waitKey(1)
            if key == 27:
                break
            glo.TheThreadLock.acquire()
            #glo.TheTrackDelta = tempDelta
            glo.TheThreadLock.release()
            ret, self.imgOrigin = self.ballCam.read()
            if glo.MAIN_STOP_FLAG is True:
                self.exitThread()
                print "Ball thread stop"
                break
    def exitThread(self):
        self.ballCam.release()
def processBallImg(img,ball,para):
    ball.updateImg(img)
    ball.hsvFilter(tuple(para[0:3]),tuple(para[3:6]))
    ball.converToBinary(para[6])
    ball.getCenter(contoursRange=tuple(para[7:9]), ksize=(para[9],para[9]))
    glo.TheThreadLock.acquire()
    glo.TheDistance,glo.TheHighFlag=ball.calculate(PickPosition=glo.PICK_POSITION,Height=glo.HEIGHT)
    glo.TheThreadLock.release()
    if glo.DEBUG_FLAG is True:
        ball.draw(calFlag=True)

if __name__ == "__main__":
    #systemInit()
    glo.TheKobuki     = Kobuki(glo.KOBUKI_COM)
    glo.TheThreadLock = threading.Lock()
    glo.TheBallThread=BallThread(2,"Ball",2)
    glo.TheBallThread.start()
    count = 0
    while True:
        if glo.TheDistance is not None and glo.TheHighFlag is not None  :
            if glo.TheDistance < glo.PICK_RANGE :
                glo.PICK_FLAG = True
        Control()
        #time.sleep(0.001)
        count += 1
        if count > 100000:
            #count = 0
            break
    glo.MAIN_STOP_FLAG = False
    exit()
