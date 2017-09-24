import numpy
import cv2
cap = cv2.VideoCapture(0)
ret,img = cap.read()
while ret is True:
    cv2.imshow("Test",img)
    ret, img = cap.read()
    ch = cv2.waitKey(1)
    if ch == 27 :
        break
cv2.destroyAllWindows()
