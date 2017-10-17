import cv2
import numpy
import time
import findBall


def nothing(x):
    #function for trackbar useless in this script
    pass


WindowName = 'ColorSelect'
cv2.namedWindow(WindowName)
cv2.resizeWindow(WindowName, 1400, 800)
findBall.creatTrackbar(WindowName, nothing)
while 1:
    decimg = cv2.imread(".\\picture\\redball.jpg")
    cv2.imshow('IMG', decimg)
    parameter = findBall.getTrackbarValue(WindowName)
    findBall.findBall(decimg, parameter)
    key = cv2.waitKey(1)
    if key == 27:
        break
    if key == ord("s"):
        cv2.imwrite('test' + str(time.time()) + '.jpg', decimg)
    #image process
cv2.destroyAllWindows()
