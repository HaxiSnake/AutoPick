import cv2
import numpy
import os
import sys
os.chdir("G:\\AutoPick")
sys.path.append(os.getcwd())
from Vision.FindObject import * 
from Vision.DebugUI import *
from Tools.ParaSave import *
#paraList
            #lower_color
nameList = ['Hmin',"Smin","Vmin",\
            #upper_color
            "Hmax","Smax","Vmax",\
            #threshold
            "Threshold",\
            #contour size
            "ContorMin","ContorMax",\
            #DilateKsize
            "DilateKsize"]
            #lower_color
valueRange=[[0,255],[0,255],[0,255],\
            #upper_color
            [30,255],[255,255],[255,255],\
            #threshold
            [0,255],\
            #contour size
            [60,1000],[1000,5000],
            #DilateKsize
            [3,15]]
#Flags
FirstFlag = False
UseCamFlag= True
#Flags
#parameter get
configFile = ".//Config//BallConfig.txt"
if FirstFlag is not True:
    paraGet    = Parameter(configFile=configFile)
    nameList,paraList = paraGet.ReadConfig()
    for i in range(len(paraList)):
        valueRange[i][0]=paraList[i]
#parameter get
#Trackbar 
trackbar = TrackBar("Parameter",(450,450))
trackbar.creatTrackbar(nameList,valueRange)
#Trackbar 
ret = False
originImg = None
cap = None
ball= None
if UseCamFlag is True:
    cap = cv2.VideoCapture(0)
    ret,originImg = cap.read()
else:
    originImg = cv2.imread(".\\vision\\picture\\redball.jpg")
    ret=True
if ret is True:
    img = cv2.resize(originImg,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    ball = FindBall(img,debugFlag = True)
else:
    print("can not open camera!")
    exit()
'''
parameterList:
lower_color:para[0:3]
upper_color:para[3:6]
threshold  :para[6]
ContorSize :para[7:9]
DilateKsize:para[9]
'''
while ret is True :
    cv2.imshow('ORIGIN', originImg)
    img = cv2.resize(originImg,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    cv2.imshow('resize', img)
    ball.updateImg(img)
    #get parameter
    para = trackbar.getTrackbarValue()
    #special process for blur size
    if para[7]%2 == 0:
        para[7]=para[7]+1
    #img process    
    ball.hsvFilter(tuple(para[0:3]),tuple(para[3:6]))
    ball.converToBinary(para[6])
    ball.getCenter(contoursRange=tuple(para[7:9]), ksize=(para[9],para[9]))
    ball.draw()
    #save or exit
    key = cv2.waitKey(1)
    if key == 27:
        break
    if key == ord('s'):
        paraSave = Parameter(para,nameList,configFile)
        paraSave.WriteConfig()
        print "Save Parameter Done!"
    #get image
    if UseCamFlag is True:
        ret,originImg = cap.read()
    else:
        originImg = cv2.imread(".\\vision\\picture\\redball.jpg")
        ret = True
    #get image
    #while ret is True end
cv2.destroyAllWindows()