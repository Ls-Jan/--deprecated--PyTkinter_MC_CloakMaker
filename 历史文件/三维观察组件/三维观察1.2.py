from tkinter import *
from PIL import Image,ImageTk,ImageDraw
from math import cos,sin,tan
from numpy import matrix
import numpy as np
import cv2


class PolarCoord:#极坐标
    def __init__(self,a,b,r):
        self.a=a#alpha
        self.b=b#belta
        self.r=r#radius

class Mouse:
    def __init__(self):
        self.FuncDrag=None#拖拽时调用的函数，无参
        self.FuncRoll=None#滚动时调用的函数，无参
        self.OffsetX=0#鼠标X位移
        self.OffsetY=0#鼠标Y位移
        self.RollUp=True#滚轮向上滚动
        self.__x=0
        self.__y=0
    def Click(self,Event):
        self.__x=Event.x
        self.__y=Event.y
    def Drag(self,Event):
        self.OffsetX=Event.x-self.__x
        self.OffsetY=Event.y-self.__y
        self.__x=Event.x
        self.__y=Event.y
        self.FuncDrag()
    def Roll(self,Event):
        if(Event.delta>0):
            self.RollUp=True
        else:
            self.RollUp=False
        self.FuncRoll()
        

class Interface:#界面，完成交互和显示工作
    instance=None
    blockList=[]#方块列表
    ViewSize=(750,750)#视窗大小
    def __new__(cls, *args, **kw):#单例类
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance
    def __init__(self):#blocks:Block列表
        def Drag():
            inst=Interface.instance
            inst.Camera.a+=inst.myMouse.OffsetX/250
            inst.Camera.b-=inst.myMouse.OffsetY/250
            print("【a:{},b:{}】".format(round(inst.Camera.a,2),round(inst.Camera.b,2)))
            inst.Work()
        def Roll():
            inst=Interface.instance
            inst.Camera.r+=(5 if inst.myMouse.RollUp else -5)
            print("【r:{}】".format(inst.Camera.r))
            inst.Work()
        self.myMouse=Mouse()
        self.myMouse.FuncDrag=lambda :Drag()
        self.myMouse.FuncRoll=lambda :Roll()
        self.tk=Tk()
        self.Camera=PolarCoord(2,2,200)#摄像机/镜头/视野的极坐标(ρ,θ,r)
        self.canvas=Canvas(self.tk,width=Interface.ViewSize[0],height=Interface.ViewSize[1],bg='white')#控件
        self.canvas.bind("<MouseWheel>",self.myMouse.Roll)#滚轮滚动
        self.canvas.bind("<Button-1>",self.myMouse.Click)#左键按下
        self.canvas.bind("<B1-Motion>",self.myMouse.Drag)#左键拖拽
        
        self.canvas.grid(row=0,column=0)
    def Work(self):#渲染图片
        VSize=Interface.ViewSize
        VSizeL=(int(VSize[0]/2),int(VSize[1]/2))
        Img=np.zeros((VSize[0],VSize[1],3),np.uint8)
        for block in self.blockList:
            Img=cv2.add(Img,block.GetImg(self.Camera))
        Img = Image.fromarray(cv2.cvtColor(Img,cv2.COLOR_BGR2RGB))
        Img=ImageTk.PhotoImage(Img)
        self.canvas.create_image(VSizeL,image = Img)
        self.TkImg=Img#随便找个地方把Tk的图(即Img)存起来算了

