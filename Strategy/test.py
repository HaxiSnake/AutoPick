import os
import sys
import cv2
import time
import threading
workdir = "G:\\AutoPickRobot\\AutoPick"
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
    glo.TheDirection  = glo.PID(P=1.0,D=0.0) 
    glo.TheThreadLock = threading.Lock()
    glo.TheTrackThread= TrackThread(1,"Track",1)
    glo.TheTrackThread.start()
def KobukiControl():
    glo.TheKobuki.setSpeed(0x80)
    glo.TheKobuki.setDirection(glo.TheTrackDelta)
    glo.TheKobuki.sendCommand()
def grub():
    pass
class TrackThread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name     = name
        self.counter  = counter
        self.img      = None
        self.track    = None
        #open and set capture
        self.trackCam = cv2.VideoCapture(0)
        if self.trackCam.isOpened() is False:
            print "Can not open trackCam!"
            self.trackCam.release()
            exit()
        #self.trackCam.set(cv2.CAP_PROP_FRAME_WIDTH,180)
        #self.trackCam.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
        ret = None
        ret,self.img =self.trackCam.read()
        if ret is True:
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
        print "track config file:",glo.TRACK_CONFIG
        print namelist
        print self.Para
        #read para
    def run(self):
        ret,self.img = self.trackCam.read()
        while ret is True:
            tempDelta = processTrackImg(self.img,self.track,self.Para)
            #cv2.imshow("img",self.img)
            key = cv2.waitKey(1)
            if key == 27:
                break
            glo.TheThreadLock.acquire()
            glo.TheTrackDelta = tempDelta
            glo.TheThreadLock.release()
            ret,self.img = self.trackCam.read()
            if glo.MAIN_STOP_FLAG is True:
                self.exitThread()
                print "track thread stop"
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
    


if __name__ == "__main__":
    systemInit()
    count = 0
    while True:
        KobukiControl()
        print "delta:",glo.TheTrackDelta
        time.sleep(0.020)
        count += 1
        if count > 500:
            break
    glo.MAIN_STOP_FLAG = True
    exit()