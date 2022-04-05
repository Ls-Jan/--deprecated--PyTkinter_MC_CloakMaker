from tkinter import *

class Mouse:
    def __init__(self):
        self.FuncRoll=None#中键滚动时调用的函数，无参
        self.FuncDrag=None#左键拖拽
        self.FuncRelease=None#左键释放
        self.FuncClick=None#左键按下
        self.FuncRightClick=None#右键按下
        self.OffsetX=0#鼠标X位移
        self.OffsetY=0#鼠标Y位移
        self.RollUp=True#滚轮向上滚动
        self.X=0
        self.Y=0
        self.RootX=0
        self.RootY=0
    def __GetOppositeCoord(self,Event):
        return (Event.x_root-self.RootX,Event.y_root-self.RootY)
    def Click(self,Event):
        self.X,self.Y=self.__GetOppositeCoord(Event)
        if(self.FuncClick):
            self.FuncClick()
    def Drag(self,Event):
        oldX,oldY=self.X,self.Y
        self.X,self.Y=self.__GetOppositeCoord(Event)
        self.OffsetX,self.OffsetY=self.X-oldX,self.Y-oldY
        if(self.FuncDrag):
            self.FuncDrag()
    def Release(self,Event):
        self.X,self.Y=self.__GetOppositeCoord(Event)
        if(self.FuncRelease):
            self.FuncRelease()
    def RightClick(self,Event):
        self.X,self.Y=self.__GetOppositeCoord(Event)
        if(self.FuncRightClick):
            self.FuncRightClick()
    def Roll(self,Event):
        if(Event.delta>0):
            self.RollUp=True
        else:
            self.RollUp=False
        if(self.FuncRoll):
            self.FuncRoll()
      
class MyCanvas:
    def __init__(self,root,size=(0,0),color='green',cursorType=None):
        self.canvas=Canvas(root,width=size[0],height=size[1],cursor=cursorType,bg=color,bd=3,relief=RIDGE)
        self.mouse=Mouse()
        self.canvas.bind("<Button-1>",self.mouse.Click)#左键按下
        self.canvas.bind("<B1-Motion>",self.mouse.Drag)#左键拖拽
        self.canvas.bind("<ButtonRelease-1>",self.mouse.Release)#左键释放
        self.canvas.bind("<Button-3>",self.mouse.RightClick)#右键按下/点击
        self.canvas.bind("<MouseWheel>",self.mouse.Roll)#中键滚动
    def SetRootCoord(self,rootX,rootY):
        self.mouse.RootX,self.mouse.RootY=rootX,rootY

