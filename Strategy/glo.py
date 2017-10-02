#global flags
KOBUKI_COM   = "COM5"
DOBOT_COM    = "COM4"
TRACK_CAM    = 1
BALL_CONFIG  = ".\\Config\\BallConfig.txt"
TRACK_CONFIG = ".\\Config\\TrackConfig.txt"
DEBUG_FLAG   = True
MAIN_STOP_FLAG = False
#global flags
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

#variable
TheTrackDelta = 0.0
TheThreadLock = None
TheTrackThread = None
#class
TheDirection = None
TheKobuki    = None
TheDobot     = None