class Block:#方块
    SurfaceToPoints=[(0,1,2,3),(4,5,6,7),(7,6,1,0),(3,2,5,4),(7,0,3,4),(1,6,5,2)]#面点对应关系(还是带顺序的
    SurfacePoints=[0x0F,0xF0,0xC3,0x3C,0x99,0x66]#索引,方便判断哪个被隐盖的点所关联的面是不用显示的。用位判断(更快，更爽
    def __init__(self,points,imgs):
    #points为列表，是方块的八个顶点(三元元组)，分别是前面的四个顶点和后面的四个顶点，顺序为从左上角开始的逆时针
    #points:[左上(前),左下(前),右下(前),右上(前),左上(后),左下(后),右下(后),右上(后)]
    #imgs:为列表，是方块的六个面，最好就大小合理点，要不然会让方块不闭合或者方块某个面伸出。图片格式为cv2读取的图片
    #imgs:[前,后,左,右,上,下]
    #img:如果某个面不需要图那直接None
        self.points=[]
        for P in points:
            self.points.append(list(P)+[1])
        self.points=matrix(self.points)
        self.imgs=imgs
    def GetMatrix(Camera,ViewSize):#根据相机位置返回变换矩阵
        sinA=sin(Camera.a)
        sinB=sin(Camera.b)
        cosA=cos(Camera.a)
        cosB=cos(Camera.b)
        r=Camera.r

        Matrix=matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[r*cosA*cosB,r*sinA*cosB,r*sinB,1]])#投影中心移动到原点
        Matrix=Matrix*matrix([[cosA,-sinA,0,0],[sinA,cosA,0,0],[0,0,1,0],[0,0,0,1]])#绕z转动-a角度
        Matrix=Matrix*matrix([[sinB,0,cosB,0],[0,1,0,0],[-cosB,0,sinB,0],[0,0,0,1]])#绕y转动pi/2-b角度
        Matrix=Matrix*matrix([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])#绕z转动-pi/2角度
        
        d_CameraToView=20#镜头到观察面距离。观察面与前后截面的距离固定为0.8*d【这参数为啥发挥不了作用】
        Matrix=Matrix*matrix([[(10/9)/ViewSize[0],0,0,0],[0,(10/9)/ViewSize[1],0,0],[0,0,(5/9)/d_CameraToView,0],[0,0,0,1]])#比例变换变成规范化透视投影
        Matrix=Matrix*matrix([[1,0,0,0],[0,1,0,0],[0,0,2.5,1],[0,0,-1.5,0]])#变换成规范化平行投影
        return Matrix
    def GetImg(self,Camera):#转换图片，获取映射变化后的图片，格式仍为cv2(格式稍加转换就可打到canvas上显示
        VSize=Interface.ViewSize
        VSizeL=(int(VSize[0]/2),int(VSize[1]/2))
        TM=Block.GetMatrix(Camera,VSize)*100*Camera.r#转换矩阵(顺带把它给放大一下

        Points=[]#取出转换后的点
        for P in self.points*TM:
            Points.append((VSizeL[0]+P[(0,0)],VSizeL[1]+P[(0,1)],P[(0,2)]))#取出P的坐标
        nullP=[0]#被隐盖的点(必然有一个，但有可能有多个，所以用列表
        for pst in range(8):
            dist=Points[pst][2]-Points[nullP[0]][2]
            if dist==0:
                nullP.append(pst)
            elif dist<0:
                nullP=[pst]
        if(nullP.count(0)==2):#【经典翻车事故】
            nullP.remove(0)
        nullP.append(0)
        for pst in nullP[:-1]:#也是将它转换为位的方式，一样的理由———更快、更爽
            nullP[-1]+=(1<<pst)
        nullP=nullP[-1]
        
        targetImg=np.zeros((VSize[0],VSize[1],3),np.uint8)
        for pst in range(6):#逐个显示图片
            if(Block.SurfacePoints[pst]&nullP):#如果命中了就说明这个面有顶点是无效的，即这个面不需要显示
                continue
            if(type(self.imgs[pst]) is not np.ndarray):#如果是空的那就跳过本段
                continue
            args=self.imgs[pst].shape
            before=np.float32([[0,0],[0,args[0]],[args[1],args[0]]])
            after=[]
            for i in Block.SurfaceToPoints[pst][:3]:#取3个点就够了
                after.append([Points[i][0],Points[i][1]])
            after=np.float32(after)
            targetImg=cv2.add(targetImg,cv2.warpAffine(self.imgs[pst],cv2.getAffineTransform(before,after),VSize))#仿射变换，并将结果加入到targetImg中
        return targetImg

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


    

    block_1=Block([(-5,-1,8),(-5,-1,-8),(5,-1,-8),(5,-1,8),(5,0,8),(5,0,-8),(-5,0,-8),(-5,0,8)],[cv2.imread("Front.png"),cv2.imread("Back.png"),cv2.imread("White.png"),cv2.imread("White.png"),cv2.imread("White.png"),cv2.imread("White.png")])
    Interface.blockList=[block_1]

    viewer=Interface()
    viewer.Work()
    viewer.tk.mainloop()


Main()








