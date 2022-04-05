from tkinter import *
from PIL import Image,ImageTk

tk=Tk()
tk.geometry('1200x800')
cv2=Canvas(tk,bg='yellow',width=700,height=700)
cv2.place(x=800,y=30)

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

class CropImage:#截图（内容耦合的庞大怪物，代码质量很差，
    def __init__(self,bgCanvas):        
        self.bgCanvas=bgCanvas#底图
        self.boxHalfWidth=int(int(bgCanvas.canvas.config('width')[4])/2)#窗口大小(半宽
        self.boxHalfHeight=int(int(bgCanvas.canvas.config('height')[4])/2)#窗口大小(半高
        self.img=Image.new(size=(2*self.boxHalfWidth,2*self.boxHalfHeight),mode="RGBA",color='green')#待裁剪图片，默认图片底色
        self.croppedImg=self.img.copy()#裁剪的图片
        self.bdWidth=2+int(bgCanvas.canvas.config('bd')[4])#累了，不想对它多作解释
        bgCanvas.mouse.FuncDrag=self.__DragOnBgCanvas
        bgCanvas.mouse.FuncDoubleRightClick=self.__ClearFg
        bgCanvas.mouse.FuncClick=self.__SetCoord0
        bgCanvas.mouse.FuncRoll=self.__ScaleImgOnBg
        bgCanvas.mouse.FuncRightDrag=self.__DragScaleCenter
        bgCanvas.mouse.FuncRelease=self.__RecoverCoord0

        self.fgCanvas=MyCanvas(bgCanvas.canvas,cursorType="cross",color=bgCanvas.canvas.config('bg')[4],bdWidth=0)#顶图
        self.fgCanvas.mouse.FuncDrag=self.__DragOnFgCanvas
        self.fgCanvas.mouse.FuncRoll=self.__ScaleImgOnFg

        self.coord0=[0,0]#选中的左上角(逻辑坐标
        self.coord1=[0,0]#选中的右下角(逻辑坐标
        self.unitW=0#单位宽
        self.unitH=0#单位高
        self.scaleMultiple=1#缩放倍数
        self.scaleCenter=[self.boxHalfWidth,self.boxHalfHeight]#缩放中心

        for key in ['UL','DL','UR','DR']:
            exec('self.{}=MyCanvas(self.fgCanvas.canvas,cursorType="crosshair",bdWidth=5)'.format(key))
            mouse=eval('self.{}.mouse'.format(key))
            mouse.FuncDrag=self.__DragOnWidget(key)
        
        self.__DrawBg()
    def __LimitCoord(self,rootCoord,moveCoord):#将可变坐标moveCoord的值约束在画布内并且宽高比为定值
        unitW=self.unitW
        unitH=self.unitH
        canvas=self.bgCanvas.canvas
        rootCoord=list(rootCoord)
        moveCoord=list(moveCoord)
        
        width=int(canvas.config('width')[4])-1
        height=int(canvas.config('height')[4])-1
        BoundL=int(self.boxHalfWidth+(0-self.scaleCenter[0])*self.scaleMultiple)
        BoundU=int(self.boxHalfHeight+(0-self.scaleCenter[1])*self.scaleMultiple)
        BoundR=int(self.boxHalfWidth+(self.img.size[0]-self.scaleCenter[0])*self.scaleMultiple)-1
        BoundD=int(self.boxHalfHeight+(self.img.size[1]-self.scaleCenter[1])*self.scaleMultiple)-1

        if(BoundL<0):
            BoundL=0
        if(BoundR>width):
            BoundR=width
        if(BoundU<0):
            BoundU=0
        if(BoundD>height):
            BoundD=height
        
        if moveCoord[0]<BoundL:
            moveCoord[0]=BoundL
        if moveCoord[1]<BoundU:
            moveCoord[1]=BoundU
        if moveCoord[0]>BoundR:
            moveCoord[0]=BoundR
        if moveCoord[1]>BoundD:
            moveCoord[1]=BoundD
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
        if(X<BoundL or Y<BoundU):
            X+=unitW
            Y+=unitH
        if(X>BoundR or Y>BoundD):
            X-=unitW
            Y-=unitH
        return [int(X),int(Y)]
    def __DragOnWidget(self,type):#【左键拖拽四点】把函数闭包用在这妖魔的地方里，不合适。。(但没想到更合适的方法
        mouse=eval('self.{}.mouse'.format(type))
        canvas=self.bgCanvas.canvas
        if(type=="UL"):
            def Func():
                X,Y=self.__LimitCoord([self.coord1[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord0[1]=X,Y
                self.__DrawFg(True)
            return Func
        elif(type=="UR"):
            def Func():
                X,Y=self.__LimitCoord([self.coord0[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord0[1]=X,Y
                self.__DrawFg(True)
            return Func
        elif(type=="DL"):
            def Func():
                X,Y=self.__LimitCoord([self.coord1[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord1[1]=X,Y
                self.__DrawFg(True)
            return Func
        elif(type=="DR"):
            def Func():
                X,Y=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord1[1]=X,Y
                self.__DrawFg(True)
            return Func
    def __DragOnBgCanvas(self):#【左键拖拽底图】拖出一个矩形
        mouse=self.bgCanvas.mouse
        self.coord1=self.__LimitCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
        self.__DrawFg(True)

    def __DragOnFgCanvas(self):#【左键拖拽顶图】将截选区域移动
        mouse=self.fgCanvas.mouse
        self.coord0[0]+=mouse.OffsetX
        self.coord1[0]+=mouse.OffsetX
        self.coord0[1]+=mouse.OffsetY
        self.coord1[1]+=mouse.OffsetY
                
        width=self.boxHalfWidth*2
        height=self.boxHalfHeight*2
        BoundL=int(self.boxHalfWidth+(0-self.scaleCenter[0])*self.scaleMultiple)
        BoundU=int(self.boxHalfHeight+(0-self.scaleCenter[1])*self.scaleMultiple)
        BoundR=int(self.boxHalfWidth+(self.img.size[0]-self.scaleCenter[0])*self.scaleMultiple)-1
        BoundD=int(self.boxHalfHeight+(self.img.size[1]-self.scaleCenter[1])*self.scaleMultiple)-1
        if(BoundL<0):
            BoundL=0
        if(BoundR>width):
            BoundR=width
        if(BoundU<0):
            BoundU=0
        if(BoundD>height):
            BoundD=height
            
        if(self.coord0[0]<self.coord1[0]):#诡异的方式近似实现指针
            L=lambda val:(exec('self.coord0[0]+=val'),self.coord0[0])[1]
            R=lambda val:(exec('self.coord1[0]+=val'),self.coord1[0])[1]
        else:
            L=lambda val:(exec('self.coord1[0]+=val'),self.coord1[0])[1]
            R=lambda val:(exec('self.coord0[0]+=val'),self.coord0[0])[1]
        if(self.coord0[1]<self.coord1[1]):
            U=lambda val:(exec('self.coord0[1]+=val'),self.coord0[1])[1]
            D=lambda val:(exec('self.coord1[1]+=val'),self.coord1[1])[1]
        else:
            U=lambda val:(exec('self.coord1[1]+=val'),self.coord1[1])[1]
            D=lambda val:(exec('self.coord0[1]+=val'),self.coord0[1])[1]
            
        valLR=0
        valUD=0
        if(L(0)<BoundL):
            valLR=BoundL-L(0)
        elif(R(0)>BoundR):
            valLR=BoundR-R(0)
        if(U(0)<BoundU):
            valUD=BoundU-U(0)
        elif(D(0)>BoundD):
            valUD=BoundD-D(0)
        L(valLR)
        R(valLR)
        U(valUD)
        D(valUD)
        
        self.__DrawFg(True)
    def __DragScaleCenter(self):#【右键拖拽底图】移动图片的缩放中心
        preCenter=self.scaleCenter.copy()
        self.scaleCenter[0]-=int(self.bgCanvas.mouse.OffsetX/2)
        self.scaleCenter[1]-=int(self.bgCanvas.mouse.OffsetY/2)
        self.scaleCenter[0]=0 if self.scaleCenter[0]<0 else(self.img.size[0]-1 if self.scaleCenter[0]>=self.img.size[0] else self.scaleCenter[0])
        self.scaleCenter[1]=0 if self.scaleCenter[1]<0 else(self.img.size[1]-1 if self.scaleCenter[1]>=self.img.size[1] else self.scaleCenter[1])
        self.coord0=[self.coord0[0]-(self.scaleCenter[0]-preCenter[0])*self.scaleMultiple,self.coord0[1]-(self.scaleCenter[1]-preCenter[1])*self.scaleMultiple]
        self.coord1=[self.coord1[0]-(self.scaleCenter[0]-preCenter[0])*self.scaleMultiple,self.coord1[1]-(self.scaleCenter[1]-preCenter[1])*self.scaleMultiple]
        self.__DrawBg()
        if(self.fgCanvas.canvas.place_info()):
            self.__DrawFg()
    def __ClearFg(self):#【右键双击底图】清空画布
        for key in ['UL','DL','UR','DR']:
            exec("self.{}.canvas.place_forget()".format(key))
        self.fgCanvas.canvas.place_forget()
    def __SetCoord0(self):#【左键点击底图】设置第一个坐标Coord0
        self.preCoord0=self.coord0.copy()
        self.coord0=[self.bgCanvas.mouse.X,self.bgCanvas.mouse.Y]
    def __RecoverCoord0(self):#【左键释放底图】如果左键并没有对底图进行拖拽则恢复回之前的coord0
        if(self.coord0==[self.bgCanvas.mouse.X,self.bgCanvas.mouse.Y]):
            self.coord0=self.preCoord0
    def __ScaleImgOnBg(self):#【中键滚动底图】对图片进行缩放
        self.__ScaleImg(self.bgCanvas.mouse.RollUp)
    def __ScaleImgOnFg(self):#【中键滚动顶图】对图片进行缩放
        self.__ScaleImg(self.fgCanvas.mouse.RollUp)
    def __ScaleImg(self,RollUp):#缩放图片
        multiple=self.scaleMultiple
        if(RollUp):
            if(self.scaleMultiple<5):
                self.scaleMultiple=round(self.scaleMultiple/0.95,2)
        else:
            if(self.scaleMultiple>0.1):
                self.scaleMultiple=round(self.scaleMultiple*0.95,2)
        multiple=self.scaleMultiple/multiple
        self.__DrawBg()
        if(self.fgCanvas.canvas.place_info()):
            self.coord0=[self.boxHalfWidth-(self.boxHalfWidth-self.coord0[0])*multiple,self.boxHalfHeight-(self.boxHalfHeight-self.coord0[1])*multiple]
            self.coord1=[self.boxHalfWidth-(self.boxHalfWidth-self.coord1[0])*multiple,self.boxHalfHeight-(self.boxHalfHeight-self.coord1[1])*multiple]
            self.__DrawFg()        
    def __DrawBg(self):#画底图，底图只在图片移动和缩放时发生变化(底图的频繁处理会造成卡顿
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
        canvas.delete('bgTkImg')
        canvas.create_image(imgCenter,image=self.bgTkImg,tags='bgTkImg')

    def __DrawFg(self,cropImg=False):#画顶图。如果cropImg为真则顺便对self.croppedImg赋值
        canvas=self.fgCanvas.canvas
        L,U=self.coord0
        R,D=self.coord1
        if(L>R):
            L,R=R,L
        if(U>D):
            U,D=D,U

        imgCenter=self.bgCanvas.canvas.coords(self.bgCanvas.canvas.find_withtag('bgTkImg'))
        imgSize=self.bgImg.size
        imgOffset=[imgCenter[0]-imgSize[0]/2,imgCenter[1]-imgSize[1]/2]
        
        self.fgImg=self.bgImg.crop((L+3-imgOffset[0],U+3-imgOffset[1],R+3-imgOffset[0],D+3-imgOffset[1]))
        self.fgTkImg=ImageTk.PhotoImage(self.fgImg)
        canvas.delete('fgTkImg')
        canvas.create_image((2,2),anchor=NW,image=self.fgTkImg,tags='fgTkImg')
        canvas.config(width=R-L,height=D-U)
        canvas.place(x=L+self.bdWidth-1,y=U+self.bdWidth-1)
        self.__DrawWidget()

        if(cropImg):
            L=self.scaleCenter[0]+int((self.coord0[0]-self.boxHalfWidth)/self.scaleMultiple)
            U=self.scaleCenter[1]+int((self.coord0[1]-self.boxHalfHeight)/self.scaleMultiple)
            R=self.scaleCenter[0]+int((self.coord1[0]-self.boxHalfWidth)/self.scaleMultiple)
            D=self.scaleCenter[1]+int((self.coord1[1]-self.boxHalfHeight)/self.scaleMultiple)
            if(L>R):
                L,R=R,L
            if(U>D):
                U,D=D,U
            self.croppedImg=self.img.crop((L,U,R,D))
            if(self.unitW !=0 and self.unitH != 0):
                multiple=int(min(self.croppedImg.size[0]/self.unitW,self.croppedImg.size[1]/self.unitH)+1)
                self.croppedImg=self.croppedImg.resize((round(self.unitW*multiple),round(self.unitH*multiple)),Image.ANTIALIAS)#改变图片大小

        global cv2
        cv2.delete('TkImg')
        self.cpTkImg=ImageTk.PhotoImage(self.croppedImg)
        cv2.create_image((350,350),image=self.cpTkImg,tags='TkImg')

    def __DrawWidget(self):#绘制四点
        canvas=self.fgCanvas.canvas
        self.UL.canvas.place(x=-6,y=-6)
        self.UR.canvas.place(x=int(canvas.config('width')[4])-4,y=-6)
        self.DL.canvas.place(x=-6,y=int(canvas.config('height')[4])-4)
        self.DR.canvas.place(x=int(canvas.config('width')[4])-4,y=int(canvas.config('height')[4])-4)

    def GetCroppedImg(self):
        return self.croppedImg
    def FreshRootCoord(self):#设置根坐标(当整个窗口被拖动的时候调用该函数，以刷新根坐标
        tk.update()
        rootX=self.bgCanvas.canvas.winfo_rootx()+self.bdWidth
        rootY=self.bgCanvas.canvas.winfo_rooty()+self.bdWidth
        self.bgCanvas.SetRootCoord(rootX,rootY)
        for key in ['UL','DL','UR','DR']:
            exec("self.{}.SetRootCoord(rootX,rootY)".format(key))
    def SetUnitWH(self,unitW,unitH):#设置宽高比值(默认0:0，即自由裁剪
        self.unitW,self.unitH=(0,0) if(unitW<0 or unitH<0)else (unitW,unitH)
    def LoadImage(self,Img_PIL):#载入PIL的img图片，作为裁剪对象
        self.img=Img_PIL.copy()
        self.croppedImg=self.img.copy()
        self.scaleCenter=[self.img.size[0]/2,self.img.size[1]/2]
        self.scaleMultiple=round(min(2*self.boxHalfWidth/self.img.size[0],2*self.boxHalfHeight/self.img.size[1]),2)
        self.__DrawBg()

#cv=MyCanvas(tk,(300,480),'grey',bdWidth=0)#主画布
#cv.canvas.place(x=30,y=30)
#
#ci=CropImage(cv)
#ci.LoadImage(Image.open('Front.png'))
#ci.LoadImage(Image.open('Cube.png'))
#ci.LoadImage(Image.open('Back.jpg'))
#ci.SetUnitWH(10,16)
#
#tk.bind("<Configure>",lambda Event:ci.FreshRootCoord())#绑定坐标刷新函数，以便不会出现偏移问题
#tk.mainloop()
#

myCv1=MyCanvas(tk,(300,480),'grey',bdWidth=0)#主画布
myCi1=CropImage(myCv1)
myCi1.LoadImage(Image.open('Front.png'))
myCi1.SetUnitWH(10,16)
tk.bind("<Configure>",lambda Event:myCi1.FreshRootCoord())#绑定坐标刷新函数，以便不会出现偏移问题

myCv2=MyCanvas(tk,(300,480),'grey',bdWidth=0)#主画布
myCi2=CropImage(myCv2)
myCi2.LoadImage(Image.open('Back.jpg'))
myCi2.SetUnitWH(10,16)
tk.bind("<Configure>",lambda Event:myCi2.FreshRootCoord())#绑定坐标刷新函数，以便不会出现偏移问题

myCv1.canvas.grid(row=0,column=2)
myCv2.canvas.grid(row=0,column=3)
tk.mainloop()





