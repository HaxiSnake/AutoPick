import cv2
import numpy
import os
import sys
#workdir = "G:\\AutoPickRobot\\AutoPick"
#workdir = "E:\\WORKSPACE\\2_Haobbys\\AutoPickRobot\\AutoPick"
workdir  = "/home/pi/SpeedUp"
#configFile = ".\\Config\\TrackConfig.txt"
configFile = "./Config/SpeedConfig.txt"
os.chdir(workdir)
sys.path.append(os.getcwd())
from Vision.FindObject import * 
from Vision.DebugUI import *
from Tools.ParaSave import *
#Flags
FirstFlag = False
UseCamFlag= True
CAMID = 0

#Flags
#paraList
            #lower_color
nameList = ['Hmin',"Smin","Vmin",\
            #upper_color
            "Hmax","Smax","Vmax",\
            #threshold
            "Threshold",\
            #blurKsize
            "BlurSize",\
            #CannyRange
            "CannyRang",\
            #linePointCout
            "LinePointCount",\
            #minLineLength
            "MinLineLength",\
            #maxLineGap
            "maxLineGap"]
            #lower_color
valueRange=[[70,255],[70,255],[0,255],\
            #upper_color
            [255,255],[255,255],[255,255],\
            #threshold
            [0,255],\
            ##blurKsize //muste be odd and greater than 1
            [15,33],\
            #CannyRange
            [100,500],\
            #linePointCount
            [60,500],\
            #minLineLength
            [120,500],\
            #maxLineGap
            [10,500]]
#paraList

#parameter get
if FirstFlag is not True:
    paraGet    = Parameter(configFile=configFile)
    nameList,paraList = paraGet.ReadConfig()
    for i in range(len(paraList)):
        valueRange[i][0]=paraList[i]
#parameter get
#special process for blur size
if valueRange[7][0]%2 == 0:
    valueRange[7][0]=valueRange[7][0]+1
#Trackbar 
trackbar = TrackBar("Parameter",(300,50))
trackbar.creatTrackbar(nameList,valueRange)
#Trackbar 
ret = False
originImg = None
img = None
cap = None
track = None
debugShow = None
if UseCamFlag is True:
    cap = cv2.VideoCapture(CAMID)
    ret,originImg = cap.read()
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH,180)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
else:
    originImg = cv2.imread(".\\vision\\picture\\track5.jpg")
    ret = True
if ret is True:
    img = cv2.resize(originImg,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    track = FindTrack(img,debugFlag = False)
    debugShow = TrackShow(track)
else :
    print("can not open camera!")
    exit()
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
while ret is True :
    #cv2.imshow('ORIGIN', originImg)
    img = cv2.resize(originImg,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
    #cv2.imshow('origin', img)
    track.updateImg(img)
    #get parameter
    para = trackbar.getTrackbarValue()
    #special process for blur size
    if para[7]%2 == 0:
        para[7]=para[7]+1
    #img process
    track.hsvFilter(tuple(para[0:3]),tuple(para[3:6]))
    track.converToBinary(para[6])
    track.getCenter(blurSize=para[7],minVal=para[8],maxVal=para[8]*3,\
                    linePointCount=para[9],minLineLength=para[10],maxLineGap=para[11],\
                    slopeThreshold=math.tan(math.pi/6))
    track.draw()
    #img process
    #save or exit
    key = cv2.waitKey(1)
    if key == 27:
        break
    if key == ord('s'):
        paraSave = Parameter(para,nameList,configFile)
        paraSave.WriteConfig()
        print "Save Parameter Done!"
    else:
        debugShow.switchWindow(key)
        #q:hsv
        #w:binary
        #e:blurt
        #r:edge
    debugShow.showImg()
    #save or exit
    #get image
    if UseCamFlag is True:
        ret,originImg = cap.read()
    else:
        originImg = cv2.imread(".\\vision\\picture\\track5.jpg")
        ret = True
    #get image
    #while ret is True end
cv2.destroyAllWindows()
