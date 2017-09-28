import cv2
import numpy
import os
import sys
os.chdir("G:\\AutoPick")
sys.path.append(os.getcwd())
from Vision.FindObject import * 
from Vision.DebugUI import *
from Tools.ParaSave import *
#Trackbar 
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

#parameter get
configFile = ".//Config//BallConfig.txt"
paraGet    = Parameter(configFile=configFile)
nameList,paraList = paraGet.ReadConfig()
for i in range(len(paraList)):
    valueRange[i][0]=paraList[i]
#parameter get

trackbar = TrackBar("Parameter",(450,450))
trackbar.creatTrackbar(nameList,valueRange)
#Trackbar 


originImg = cv2.imread(".\\vision\\picture\\redball.jpg")
cv2.imshow('ORIGIN', originImg)
img = cv2.resize(originImg,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
cv2.imshow('resize', img)
ball = FindBall(img,debugFlag = True)
'''
parameterList:
lower_color:para[0:3]
upper_color:para[3:6]
threshold  :para[6]
ContorSize :para[7:9]
DilateKsize:para[9]
'''
while True :
    para = trackbar.getTrackbarValue()
    key = cv2.waitKey(1)
    ball.hsvFilter(tuple(para[0:3]),tuple(para[3:6]))
    ball.converToBinary(para[6])
    ball.getCenter(contoursRange=tuple(para[7:9]), ksize=(para[9],para[9]))
    ball.draw()
    if key == 27:
        break
    if key == ord('s'):
        paraSave = Parameter(para,nameList,configFile)
        paraSave.WriteConfig()
        print "Save Parameter Done!"
cv2.destroyAllWindows()