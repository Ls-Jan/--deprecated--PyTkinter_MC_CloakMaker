import numpy as np
import cv2
import PIL.Image,PIL.ImageTk
from tkinter import *
from MyCanvas import *
from MyBlock import *

class PolarCoord:#极坐标
    def __init__(self,a,b,r):
        self.a=a#alpha
        self.b=b#belta
        self.r=r#radius

class My3DViewer:
    def __Drag(self):
        self.Camera.a-=self.myCanvas.mouse.OffsetX/250
        self.Camera.b-=self.myCanvas.mouse.OffsetY/250
        self.Work()
    def __Roll(self):
        self.Camera.r+=(5 if self.myCanvas.mouse.RollUp else -5)
        self.Work()
    def __init__(self,myCanvas):
        self.blockList=[]#方块列表
        self.myCanvas=myCanvas
        self.myCanvas.mouse.FuncDrag=self.__Drag
        self.myCanvas.mouse.FuncRoll=self.__Roll
        self.VSize=[int(self.myCanvas.canvas.config('width')[4]),int(self.myCanvas.canvas.config('height')[4])]
        
        self.Camera=PolarCoord(2,2,200)#摄像机/镜头/视野的极坐标(ρ,θ,r)
    def Work(self):#渲染图片
        VSizeHalf=(int(self.VSize[0]/2),int(self.VSize[1]/2))
        Img=np.zeros((self.VSize[0],self.VSize[1],3),np.uint8)
        for block in self.blockList:
            Img=cv2.add(Img,block.GetImg(self.Camera,self.VSize))
        Img = PIL.Image.fromarray(cv2.cvtColor(Img,cv2.COLOR_BGR2RGB))
        Img=PIL.ImageTk.PhotoImage(Img)
        self.myCanvas.canvas.create_image(VSizeHalf,image = Img)
        self.TkImg=Img#随便找个地方把Tk的图(即Img)存起来算了
    
    
    