import cv2
import numpy
from FindObject import *
from DebugUI import TrackBar
#Trackbar Test
nameList = ['Hmin',"Smin","Vmin","Hmax","Smax","Vmax"]
valueRange=[(0,255),(137,255),(0,255),(30,255),(255,255),(255,255)]
trackbar = TrackBar("Test")
trackbar.creatTrackbar(nameList,valueRange)
barBinary = TrackBar("converToBinary") 
barBinary.creatTrackbar(['threshold:'],[(0,255)])
#Trackbar Test
cap = cv2.VideoCapture(0)
ret,img = cap.read()
#img = cv2.imread(".\\vision\\picture\\redball.jpg")
#cv2.imshow('ORIGIN', img)
ball = FindBall(None)
if ret is True:
    ball = FindBall(img,debugFlag = True)
while ret is True :
    cv2.imshow('origin',img)
    ball.updateImg(img)
    color = trackbar.getTrackbarValue()
    threshold = barBinary.getTrackbarValue()
    key = cv2.waitKey(1)
    ball.hsvFilter(tuple(color[0:3]),tuple(color[3:]))
    ball.converToBinary(threshold[0])
    ball.dilate(ksize=(5,5))
    ball.getCenter()
    ball.draw()
    ret,img = cap.read()
    if key == 27:
        break
cv2.destroyAllWindows()