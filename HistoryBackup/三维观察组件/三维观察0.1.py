from tkinter import *
from PIL import Image,ImageTk
from math import cos,sin,tan
from numpy import matrix

class Coord:
    def __init__(self,args1=0,args2=0,args3=0,PolarCoord=False):
        if(PolarCoord):
            self.a=args1#alpha
            self.b=args2#belta
            self.r=args3#radius
        else:
            self.x=args1
            self.y=args2
            self.z=args3
class Interface:#画板，或者说是视口
    tk=Tk()
    canvas=Canvas(tk,width=500,height=500,bg = 'white')
    Img=[]#存放着6张待渲染图，对应的长方体的面依次为：前(0123)、后(4567)、上(2345)、下(0167)、左(0347)、右(1256)
class Renderer:#渲染器，用于把图P上去
    pointMatrix=matrix([[-1,-1,-1,1],[-1,-1,1,1],[-1,1,-1,1],[-1,1,1,1],[1,-1,-1,1],[1,-1,1,1],[1,1,-1,1],[1,1,1,1]])#长方体的八个顶点坐标
    def __init__(self):
        Img=[]#存放着6张待渲染图，对应的长方体的面依次为：前(0123)、后(4567)、上(2345)、下(0167)、左(0347)、右(1256)
        __TkImg=[]#存放着6张Tk专用图    
    def Work(self,Camera,ViewSize):#Camera：摄像机/镜头/视野的极坐标(ρ,θ,r);ViewSize：观察窗口大小(Sx,Sy)
        TotalMatrix=matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        
        sinA=sin(Camera.a)
        sinB=sin(Camera.b)
        cosA=cos(Camera.a)
        cosB=cos(Camera.b)
        r=Camera.r
        TotalMatrix=TotalMatrix*matrix([[100*r,0,0,0],[0,100*r,0,0],[0,0,100*r,0],[r*cosA*cosB,r*sinA*cosB,r*sinB,1]])#投影中心移动到原点
        TotalMatrix=TotalMatrix*matrix([[cosA,-sinA,0,0],[sinA,cosA,0,0],[0,0,1,0],[0,0,0,1]])#绕z转动-a角度
        TotalMatrix=TotalMatrix*matrix([[sinB,0,cosB,0],[0,1,0,0],[-cosB,0,sinB,0],[0,0,0,1]])#绕y转动pi/2-b角度
        
        d_CameraToView=r/2#镜头到观察面距离。观察面与前后截面的距离固定为0.8*d
        TotalMatrix=TotalMatrix*matrix([[(10/9)/ViewSize[0],0,0,0],[0,(10/9)/ViewSize[1],0,0],[0,0,(5/9)/d_CameraToView,0],[0,0,0,1]])#比例变换变成规范化透视投影
        TotalMatrix=TotalMatrix*matrix([[1,0,0,0],[0,1,0,0],[0,0,2.5,0],[0,0,-1.5,0]])#变换成规范化平行投影
        
        resultMatrix=self.pointMatrix*TotalMatrix#八个顶点在映射变换(舍去三维空间裁剪的步骤
        resultPoints=[]
        ViewZ=-1 if (cosB>0 or (cosB==0 and sinB>0)) else 1#确定观察窗口的z坐标，以此为标准舍弃部分的点
        for P in resultMatrix:
            resultPoints.append((P[(0,0)],P[(0,1)],P[(0,2)]))#取出P的三个坐标
        
        print(resultMatrix)
        IsInSection=lambda x,tup:(tup[0]-x)*(tup[1]-x)<=0
        self.Img=Image.new(mode='RGB',size=ViewSize)
        ViewSize=(ViewSize[0]/2,ViewSize[1]/2)
        for P in resultPoints:
            left=P[0]-4
            up=P[1]-4
            for i in range(0,2):
                if(IsInSection(left+i,(-ViewSize[0],ViewSize[0]))):
                    for j in range(0,2):
                        if(IsInSection(up+j,(-ViewSize[1],ViewSize[1]))):
#                            print("【{},{}】".format(round(ViewSize[0]+left+i),round(ViewSize[1]+up+j)))
                            self.Img.putpixel((round(ViewSize[0]+left+i),round(ViewSize[1]+up+j)),(255,255,255))
        print("MMM")
        self.__TkImg=ImageTk.PhotoImage(self.Img)
        Interface.canvas.create_image((round(ViewSize[0]),round(ViewSize[1])),image = self.__TkImg)
        
    
class Viewer:
    renderer=Renderer()
    instance=None
    def __new__(cls, *args, **kw):        
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance
    def __init__(self):
        self.Mouse=Coord(0,0,0,False)#获取鼠标左键按下时的相对坐标，以此获取鼠标拖拽时的位移
        self.Camera=Coord(0,0,100,True)#摄像机/镜头/视野的极坐标(ρ,θ,r)
    def BtClick(Event):#鼠标刚准备拖动时记录坐标
        Viewer.instance.Mouse.x=Event.x
        Viewer.instance.Mouse.y=Event.y        
    def BtRoll(Event):#与世界中心的距离的拉进拉远
        if Viewer.instance==None:
            return
        if(Event.delta>0):
            Viewer.instance.Camera.r+=10
        else:
            Viewer.instance.Camera.r-=10
        print("【r:{}】".format(Viewer.instance.Camera.r))
        Viewer.renderer.Work(Viewer.instance.Camera,(500,500))
    def BtDrag(Event):
        if Viewer.instance==None:
            return
        global Img    
        global TkImg
        global canvas2
        Viewer.instance.Camera.a-=(Event.y-Viewer.instance.Mouse.y)/250
        Viewer.instance.Camera.b-=(Event.x-Viewer.instance.Mouse.x)/250
        Viewer.instance.Mouse.x=Event.x
        Viewer.instance.Mouse.y=Event.y
        print("【a:{},b:{}】".format(round(Viewer.instance.Camera.a,2),round(Viewer.instance.Camera.b,2)))
        Viewer.renderer.Work(Viewer.instance.Camera,(500,500))

        

def Main():
  #  Front=Image.open("5.png")#披风正面
  #  Back=Image.open("3.png")#披风背面
  #  ColorU=(255,0,0)#上位置颜色
  #  ColorD=(0,255,0)#下位置颜色
  #  ColorL=(0,0,255)#左位置颜色
  #  ColorR=(255,255,0)#右位置颜色
  #  unit=10#单位长度
  #  Up=Image.new("RGB",(10*unit,unit),ColorU)#上位置
  #  Down=Image.new("RGB",(10*unit,unit),ColorD)#下位置
  #  Left=Image.new("RGB",(10*unit,unit),ColorL)#左位置
  #  Right=Image.new("RGB",(10*unit,unit),ColorR)#右位置


    viewer=Viewer()
    Interface.canvas.bind("<MouseWheel>",Viewer.BtRoll)#滚轮滚动
    Interface.canvas.bind("<Button-1>",Viewer.BtClick)#左键按下
    Interface.canvas.bind("<B1-Motion>",Viewer.BtDrag)#左键拖拽
    Interface.canvas.grid(row=0,column=0)
    Interface.tk.mainloop()

Main()

