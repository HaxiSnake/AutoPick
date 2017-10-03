#global flags
KOBUKI_COM   = "COM5"
DOBOT_COM    = "COM4"
TRACK_CAM    = 1
BALL_CAM     = 0
BALL_CONFIG  = ".\\Config\\BallConfig.txt"
TRACK_CONFIG = ".\\Config\\TrackConfig.txt"
DEBUG_FLAG   = True
MAIN_STOP_FLAG = False
PICK_FLAG   = False
#global flags
#variable
KOBUKI_SPEED = 0x80
PICK_POSITION= 100
HEIGHT       = 240
PICK_RANGE   = 30
TRACK_P      = 0.01
TRACK_D      = 0.0
TheTrackDelta = 0.0
TheThreadLock = None
TheDistance  = None
TheHighFlag  = None  
#variable
#class
TheDirection = None
TheKobuki    = None
TheDobot     = None
TheTrackThread = None
TheBallThread = None
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
