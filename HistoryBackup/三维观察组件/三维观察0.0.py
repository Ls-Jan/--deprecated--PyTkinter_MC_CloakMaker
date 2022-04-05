from tkinter import *
from PIL import Image,ImageTk

class Interface:#画板，或者说是视口
    tk=Tk()
    canvas=Canvas(tk,width=500,height=500,bg = 'white')
class Renderer:#渲染器，用于把图P上去的
    pointList=[(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)]#长方体的八个顶点坐标
    Img=[]#存放着6张待渲染图，对应的长方体的面依次为：前(0123)、后(4567)、左(0347)、右(1256)、上(2345)、下(0167)
    __TkImg=[]#存放着6张Tk专用图
    def Work(Camera):#Camera：摄像机/镜头/视野的极坐标(ρ,θ,r)
        pass
    

class Viewer:
    class Coord:
        pass
    instance=None
    def __new__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance
    def __init__(self):
        self.Mouse=Viewer.Coord#获取鼠标左键按下时的相对坐标，以此获取鼠标拖拽时的位移
        self.Camera=Viewer.Coord#摄像机/镜头/视野的极坐标(ρ,θ,r)
        self.Mouse.x=0
        self.Mouse.y=0
        self.Camera.a=0#alpha
        self.Camera.b=0#belta
        self.Camera.r=100
    def BtRoll(Event):#与世界中心的距离的拉进拉远
        if(Event.delta>0):
            Viewer.instance.Camera.r-=1
        else:
            Viewer.instance.Camera.r+=1
        print("r:{}".format(Viewer.instance.Camera.r))
    def BtDrag(Event):
        global Img    
        global TkImg
        global canvas2
        Viewer.instance.Camera.a-=(Event.x-Viewer.instance.Mouse.x)/500
        Viewer.instance.Camera.b-=(Event.y-Viewer.instance.Mouse.y)/500
        Viewer.instance.Mouse.x=Event.x
        Viewer.instance.Mouse.y=Event.y
        print("a:{},b:{}".format(round(Viewer.instance.Camera.a,2),round(Viewer.instance.Camera.b,2)))
#        Renderer.Work(Viewer.instance.Camera)
        TkImg=ImageTk.PhotoImage(Img)
        Interface.canvas.create_image((250,250),image = TkImg)

        

def Main():
    Front=Image.open("5.png")
    Back=Image.open("5.png")




viewer=Viewer

Img=Image.open("Test.png")
TkImg=ImageTk.PhotoImage(Img)

    
Interface.canvas.bind("<MouseWheel>",Viewer.BtRoll)#滚轮滚动
Interface.canvas.bind("<B1-Motion>",Viewer.BtDrag)#左键拖拽
Interface.canvas.create_image((250,250),image = TkImg)
Interface.canvas.grid(row=0,column=0)

Interface.tk.mainloop()





