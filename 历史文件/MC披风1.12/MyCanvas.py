from tkinter import *
from MyMouse import *

class MyCanvas:
    def __init__(self,root,size=(0,0),color='green',bdWidth=3,cursorType=None):
        self.canvas=Canvas(root,width=size[0],height=size[1],cursor=cursorType,bg=color,bd=bdWidth,relief=RIDGE)
        self.mouse=MyMouse()
        self.canvas.bind("<Button-1>",self.mouse.Click)#左键按下
        self.canvas.bind("<B1-Motion>",self.mouse.Drag)#左键拖拽
        self.canvas.bind("<ButtonRelease-1>",self.mouse.Release)#左键释放
        self.canvas.bind("<Double-Button-1>",self.mouse.DoubleClick)#左键双击
        self.canvas.bind("<Button-3>",self.mouse.RightClick)#右键按下
        self.canvas.bind("<Double-Button-3>",self.mouse.DoubleRightClick)#右键双击
        self.canvas.bind("<B3-Motion>",self.mouse.RightDrag)#右键拖拽
        self.canvas.bind("<MouseWheel>",self.mouse.Roll)#中键滚动
    def SetRootCoord(self,rootX,rootY):
        self.mouse.RootX,self.mouse.RootY=rootX,rootY
