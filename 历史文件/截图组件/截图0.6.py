from tkinter import *
from PIL import Image,ImageTk

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
    def __init__(self,root,size=(0,0),color='green',bdWidth=3,cursorType=None):
        self.canvas=Canvas(root,width=size[0],height=size[1],cursor=cursorType,bg=color,bd=bdWidth,relief=RIDGE)
        self.mouse=Mouse()
        self.canvas.bind("<Button-1>",self.mouse.Click)#左键按下
        self.canvas.bind("<B1-Motion>",self.mouse.Drag)#左键拖拽
        self.canvas.bind("<ButtonRelease-1>",self.mouse.Release)#左键释放
        self.canvas.bind("<Button-3>",self.mouse.RightClick)#右键按下/点击
        self.canvas.bind("<MouseWheel>",self.mouse.Roll)#中键滚动
    def SetRootCoord(self,rootX,rootY):
        self.mouse.RootX,self.mouse.RootY=rootX,rootY

class CheckedRect:#选中的方框（内容耦合的庞大怪物，代码质量很差，
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
    def __init__(self,bgCanvas):
        self.coord0=[0,0]#选中的左上角(逻辑坐标。至于我为什么要说是逻辑坐标，就看看我对self.bdWidth这个变量赋值时的注释就知道是怎么回事了
        self.coord1=[0,0]#选中的右下角(逻辑坐标
        self.bgCanvas=bgCanvas#底图
        self.boxWidth=int(bgCanvas.canvas.config('width')[4])#窗口大小(宽
        self.boxHeight=int(bgCanvas.canvas.config('height')[4])#窗口大小(高
        for key in CheckedRect.TypeForInit:
            CheckedRect.TypeForInit[key](self,bgCanvas.canvas.master)
            mouse=eval('self.{}.mouse'.format(key))
            mouse.FuncDrag=self.__DragOnWidget(key)
        bgCanvas.mouse.FuncDrag=self.__DragOnBgCanvas
        bgCanvas.mouse.FuncRightClick=self.__ClearRect
        bgCanvas.mouse.FuncClick=self.__SetCoord0
        self.img=Image.new(size=(self.boxWidth,self.boxHeight),mode="RGBA",color=bgCanvas.canvas.config('bg')[4])#待裁剪图片，默认图片底色
        self.unitW=0
        self.unitH=0
        self.bdWidth=2+int(bgCanvas.canvas.config('bd')[4])#非常弱智，非常弱智，简直就是，只能说，nb，艹，傻逼玩意儿
        #获得的组件宽度是组件的整体开算的，而我这画布组件只关心绘画区，这导致了我图片以及画的矩形发生了偏移
        #真是神仙，画布组件无论怎么设置参数，总会有两个像素宽度的白色框在这组件的最外面，怎么都关不掉的，而且颜色也没办法更改，真是服了
        #它绘图是以组件的根坐标进行绘制的，不是根据绘画区的根坐标开始的，傻逼，简直就是傻逼，真是垃圾玩意儿，哪个脑瘫这么设计的，绘图谁会关心边框的
        #马德我愿称这弱智为神人，平添我开发难度
        self.scaleMultiple=1#缩放倍数
        self.scaleCenter=[self.boxWidth/2,self.boxHeight/2]#缩放中心
        self.fgCanvas=MyCanvas(bgCanvas.canvas,color=bgCanvas.canvas.config('bg')[4],bdWidth=0)#顶图
        self.__DrawBg()
    def __DragOnWidget(self,type):#把函数闭包用在这妖魔的地方里，不合适。。(但没想到更合适的方法
        mouse=eval('self.{}.mouse'.format(type))
        canvas=self.bgCanvas.canvas
        if(type=="UL"):
            def Func():
                X,Y=self.__LimitCoord([self.coord1[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord0[1]=X,Y
                self.__DrawFg()
                self.__DrawRect()
            return Func
        elif(type=="UR"):
            def Func():
                X,Y=self.__LimitCoord([self.coord0[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord0[1]=X,Y
                self.__DrawFg()
                self.__DrawRect()
            return Func
        elif(type=="DL"):
            def Func():
                X,Y=self.__LimitCoord([self.coord1[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord1[1]=X,Y
                self.__DrawFg()
                self.__DrawRect()
            return Func
        elif(type=="DR"):
            def Func():
                X,Y=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord1[1]=X,Y
                self.__DrawFg()
                self.__DrawRect()
            return Func
    def __DragOnBgCanvas(self):
        mouse=self.bgCanvas.mouse
        X,Y=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
        self.coord1=[X,Y]
        self.__DrawFg()
        self.__DrawRect()
    def __ClearRect(self):#清掉画布
        self.bgCanvas.canvas.delete('rect')
        for key in CheckedRect.TypeForInit:
            exec("self.{}.canvas.place_forget()".format(key))
    def __SetCoord0(self):#用于左键拖拽主画布(底图)时设置第一个坐标Coord0
        self.coord0=[self.bgCanvas.mouse.X,self.bgCanvas.mouse.Y]
    def __LimitCoord(self,rootCoord,moveCoord):#将坐标值规范化使其约束于画布内并且宽高比为定值
        unitW=self.unitW
        unitH=self.unitH
        canvas=self.bgCanvas.canvas
        width=int(canvas.config('width')[4])-1
        height=int(canvas.config('height')[4])-1
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
        if(unitW==0 or unitH==0):
            return moveCoord
        unit1=(moveCoord[0]-rootCoord[0])/unitW
        unit2=(moveCoord[1]-rootCoord[1])/unitH
        if(abs(unit1)<abs(unit2)):
            unit2=abs(unit1) if unit2>0 else -abs(unit1)
        else:
            unit1=abs(unit2) if unit1>0 else -abs(unit2)
        X=rootCoord[0]+unitW*unit1
        Y=rootCoord[1]+unitH*unit2
        if(X<0 or Y<0):
            X+=unitW
            Y+=unitH
        if(X>width or Y>height):
            X-=unitW
            Y-=unitH
        return X,Y

    def __ScaleImg(self):#对图片进行缩放
        if(self.bgCanvas.mouse.RollUp):
            self.scaleMultiple-=0.1
        else:
            self.scaleMultiple+=0.1
        self.__DrawBg()
        self.__DrawFg()
        self.__DrawRect()
    def __DragScaleCenter(self):#移动图片的缩放中心
        self.scaleCenter[0]-=self.bgCanvas.mouse.OffsetX
        self.scaleCenter[1]-=self.bgCanvas.mouse.OffsetY
        self.__DrawBg()
        self.__DrawFg()
        self.__DrawRect()
    def __DrawRect(self):#画矩形
        canvas=self.bgCanvas.canvas
        canvas.delete('rect')
        canvas.create_rectangle(self.coord0[0]+self.bdWidth,self.coord0[1]+self.bdWidth,self.coord1[0]+self.bdWidth,self.coord1[1]+self.bdWidth,outline='red',tags='rect')
        rootCoord=(canvas.winfo_x()+self.bdWidth,canvas.winfo_y()+self.bdWidth)
        absCoord0=(self.coord0[0]+rootCoord[0],self.coord0[1]+rootCoord[1])
        absCoord1=(self.coord1[0]+rootCoord[0],self.coord1[1]+rootCoord[1])
        for key in CheckedRect.TypeForPlace:
            CheckedRect.TypeForPlace[key](self,absCoord0,absCoord1)
    def __DrawFg(self):#画顶图
        pass
    def __DrawBg(self):#画底图，底图只在图片移动和放大时发生变化
        canvas=self.bgCanvas.canvas
        img=self.img.crop((#图片裁剪，后面图片以此为基础处理获得ImageTk图片
        max(self.scaleCenter[0]-self.boxWidth/(2*self.scaleMultiple),0),
        max(self.scaleCenter[0]-self.boxHeight/(2*self.scaleMultiple),0),
        min(self.scaleCenter[0]+self.boxWidth/(2*self.scaleMultiple),self.img.size[0]),
        min(self.scaleCenter[0]+self.boxHeight/(2*self.scaleMultiple),self.img.size[1])))
        self.bgImg=ImageTk.PhotoImage(img.point(lambda p:p*0.8))#把底图变暗(这运算很大，单独处理
        canvas.delete('bgImg')
        canvas.create_image(tuple(self.scaleCenter),image=self.bgImg,tags='bgImg')
    def SetRootCoord(self):#设置根坐标(当整个窗口被拖动的时候调用该函数，以刷新根坐标
        tk.update()
        rootX,rootY=self.bgCanvas.canvas.winfo_rootx(),self.bgCanvas.canvas.winfo_rooty()    
        self.bgCanvas.SetRootCoord(rootX,rootY)
        for key in CheckedRect.TypeForInit:
            exec("self.{}.SetRootCoord(rootX,rootY)".format(key))
    def SetUnitWH(self,unitW,unitH):#设置宽高比值(默认0:0，即自由裁剪
        self.unitW,self.unitH=(0,0) if(unitW<0 or unitH<0)else (unitW,unitH)
    def LoadImage(self,Img_PIL):#载入PIL的img图片，作为裁剪对象
        self.img=Img_PIL.copy()
        self.scaleCenter=[self.img.size[0]/2,self.img.size[1]/2]
        print(self.scaleCenter)
        self.scaleMultiple=min(round(self.boxWidth/self.img.size[0],1),round(self.boxHeight/self.img.size[1],1))-0.2
        self.__DrawBg()

tk=Tk()
tk.geometry('600x600')

cv=MyCanvas(tk,(350,350),'grey')
cv.canvas.place(x=30,y=30)

cr=CheckedRect(cv)
cr.LoadImage(Image.open('1.png'))
#cr.SetUnitWH(10,16)

tk.bind("<Configure>",lambda Event:cr.SetRootCoord())
tk.mainloop()














