import cv2
import numpy
from FindObject import *
from DebugUI import TrackBar
#Trackbar Test
nameList = ['Hmin',"Smin","Vmin","Hmax","Smax","Vmax"]
valueRange=[(70,255),(70,255),(0,255),(255,255),(255,255),(255,255)]
trackbar = TrackBar("Track Test")
trackbar.creatTrackbar(nameList,valueRange)
barBinary = TrackBar("converToBinary") 
barBinary.creatTrackbar(['threshold:'],[(0,255)])
#Trackbar Test

img = cv2.imread(".\\Vision\\picture\\track4.jpg")
cv2.imshow('ORIGIN', img)
track = FindTrack(img,debugFlag = True)
while True :
    color = trackbar.getTrackbarValue()
    threshold = barBinary.getTrackbarValue()
    key = cv2.waitKey(1)
    track.hsvFilter(tuple(color[0:3]),tuple(color[3:]))
    track.converToBinary(threshold[0])
    track.getCenter(blurSize=15,minVal=100,maxVal=300,\
                    linePointCount=60,minLineLength=120,maxLineGap=10,\
                    slopeThreshold=math.tan(math.pi/6))
    track.draw()
    if key == 27:
        break
cv2.destroyAllWindows()