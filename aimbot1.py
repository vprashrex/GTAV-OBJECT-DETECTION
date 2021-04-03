import cv2
import numpy as np

import numpy as np
from PIL import ImageGrab
import cv2
from time import time
import win32ui
import win32gui
import win32con
from d import detection


class WindowCapture:
    w = 0
    h = 0

    def __init__(self, windowName, w, h):
        self.windowName = windowName

        self.hwnd = win32gui.FindWindow(None, self.windowName)
        #window_rect = win32gui.GetWindowRect(self.hwnd)

        self.w = w
        self.h = h
        '''
        border_pixel = 8
        titlebar_pixel = 30
        self.w = self.w -(border_pixel*2)
        self.h = self.h - titlebar_pixel - border_pixel
        self.cropped_x = border_pixel
        self.cropped_y = titlebar_pixel
        
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y
        '''

    def take_screenshot(self):
        x = 60
        y = 60
        

        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (x,y), win32con.SRCCOPY)
        #dataBitMap.SaveBitmapFile(cDC, "foo.png")
        signedArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        img = img[..., :3]
        cx = (x+(self.w/2))
        cy = (y+(self.h/2))
        img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        #cv2.circle(img,(int(cx),int(cy)),4,(0,255,0),cv2.FILLED)
        
        return img
    


ptime = 0
ctime = 0

a = WindowCapture('prash',800,640)


wht = 320
loop_time = time()

cfg = 'yolov4-tiny.cfg'
weight = 'yolov4-tiny.weights'
label_path = 'coco.names'
b = detection(cfg, weight, 320,label_path)

while True:
    r = a.take_screenshot()
    b.detect(0.5, r)
    (H, W) = r.shape[:2]
    fps = 1/(time()-loop_time)
    cv2.putText(r, str(int(fps)), (0, 40),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    loop_time = time()
    cv2.imshow('frame', r)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break


cv2.destroyAllWindows()
