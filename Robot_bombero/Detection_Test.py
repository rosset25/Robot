from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

from candle import candle

camera = PiCamera()
rawCapture = PiRGBArray(camera)
time.sleep(1.0)
camera.capture(rawCapture, format="bgr")
img = rawCapture.array

c = candle(img)
if c is None:
    print('No candle found in image')
else:
    x, y, w, h = c
    print('Candle: (x,y)=(%d,%d), w=%d, h=%d ' % (x,y+250,w,h))
    cv2.rectangle(img, (x-w/2,y+250-h/2), (x+w/2,y+250+h/2), (0,255,255), 2)
    
cv2.imwrite("snapshot.png",img)
