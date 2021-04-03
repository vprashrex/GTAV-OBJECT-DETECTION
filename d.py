import cv2
import numpy as np
from time import time
from direct_key import PressKey, ReleaseKey, X
import pyautogui as pag
import win32api
import win32con

class detection:
    
    pag.FAILSAFE = False
    
    def __init__(self,cfg,weight,wht,label_path):
        self.cfg = cfg 
        self.weight = weight
        self.wht = wht
        self.label_path = label_path
        self.label = open(self.label_path).read().split('\n')
        
        self.net = cv2.dnn.readNetFromDarknet(self.cfg,self.weight)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        
        self.layername = self.net.getLayerNames()
        self.outputname = [self.layername[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        
    
    


    def click(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)



    
    def detect(self,conf_thresh,img):
        self.current_key_pressed = set()
        self.key_pressed = False
        self.conf_thresh = conf_thresh
        self.img = img
        (H,W) = self.img.shape[:2]
        blob = cv2.dnn.blobFromImage(img,1/255.0,(self.wht,self.wht),swapRB=True,crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.outputname)
        
        boxes = []
        classIDs = []
        confidences = []
        
        for output in outputs:
            for bb in output:
                scores = bb[5:]
                classid = np.argmax(scores)
                conf = scores[classid]
                
                if conf>conf_thresh:
                    box = bb[0:4] * np.array([W,H,W,H])
                    (cx,cy,width,height) = box.astype('int')
                    
                    x = int(cx - (width/2))
                    y = int(cy - (height/2))
                    
                    boxes.append([x,y,int(width),int(height)])
                    confidences.append(float(conf))
                    classIDs.append(classid)
                    
        
        idxs = cv2.dnn.NMSBoxes(boxes,confidences,conf_thresh,0.3)
        
        if len(idxs)>0:
            for i in idxs.flatten():
                (x,y) = (boxes[i][0],boxes[i][1])
                (w,h) = (boxes[i][2],boxes[i][3])
                if len(self.label[classIDs[i]])==6:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    px = int(x+(w/2.0))
                    py = int(y+(h/2.0))
                    cv2.circle(img,(int(px),int(py)),4,(0,255,0),cv2.FILLED)
                    center = (px,py)
                    pag.moveTo(px,py)
                    PressKey(X)
                    self.current_key_pressed.add(X)
                    self.key_pressed = True
                else:
                    ReleaseKey(X)
                    
                    
                    
        
        return img