class CheckedRect:#选中的方框
    TypeForInit={
        'UL':lambda self,root:(exec("self.UL=MyCanvas(root,cursorType='crosshair')")),
        'UR':lambda self,root:(exec("self.UR=MyCanvas(root,cursorType='crosshair')")),
        'DL':lambda self,root:(exec("self.DL=MyCanvas(root,cursorType='crosshair')")),
        'DR':lambda self,root:(exec("self.DR=MyCanvas(root,cursorType='crosshair')"))}
    TypeForPlace={
        'UL':lambda self,coord0,coord1:self.UL.canvas.place(x=coord0[0]-4,y=coord0[1]-4),
        'UR':lambda self,coord0,coord1:self.UR.canvas.place(x=coord1[0]-4,y=coord0[1]-4),
        'DL':lambda self,coord0,coord1:self.DL.canvas.place(x=coord0[0]-4,y=coord1[1]-4),
        'DR':lambda self,coord0,coord1:self.DR.canvas.place(x=coord1[0]-4,y=coord1[1]-4)}
    def __init__(self,myCanvas):
        self.coord0=[0,0]#选中的左上角
        self.coord1=[0,0]#选中的右下角
        self.myCanvas=myCanvas
        for key in CheckedRect.TypeForInit:
            CheckedRect.TypeForInit[key](self,myCanvas.canvas.master)
            mouse=eval('self.{}.mouse'.format(key))
            mouse.FuncDrag=self.__DragOnWidget(key)
        myCanvas.mouse.FuncDrag=self.__DragOnCanvas
        myCanvas.mouse.FuncRightClick=self.__ClearRect
        myCanvas.mouse.FuncClick=self.__SetCoord0
    def __DragOnWidget(self,type):#把函数闭包用在这妖魔的地方里，不合适。。(但没想到更合适的方法
        mouse=eval('self.{}.mouse'.format(type))
        canvas=self.myCanvas.canvas
        if(type=="UL"):
            def Func():
                X,Y=self.__LimitCoord([self.coord1[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord0[1]=X,Y
                self.__DrawRect()
            return Func
        elif(type=="UR"):
            def Func():
                X,Y=self.__LimitCoord([self.coord0[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord0[1]=X,Y
                self.__DrawRect()
            return Func
        elif(type=="DL"):
            def Func():
                X,Y=self.__LimitCoord([self.coord1[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord1[1]=X,Y
                self.__DrawRect()
            return Func
        elif(type=="DR"):
            def Func():
                X,Y=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord1[1]=X,Y
                self.__DrawRect()
            return Func
    def __DragOnCanvas(self):
        mouse=self.myCanvas.mouse
        X,Y=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
        self.coord1=[X,Y]
        self.__DrawRect()
    def __DrawRect(self):#画矩形
        canvas=self.myCanvas.canvas
        canvas.delete('rect')
        canvas.create_rectangle(self.coord0[0],self.coord0[1],self.coord1[0],self.coord1[1],outline='red',tags='rect')
        rootCoord=(canvas.winfo_x(),canvas.winfo_y())
        absCoord0=(self.coord0[0]+rootCoord[0],self.coord0[1]+rootCoord[1])
        absCoord1=(self.coord1[0]+rootCoord[0],self.coord1[1]+rootCoord[1])
        for key in CheckedRect.TypeForPlace:
            CheckedRect.TypeForPlace[key](self,absCoord0,absCoord1)
    def __ClearRect(self):
        self.myCanvas.canvas.delete('rect')
        for key in CheckedRect.TypeForInit:
            exec("self.{}.canvas.place_forget()".format(key))
    def __SetCoord0(self):
        self.coord0=[self.myCanvas.mouse.X,self.myCanvas.mouse.Y]
    def __LimitCoord(self,rootCoord,moveCoord):#将坐标值规范化使其约束于画布内并且宽高比为定值
        unitW=10
        unitH=16
        canvas=self.myCanvas.canvas
        width=canvas.winfo_width()-4
        height=canvas.winfo_height()-4
        rootCoord=list(rootCoord)
        moveCoord=list(moveCoord)

        if moveCoord[0]<0:
            moveCoord[0]=0 
        if moveCoord[1]<0:
            moveCoord[1]=0 
        if moveCoord[0]>width:
            moveCoord[0]=width
        if moveCoord[1]>height:
            moveCoord[1]=height
        unit1=(moveCoord[0]-rootCoord[0])/unitW
        unit2=(moveCoord[1]-rootCoord[1])/unitH
        if(abs(unit1)<abs(unit2)):
            unit2=abs(unit1) if unit2>0 else -abs(unit1)
        else:
            unit1=abs(unit2) if unit1>0 else -abs(unit2)
        X=rootCoord[0]+unitW*unit1
        Y=rootCoord[1]+unitH*unit2
        if(X>width or Y>height):
            X-=unitW
            Y-=unitH
        if(X<0 or Y<0):
            X+=unitW
            Y+=unitH
        return X,Y
    def SetRootCoord(self):
        tk.update()
        rootX,rootY=self.myCanvas.canvas.winfo_rootx(),self.myCanvas.canvas.winfo_rooty()    
        self.myCanvas.SetRootCoord(rootX,rootY)
        for key in CheckedRect.TypeForInit:
            exec("self.{}.SetRootCoord(rootX,rootY)".format(key))
    def RedrawRect(self):
        self.__DrawRect()
    def ClearRect(self):
        self.__ClearRect()
tk=Tk()
tk.geometry('600x600')
cv=MyCanvas(tk,(351,351),'grey')
cv.canvas.place(x=30,y=30)
cr=CheckedRect(cv)
tk.bind("<Configure>",lambda Event:cr.SetRootCoord())
tk.mainloop()














