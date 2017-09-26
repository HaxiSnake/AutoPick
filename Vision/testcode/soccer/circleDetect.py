import cv2
import numpy 

#img = cv2.imread('E://WORKSPACE//2_Haobbys//AutoPick//Vision//picture//redball.jpg')
img = cv2.imread('E://WORKSPACE//2_Haobbys//AutoPick//Vision//testcode//soccer//01.jpeg')
cv2.imshow('origin',img)
#img = cv2.medianBlur(img,3)
cimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, 1, 5,param1=30, param2=30, minRadius=0, maxRadius=100)

circles = numpy.uint16(numpy.around(circles))
for i in circles[0, :]:
    # draw the outer circle
    cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # draw the center of the circle
    cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)

cv2.imshow('detected circles', cimg)
cv2.waitKey(0)
cv2.destroyAllWindows()
