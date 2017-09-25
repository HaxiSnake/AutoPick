import cv2
import numpy
import math
import sys
class Line:
    '''A class for line'''
    def __init__(self,x0,y0,k):
        self.x0 = x0
        self.y0 = y0
        self.k  = k
    def getY(self,x):
        if (self.k == float("inf") or self.k == float("-inf")):
            self.y = float("inf")
            print ("y is inf!!")
        else:
            self.y = 1.0*self.k*(x-self.x0)+self.y0
        return self.y
    def getX(self,y):
        if(self.k == 0):
            self.x = float("inf")
            print ("x is inf!")
        else:
            self.x = (y-self.y0)*1.0/self.k+self.x0
        return self.x
    def update(self,x,y,k):
        self.x0 = x
        self.y0 = y
        self.k  = k
class FindObject:
    'A class to find object with opencv2. require: cv2 numpy'
    def __init__(self,img,debugFlag=False):
        self.img     = img
        self.hsvmask = None
        self.binary  = None
        self.debugFlag = debugFlag
        print ("A FindObject Class is created!")
    def updateImg(self,img):
        '''update img
            input:img
            return: img
        '''
        if img is None :
            print("img is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit()
        self.img = img
        return self.img
    def hsvFilter(self,lower_color=(0,0,0),upper_color=(255,255,255)):
        ''' convert to HSV color space and threshold
            input: lower_color=(0,0,0),upper_color=(255,255,255)
            return: img
        '''
        self.hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(self.hsv, lower_color, upper_color)
        self.hsvmask = cv2.bitwise_and(self.img, self.img, mask=self.mask)

        if self.debugFlag is True :
            cv2.imshow('hsvFilter',self.hsvmask)
        return self.hsvmask
    def converToBinary(self,thresholdValue=0):
        ''' convert to binary 
            input: thresholdValue=0
            return: img
            attention: hsvFileter need run firstly
        '''
        if self.hsvmask is None:
            print("hsvmask is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit()
        else:
            self.gray = cv2.cvtColor(self.hsvmask,cv2.COLOR_BGR2GRAY)
            self.retval,self.binary = cv2.threshold(self.gray, thresholdValue, 255, cv2.THRESH_BINARY)
            if self.debugFlag is True :
                cv2.imshow('converToBinary',self.binary)
            return self.binary
    def erode(self,shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None):
        ''' Erodes an image by using a specific structuring element.
            input : shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None
            return: img
            attention: converToBinary need run before this
        '''
        if binaryImg is None:
            binaryImg = self.binary
        if binaryImg is None:
            print("binary is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit() 
        else:
            kernel = cv2.getStructuringElement(shape,ksize)
            self.erodeImg = cv2.erode(binaryImg,kernel)  
            if self.debugFlag is True :
                cv2.imshow('erode',self.erodeImg)
            return self.erodeImg               
    def dilate(self,shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None):
        ''' Dilates an image by using a specific structuring element.
            input : shape=cv2.MORPH_RECT, ksize=(3,3),binaryImg = None
            return: img
            attention: converToBinary need run before this
        '''
        if binaryImg is None:
            binaryImg = self.binary
        if binaryImg is None:
            print("binary is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit() 
        else:
            kernel = cv2.getStructuringElement(shape,ksize)
            self.dilateImg = cv2.dilate(binaryImg,kernel)  
            if self.debugFlag is True :
                cv2.imshow('dilate',self.dilateImg)
            return self.dilateImg
    def getCenter(self):
        pass

class FindBall(FindObject):
    def getCenter(self,binaryImg=None,contoursRange=(60,1000),dilateFlag=True, ksize=(3,3)):
        '''Get the center the of the ball
        input : binaryImg,contoursRange=(200,1000)
        return: coutours,img
        '''
        self.CenterP=[]
        if binaryImg is None :
            binaryImg = self.binary
        if binaryImg is None :
            print("binary is None!",sys._getframe().f_lineno,sys._getframe().f_code.co_name)
            exit()
        else:  
            if dilateFlag is True :
                tempImg = binaryImg
                binaryImg=self.dilate(ksize=ksize,binaryImg=tempImg)
            self.contourImg,self.contours,hierarchy = cv2.findContours(binaryImg,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            i = 0
            count = len(self.contours)
            while (i<count):
                if self.contours[i].shape[0] < contoursRange[0] or self.contours[i].shape[0] > contoursRange[1]:
                    del self.contours[i]
                    count = count - 1
                    i = i - 1
                i = i + 1
            i = 0
            count = len(self.contours)
            while (i < count ):
                x, y, w, h = cv2.boundingRect(self.contours[i])
                if w > h:
                    k=w/h
                else:
                    k=h/w
                if k > 3:
                    #delete narrow contours
                    del self.contours[i]
                    count = count - 1
                    continue
                else:
                    area = math.fabs(cv2.contourArea(self.contours[i]))
                    if area >0:
                        if (w*h/area) > 3:
                            #delete tilt and narrow contours 
                            del self.contours[i]
                            count = count - 1
                            i = i - 1
                    i = i + 1

            if len(self.contours) >=1 :
                i=0 
                count = len(self.contours)
                _white =  (255, 255, 255)
                while(i<count):
                    x, y, w, h = cv2.boundingRect(self.contours[i])
                    lx = x + w/2
                    ly = y + h/2
                    
                    self.CenterP.append([lx,ly])
                    i=i+1
                self.CenterP = numpy.asarray(self.CenterP)
                idex = numpy.lexsort([self.CenterP[:,1],self.CenterP[:,0]])
                self.CenterP = self.CenterP[idex,:]
                return  self.contours,self.CenterP
            else :
                self.CenterP = numpy.asarray(self.CenterP)
                return self.contours,self.CenterP

    def draw(self):
        _white =  (255, 255, 255)
        if len(self.contours) > 0 and len(self.contours) == len(self.CenterP):
            self.drawImg = self.img.copy()
            #cv2.drawContours(self.drawImg,self.contours,-1,_white,5)
            i=0
            count = len(self.CenterP)
            while(i<count):
                cv2.circle(self.drawImg, (self.CenterP[i][0], self.CenterP[i][1]),4, _white, -1)
                area = math.fabs(cv2.contourArea(self.contours[i]))
                cv2.circle(self.drawImg, (self.CenterP[i][0], self.CenterP[i][1]), int(math.sqrt(area/math.pi)), _white, 0)
                i = i + 1
            cv2.imshow("Redball",self.drawImg)

class FindTrack(FindObject):
    def __init__(self,img,debugFlag=False):
        self.img     = img
        self.hsvmask = None
        self.binary  = None
        self.debugFlag = debugFlag
        self.imgSize = img.shape
        self.Middle = Line(self.imgSize[1]/2,0,float("inf"))
        print ("A FindTrack Class is created!")
    def getCenter(self,minVal=50,maxVal=150,\
        linePointCount=60,minLineLength=120,maxLineGap=10,\
        slopeThreshold=math.tan(math.pi/6)):
        
        #self.tempImg=self.dilate(ksize=(2,2))
        self.tempImg = cv2.medianBlur(self.binary.copy(),15)
        self.edges = cv2.Canny(self.tempImg.copy(),minVal,maxVal)
        self.lines = cv2.HoughLinesP(self.edges,1,numpy.pi/180,linePointCount,minLineLength,maxLineGap) 
        if self.lines is not None:
            self.leftLines = []
            self.rightLines = []
            
            for item in self.lines:
                x1 = item[0][0]
                y1 = item[0][1]
                x2 = item[0][2]
                y2 = item[0][3]
                if (0 == (x2-x1)):
                    if y2 > y1 :
                        k = float("inf")
                    else:
                        k = float("-inf")
                else :
                    k  = (y2 - y1)*1.0/(x2 - x1)
                if (k < 0.0 - slopeThreshold ):
                    self.leftLines.append(item[0])
                if (k > slopeThreshold ):
                    self.rightLines.append(item[0])
            if self.debugFlag is True:
                self.lineTemp = self.img.copy()
                self.imgSize = self.lineTemp.shape
                if self.leftLines is not None :
                    for item in self.leftLines:
                        cv2.line(self.lineTemp,(item[0],item[1]),(item[2],item[3]  ),(255,0,0),3)
                if self.rightLines is not None :
                    for item in self.rightLines:
                        cv2.line(self.lineTemp,(item[0],item[1]),(item[2],item[3]  ),(0,0,255),3)              
                tempMiddleX =[0,0]
                tempMiddleY =[0,0]
                if self.leftLines is not None and self.rightLines is not None:
                    count = min(len(self.rightLines),len(self.leftLines))
                    i=0 
                    sumRX=[0,0]
                    sumLX=[0,0]
                    while(i < count ):
                        kL =  (self.leftLines[i][3]-self.leftLines[i][1])*1.0/(self.leftLines[i][2]-self.leftLines[i][0])
                        kR =  (self.rightLines[i][3]-self.rightLines[i][1])*1.0/(self.rightLines[i][2]-self.rightLines[i][0])
                        LineL = Line(self.leftLines[i][0],self.leftLines[i][1],kL)
                        LineR = Line(self.rightLines[i][0],self.rightLines[i][1],kR) 
                        sumLX[0] = sumLX[0] + LineL.getX(self.imgSize[0]*1.0/2)
                        sumLX[1] = sumLX[1] + LineL.getX(self.imgSize[0]*1.0*2/3)
                        sumRX[0] = sumRX[0] + LineR.getX(self.imgSize[0]*1.0/2)
                        sumRX[1] = sumRX[1] + LineR.getX(self.imgSize[0]*1.0*2/3)
                        i = i + 1
                    tempMiddleY[0] = self.imgSize[0]*1.0/2
                    tempMiddleY[1] = self.imgSize[0]*1.0*2/3
                    tempMiddleX[0] = (sumLX[0]*1.0/count+sumRX[0]*1.0/count)/2.0
                    tempMiddleX[1] = (sumLX[1]*1.0/count+sumRX[1]*1.0/count)/2.0
                    
                    if tempMiddleX[1] == tempMiddleX[0] :
                        tempMiddleK = float("inf")
                    else :
                        tempMiddleK = (tempMiddleY[1]-tempMiddleY[0])*1.0 /(tempMiddleX[1]-tempMiddleX[0])
                    self.Middle.update(tempMiddleX[0],tempMiddleY[0],tempMiddleK)
                    cv2.line(self.lineTemp,\
                    (int(self.Middle.getX(0)),0),\
                    (int(self.Middle.getX(self.imgSize[0])),self.imgSize[0]),\
                    (0,255,255),3)
                
                cv2.line(self.lineTemp,(self.imgSize[1]/2,0),(self.imgSize[1]/2,self.imgSize[0]),(255,255,0),3)
                cv2.line(self.lineTemp,(0,int(self.imgSize[0]*1.0/2)),(self.imgSize[1],int(self.imgSize[0]*1.0/2)),(255,255,0),1)
                cv2.line(self.lineTemp,(0,int(self.imgSize[0]*1.0*2/3)),(self.imgSize[1],int(self.imgSize[0]*1.0*2/3)),(255,255,0),1)
                cv2.imshow("Lines after slope choose",self.lineTemp)

        if self.debugFlag is True:
            self.drawImg = self.img.copy()
            if self.lines is not None:
                #print (len(self.lines))
                for items in self.lines:
                    x1 = items[0][0]
                    y1 = items[0][1]
                    x2 = items[0][2]
                    y2 = items[0][3]
                    #print(items)
                    cv2.line(self.drawImg,(x1,y1),(x2,y2),(0,255,0),3)
            cv2.imshow("canny",self.edges)
            cv2.imshow("houghLinesP",self.drawImg)
        




    