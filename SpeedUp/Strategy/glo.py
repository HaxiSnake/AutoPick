#global flags
KOBUKI_COM   = "/dev/ttyUSB0"
TRACK_CAM    = 0
FLAG_CONFIG  = "./Config/FlagConfig.txt"
TRACK_CONFIG = "./Config/SpeedConfig.txt"
IMG_SCALE    = 0.5
MODE_SELECT = 1   #1:TrackTest 2:BallTest 3:TogetherRun
DEBUG_FLAG   = True
MAIN_STOP_FLAG = False
TURN_FLAG = False
#global flags
#variable
KOBUKI_SPEED = 0x99
TURN_SPEED   = 0x80
FORWARD_TIME = 4.5 
TURN_TIME = 2.4
TRACK_P      = 20000.0
TRACK_D      = 10.0
TRACK_PROSPECT = 480*0.5*4/5
TRACK_TARGET   = 640*0.5/2 
POINTAREA_X_LOW  = 480 * 0.5 /10000
POINTAREA_X_HIGH = 480 * 0.5 * 5/5
POINTAREA_Y      = 640 * 0.5 / 5
TheTrackDelta = 0.0
TheFlagCount = 0
TheFlagCountMin = 2
TheThreadLock = None 
#variable
#class
TheDirection = None
TheKobuki    = None
TheTrackThread = None
TheBallThread = None
TheStrategyThread = None
#class
class PID:
    def __init__(self,P=1.0,I=0.0,D=0.0):
        self.P = P
        self.I = I
        self.D = D
        self.deltaNow = 0.0
        self.deltaOld = 0.0
        self.errI     = 0.0
        self.Out = 0.0
    def control(self,delta):
        self.deltaNow = delta
        self.errI = self.errI + self.deltaNow
        self.Out = self.P * (self.deltaNow) + self.I*self.errI + self.D * (self.deltaNow -self.deltaOld)
        self.deltaOld = self.deltaNow
        return self.Out
