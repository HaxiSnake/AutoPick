import cv2
import numpy
import sys

class TrackBar():
    'A class to get TrackBar Value. Require: cv2 numpy'
    def __init__(self,winName='TrackBar',windowSize=(400,300)):
        self.winName = winName
        self.nameList = ['Temp']
        self.valueRange = [(0,255)]
        self.trackbarResult = []
        cv2.namedWindow(self.winName)
        cv2.resizeWindow(self.winName, windowSize[0], windowSize[1])
    def nothing(self,test):
        'A function to be the parameter of cv2.createTrackbar '
        pass
    def creatTrackbar(self,nameList = ['Temp'],valueRange = [(0,255)]):
        'Creat Trackbar'
        self.nameList = nameList
        self.valueRange = valueRange
        self.listLenth = len(self.nameList)
        if (self.listLenth > 0):
            for name,value in zip(self.nameList,self.valueRange):
                cv2.createTrackbar(name,self.winName,value[0],value[1],self.nothing)
        else:
             print("Namelist is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
             exit()
        print 'Creat Trackbar Done!'
    def getTrackbarValue(self):
        'Get TrackbarValue'
        if(self.listLenth > 0):
            self.trackbarResult = []
            for name in self.nameList:
                tempResult = cv2.getTrackbarPos(name, self.winName )
                self.trackbarResult.append( tempResult )
            return self.trackbarResult
        else :
             print("Namelist is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
             exit()

    
