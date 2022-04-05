from tkinter import *
from PIL import Image,ImageTk

tk=Tk()
tk.geometry('1200x800')
cv2=Canvas(tk,bg='yellow',width=700,height=700)
cv2.place(x=400,y=30)

class Mouse:
    def __init__(self):
        self.FuncRoll=None#中键滚动时调用的函数，无参
        self.FuncDrag=None#左键拖拽
        self.FuncRelease=None#左键释放
        self.FuncClick=None#左键按下
        self.FuncDoubleClick=None#左键双击
        self.FuncRightClick=None#右键按下
        self.FuncRightDrag=None#右键拖拽
        self.FuncDoubleRightClick=None#右键双击
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
    def RightDrag(self,Event):
        oldX,oldY=self.X,self.Y
        self.X,self.Y=self.__GetOppositeCoord(Event)
        self.OffsetX,self.OffsetY=self.X-oldX,self.Y-oldY
        if(self.FuncRightDrag):
            self.FuncRightDrag()
    def DoubleClick(self,Event):
        self.X,self.Y=self.__GetOppositeCoord(Event)
        if(self.FuncDoubleClick):
            self.FuncDoubleClick()
    def DoubleRightClick(self,Event):
        self.X,self.Y=self.__GetOppositeCoord(Event)
        if(self.FuncDoubleRightClick):
            self.FuncDoubleRightClick()

class MyCanvas:
    def __init__(self,root,size=(0,0),color='green',bdWidth=3,cursorType=None):
        self.canvas=Canvas(root,width=size[0],height=size[1],cursor=cursorType,bg=color,bd=bdWidth,relief=RIDGE)
        self.mouse=Mouse()
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
        self.boxHalfWidth=int(int(bgCanvas.canvas.config('width')[4])/2)#窗口大小(半宽
        self.boxHalfHeight=int(int(bgCanvas.canvas.config('height')[4])/2)#窗口大小(半高
        for key in CheckedRect.TypeForInit:
            CheckedRect.TypeForInit[key](self,bgCanvas.canvas.master)
            mouse=eval('self.{}.mouse'.format(key))
            mouse.FuncDrag=self.__DragOnWidget(key)
        bgCanvas.mouse.FuncDrag=self.__DragOnBgCanvas
        bgCanvas.mouse.FuncDoubleRightClick=self.__ClearRect
        bgCanvas.mouse.FuncClick=self.__SetCoord0
        bgCanvas.mouse.FuncRoll=self.__ScaleImg
        bgCanvas.mouse.FuncRightDrag=self.__DragScaleCenter
        
        self.img=Image.new(size=(2*self.boxHalfWidth,2*self.boxHalfHeight),mode="RGBA",color=bgCanvas.canvas.config('bg')[4])#待裁剪图片，默认图片底色
        self.croppedImg=self.img.copy()#裁剪的图片
        self.unitW=0
        self.unitH=0
        self.bdWidth=2+int(bgCanvas.canvas.config('bd')[4])#非常弱智，非常弱智，简直就是，只能说，nb，艹，傻逼玩意儿
        #获得的组件宽度是组件的整体开算的，而我这画布组件只关心绘画区，这导致了我图片以及画的矩形发生了偏移
        #真是神仙，画布组件无论怎么设置参数，总会有两个像素宽度的白色框在这组件的最外面，怎么都关不掉的，而且颜色也没办法更改，真是服了
        #它绘图是以组件的根坐标进行绘制的，不是根据绘画区的根坐标开始的，傻逼，简直就是傻逼，真是垃圾玩意儿，哪个脑瘫这么设计的，绘图谁会关心边框的
        #马德我愿称这弱智为神人，平添我开发难度
        self.scaleMultiple=1#缩放倍数
        self.scaleCenter=[self.boxHalfWidth,self.boxHalfHeight]#缩放中心
        self.fgCanvas=MyCanvas(bgCanvas.canvas,cursorType="cross",color=bgCanvas.canvas.config('bg')[4],bdWidth=0)#顶图
        self.fgCanvas.mouse.FuncDrag=self.__DragOnFgCanvas
        self.__DrawBg()
    def __LimitCoord(self,rootCoord,moveCoord):#将可变坐标moveCoord的值约束在画布内并且宽高比为定值
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
        return int(X),int(Y)
    def __DragOnWidget(self,type):#【左键拖拽四点】把函数闭包用在这妖魔的地方里，不合适。。(但没想到更合适的方法
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
    def __DragOnBgCanvas(self):#【左键拖拽底图】拖出一个矩形
        mouse=self.bgCanvas.mouse
        X,Y=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
        self.coord1=[X,Y]
        self.__DrawFg()
        self.__DrawRect()
        
    def __DragOnFgCanvas(self):#【左键拖拽顶图】将截选区域移动
        pass
    def __DragScaleCenter(self):#【右键拖拽底图】移动图片的缩放中心
        self.scaleCenter[0]-=int(self.bgCanvas.mouse.OffsetX/2)
        self.scaleCenter[1]-=int(self.bgCanvas.mouse.OffsetY/2)
        self.scaleCenter[0]=0 if self.scaleCenter[0]<0 else(self.img.size[0]-1 if self.scaleCenter[0]>=self.img.size[0] else self.scaleCenter[0])
        self.scaleCenter[1]=0 if self.scaleCenter[1]<0 else(self.img.size[1]-1 if self.scaleCenter[1]>=self.img.size[1] else self.scaleCenter[1])
        self.__DrawBg()
        if(self.bgCanvas.canvas.gettags('rect')):
            self.__DrawFg()
            self.__DrawRect()
    def __ClearRect(self):#【右键点击底图】清空画布
