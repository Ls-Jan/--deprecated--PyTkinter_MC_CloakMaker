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
    def __init__(self,root,size=(3,3),color='green',cursorType=None):
        self.canvas=Canvas(root,width=size[0],height=size[1],cursor=cursorType,bg=color)
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
        'DR':lambda self,root:(exec("self.DR=MyCanvas(root,cursorType='crosshair')")),
        'U':lambda self,root:(exec("self.U=MyCanvas(root,cursorType='sb_v_double_arrow')")),
        'D':lambda self,root:(exec("self.D=MyCanvas(root,cursorType='sb_v_double_arrow')")),
        'L':lambda self,root:(exec("self.L=MyCanvas(root,cursorType='sb_h_double_arrow')")),
        'R':lambda self,root:(exec("self.R=MyCanvas(root,cursorType='sb_h_double_arrow')"))}
    TypeForPlace={
        'UL':lambda self,coord0,coord1:self.UL.canvas.place(x=coord0[0]-3,y=coord0[1]-3),
        'UR':lambda self,coord0,coord1:self.UR.canvas.place(x=coord1[0]-3,y=coord0[1]-3),
        'DL':lambda self,coord0,coord1:self.DL.canvas.place(x=coord0[0]-3,y=coord1[1]-3),
        'DR':lambda self,coord0,coord1:self.DR.canvas.place(x=coord1[0]-3,y=coord1[1]-3),
        'U':lambda self,coord0,coord1:self.U.canvas.place(x=(coord0[0]+coord1[0])/2-3,y=coord0[1]-3),
        'D':lambda self,coord0,coord1:self.D.canvas.place(x=(coord0[0]+coord1[0])/2-3,y=coord1[1]-3),
        'L':lambda self,coord0,coord1:self.L.canvas.place(x=coord0[0]-3,y=(coord0[1]+coord1[1])/2-3),
        'R':lambda self,coord0,coord1:self.R.canvas.place(x=coord1[0]-3,y=(coord0[1]+coord1[1])/2-3)}
    def __DragWidget(self,type):#把函数闭包用在这妖魔的地方里，不合适。。(但没想到更合适的方法
        def Func():
            mouse=eval('self.{}.mouse'.format(type))
            if(type=="UL"):
                length=CheckedRect.__FormatLength((mouse.X,mouse.Y),(self.coord1[0],self.coord1[1]))
                self.coord0[0],self.coord0[1]=CheckedRect.__FormatCoord([self.coord1[0]-length[0],self.coord1[1]-length[1]])
            elif(type=="UR"):
                unit=CheckedRect.__FormatLength((self.coord0[0],mouse.Y),(mouse.X,self.coord1[1]))
                self.coord1[0]=mouse.X
                self.coord0[1]=mouse.Y
            elif(type=="DL"):
                unit=CheckedRect.__FormatLength((mouse.X,self.coord0[1]),(self.coord1[0],mouse.Y))
                self.coord0[0]=mouse.X
                self.coord1[1]=mouse.Y
            elif(type=="DR"):
                unit=CheckedRect.__FormatLength((self.coord0[0],self.coord0[1]),(mouse.X,mouse.Y))
                self.coord1[0]=mouse.X
                self.coord1[1]=mouse.Y
            elif(type=="U"):
                unit=CheckedRect.__FormatLength((self.coord0[0],mouse.Y),(self.coord1[0],self.coord1[1]))
                self.coord0[1]=mouse.Y
            elif(type=="D"):
                unit=CheckedRect.__FormatLength((self.coord0[0],self.coord0[1]),(self.coord1[0],mouse.Y))
                self.coord1[1]=mouse.Y
            elif(type=="L"):
                unit=CheckedRect.__FormatLength((mouse.X,self.coord0[0]),(self.coord1[0],self.coord1[1]))
                self.coord0[0]=mouse.X
            elif(type=="R"):
                unit=CheckedRect.__FormatLength((self.coord0[0],self.coord0[1]),(mouse.X,self.coord1[1]))
                self.coord1[0]=mouse.X
            self.__DrawRect()
        return Func
    def __init__(self,myCanvas):
        self.coord0=[0,0]#选中的左上角
        self.coord1=[0,0]#选中的右下角
        self.myCanvas=myCanvas
        for key in CheckedRect.TypeForInit:
            CheckedRect.TypeForInit[key](self,myCanvas.canvas.master)
            mouse=eval('self.{}.mouse'.format(key))
            mouse.FuncDrag=self.__DragWidget(key)
        myCanvas.mouse.FuncDrag=self.__Drag
        myCanvas.mouse.FuncRightClick=self.__RightClick
        myCanvas.mouse.FuncClick=self.__Click
    def __Drag(self):
        mouse=self.myCanvas.mouse
        mouse.X,mouse.Y=self.__FormatCoord([mouse.X,mouse.Y])
        self.coord1=[mouse.X,mouse.Y]
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
    def __RightClick(self):
        self.myCanvas.canvas.delete('rect')
        for key in CheckedRect.TypeForInit:
            exec("self.{}.canvas.place_forget()".format(key))
    def __Click(self):
        self.coord0=[self.myCanvas.mouse.X,self.myCanvas.mouse.Y]
    def SetRootCoord(self):
        tk.update()
        rootX,rootY=self.myCanvas.canvas.winfo_rootx(),self.myCanvas.canvas.winfo_rooty()    
        self.myCanvas.SetRootCoord(rootX,rootY)
        for key in CheckedRect.TypeForInit:
            exec("self.{}.SetRootCoord(rootX,rootY)".format(key))
    def __FormatCoord(self,coord):#对超过范围的坐标值进行修改，让其限定在主画布之内
        canvas=self.myCanvas.canvas
        if(coord[0]<0):
            coord[0]=0
        if(coord[1]<0):
            coord[1]=0
        if(coord[0]>canvas.winfo_width()):
            coord[0]=canvas.winfo_width()
        if(coord[1]>canvas.winfo_height()):
            coord[1]=canvas.winfo_height()
        return coord
    def __FormatLength(Coord1,Coord2):#获取格式化的长度(长宽比为10:16)
        unit1=(Coord2[0]-Coord1[0])/10
        unit2=(Coord2[1]-Coord1[1])/16
        return (10*unit1,16*unit1) if unit1<unit2 else (10*unit2,16*unit2)
        
tk=Tk()
cv=MyCanvas(tk,(500,500),'grey')
cv.canvas.place(x=30,y=30)
cr=CheckedRect(cv)
tk.bind("<Configure>",lambda Event:cr.SetRootCoord())
tk.mainloop()