#        self.bgCanvas.canvas.delete('rect')
        for key in CheckedRect.TypeForInit:
            exec("self.{}.canvas.place_forget()".format(key))
        self.fgCanvas.canvas.place_forget()
    def __SetCoord0(self):#【左键拖拽底图】设置第一个坐标Coord0
        self.coord0=[self.bgCanvas.mouse.X,self.bgCanvas.mouse.Y]
    def __ScaleImg(self):#【中键滚动底图】对图片进行缩放
        if(self.bgCanvas.mouse.RollUp):
            self.scaleMultiple=round(self.scaleMultiple/0.95,2)
        else:
            if(self.scaleMultiple>0.1):
                self.scaleMultiple=round(self.scaleMultiple*0.95,2)
        self.__DrawBg()
        if(self.bgCanvas.canvas.gettags('rect')):
            self.__DrawFg()
            self.__DrawRect()
    def __DrawRect(self):#画矩形
        canvas=self.bgCanvas.canvas
#        canvas.delete('rect')
#        canvas.create_rectangle(*(self.__AlterCoord(self.coord0)),*(self.__AlterCoord(self.coord1)),outline='red',tags='rect')
        rootCoord=self.__AlterCoord((canvas.winfo_x(),canvas.winfo_y()))
        absCoord0=(self.coord0[0]+rootCoord[0],self.coord0[1]+rootCoord[1])
        absCoord1=(self.coord1[0]+rootCoord[0],self.coord1[1]+rootCoord[1])
        for key in CheckedRect.TypeForPlace:
            CheckedRect.TypeForPlace[key](self,absCoord0,absCoord1)
    def __DrawBg(self):#画底图，底图只在图片移动和放大时发生变化(底图的频繁处理会造成卡顿，所以单独挑了出来
        canvas=self.bgCanvas.canvas
        
        pstC=self.scaleCenter
        pstL=max(pstC[0]-self.boxHalfWidth/self.scaleMultiple,0)
        pstU=max(pstC[1]-self.boxHalfHeight/self.scaleMultiple,0)
        pstR=min(pstC[0]+self.boxHalfWidth/self.scaleMultiple,self.img.size[0])
        pstD=min(pstC[1]+self.boxHalfHeight/self.scaleMultiple,self.img.size[1])
        
        bgImg=self.img.crop((pstL,pstU,pstR,pstD))#图片裁剪，后面图片以此为基础处理获得ImageTk图片
        self.bgImg=bgImg.resize((round(bgImg.size[0]*self.scaleMultiple),round(bgImg.size[1]*self.scaleMultiple)),Image.ANTIALIAS)#改变图片尺寸
        self.bgTkImg=ImageTk.PhotoImage(self.bgImg.point(lambda p:p*0.8))#把底图变暗
        imgCenter=(#在合适的中心将图片打上去
            self.boxHalfWidth+(pstL+pstR-2*pstC[0])/2*self.scaleMultiple+self.bdWidth,
            self.boxHalfHeight+(pstU+pstD-2*pstC[1])/2*self.scaleMultiple+self.bdWidth)
        self.__AlterCoord(imgCenter)
        canvas.delete('bgTkImg')
        canvas.create_image(imgCenter,image=self.bgTkImg,tags='bgTkImg')
    #    global cv2
    #    cv2.delete('bgTkImg')
    #    cv2.create_image((350,350),image=self.bgTkImg,tags='bgTkImg')
    def __DrawFg(self):#画顶图
        canvas=self.fgCanvas.canvas
        L,U=self.coord0
        R,D=self.coord1
        if(L>R):
            L,R=R,L
        if(U>D):
            U,D=D,U
        self.fgImg=self.bgImg.crop((L+2,U+2,R+2,D+2))
        self.fgTkImg=ImageTk.PhotoImage(self.fgImg)
        canvas.delete('fgTkImg')
        canvas.create_image((int((R-L)/2+2),int((D-U)/2+2)),image=self.fgTkImg,tags='fgTkImg')
        canvas.config(width=R-L,height=D-U)
        canvas.place(x=L+self.bdWidth,y=U+self.bdWidth)
        global cv2
        cv2.delete('fgTkImg')
        cv2.create_image((350,350),image=self.fgTkImg,tags='fgTkImg')
    def __AlterCoord(self,coord):#将绘图坐标改成为组件坐标
        return (coord[0]+self.bdWidth,coord[1]+self.bdWidth)
    def __CropImg(self):
        croppedImg=self.img.crop(
                        self.scaleCenter[0]+int((self.coord0[0]-self.scaleCenter[0])/self.scaleMultiple),
                        self.scaleCenter[1]+int((self.coord0[1]-self.scaleCenter[1])/self.scaleMultiple),
                        self.scaleCenter[0]+int((self.coord1[0]-self.scaleCenter[0])/self.scaleMultiple),
                        self.scaleCenter[1]+int((self.coord1[1]-self.scaleCenter[1])/self.scaleMultiple))
        multiple=int(max(croppedImg.size[0]/self.unitW,croppedImg.size[1].self.unitH))
        self.croppedImg=croppedImg.resize(unitW*multiple,unitH*multiple,Image.ANTIALIAS)#改变图片大小
    def GetCroppedImg(self):
        return self.croppedImg
    def FreshRootCoord(self):#设置根坐标(当整个窗口被拖动的时候调用该函数，以刷新根坐标
        tk.update()
        rootX,rootY=self.bgCanvas.canvas.winfo_rootx(),self.bgCanvas.canvas.winfo_rooty()    
        self.bgCanvas.SetRootCoord(rootX,rootY)
        for key in CheckedRect.TypeForInit:
            exec("self.{}.SetRootCoord(rootX,rootY)".format(key))
    def SetUnitWH(self,unitW,unitH):#设置宽高比值(默认0:0，即自由裁剪
        self.unitW,self.unitH=(0,0) if(unitW<0 or unitH<0)else (unitW,unitH)
    def LoadImage(self,Img_PIL):#载入PIL的img图片，作为裁剪对象
        self.img=Img_PIL.copy()
        self.croppedImg=self.img.copy()
        self.scaleCenter=[self.img.size[0]/2,self.img.size[1]/2]
        self.scaleMultiple=round(min(2*self.boxHalfWidth/self.img.size[0],2*self.boxHalfHeight/self.img.size[1]),2)
        self.__DrawBg()

cv=MyCanvas(tk,(300,480),'grey')#主画布
cv.canvas.place(x=30,y=30)

cr=CheckedRect(cv)
cr.LoadImage(Image.open('Front.png'))
#cr.LoadImage(Image.open('Cube.png'))
#cr.LoadImage(Image.open('1.png'))
cr.SetUnitWH(10,16)

tk.bind("<Configure>",lambda Event:cr.FreshRootCoord())#绑定坐标刷新函数，以便不会出现偏移问题
tk.mainloop()














