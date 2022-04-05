from tkinter import *
from MyCanvas import *
import PIL.Image,PIL.ImageTk

class MyCropImage:#截图（内容耦合的庞大怪物
    def __init__(self,bgCanvas):
        self.boxHalfWidth=int(int(bgCanvas.canvas.config('width')[4])/2)#窗口大小(半宽
        self.boxHalfHeight=int(int(bgCanvas.canvas.config('height')[4])/2)#窗口大小(半高
        self.img=PIL.Image.new(size=(2*self.boxHalfWidth,2*self.boxHalfHeight),mode="RGBA",color='green')#待裁剪图片，默认图片底色
        self.croppedImg=self.img.copy()#裁剪的图片
        self.bdWidth=2+int(bgCanvas.canvas.config('bd')[4])#累了，不想对它多作解释

        self.bgCanvas=bgCanvas#底图
        self.bgCanvas.mouse.FuncDrag=self.__DragOnBgCanvas
        self.bgCanvas.mouse.FuncDoubleRightClick=self.__ClearFg
        self.bgCanvas.mouse.FuncClick=self.__SetCoord0
        self.bgCanvas.mouse.FuncRoll=self.__ScaleImgOnBg
        self.bgCanvas.mouse.FuncRelease=self.__RecoverCoord0
        self.bgCanvas.mouse.FuncRightDrag=lambda :self.__DragScaleCenter(self.bgCanvas.mouse)

        self.fgCanvas=MyCanvas(bgCanvas.canvas,cursorType="cross",color=bgCanvas.canvas.config('bg')[4],bdWidth=0)#顶图
        self.fgCanvas.mouse.FuncDrag=self.__DragOnFgCanvas
        self.fgCanvas.mouse.FuncRoll=self.__ScaleImgOnFg
        self.fgCanvas.mouse.FuncDoubleRightClick=self.__ClearFg
        self.fgCanvas.mouse.FuncRightDrag=lambda :self.__DragScaleCenter(self.fgCanvas.mouse)
        
        self.coord0=[0,0]#选中的左上角(逻辑坐标
        self.coord1=[0,0]#选中的右下角(逻辑坐标
        self.unitW=0#单位宽
        self.unitH=0#单位高
        self.scaleRatio=1#缩放倍率
        self.scaleCenter=[self.boxHalfWidth,self.boxHalfHeight]#缩放中心
        self.__freeCutting=False#自由裁剪
        self.__multiple=1#截图的宽高将单位宽高的倍数，如果是自由裁剪则该值为1

        for key in ['UL','DL','UR','DR']:
            exec('self.{}=MyCanvas(self.fgCanvas.canvas,cursorType="crosshair",bdWidth=0,size=(5,5))'.format(key))
            mouse=eval('self.{}.mouse'.format(key))
            mouse.FuncDrag=self.__DragOnWidget(key)
        
        self.master=bgCanvas.canvas
        while(self.master.master):
            self.master=self.master.master
        
        self.callBack=None#回调函数。当self.croppedImg发生变化时调用
        self.__DrawBg()
        self.coord0=self.__LimitTwoCoord([self.boxHalfWidth,self.boxHalfHeight],[0,0])
        self.coord1=self.__LimitTwoCoord(self.coord0,[self.boxHalfWidth*2,self.boxHalfHeight*2])
        self.__DrawFg(True)
    def __LimitOneCoord(self,coord):#将坐标coord限制在图片范围内
        L=int(self.boxHalfWidth+(0-self.scaleCenter[0])*self.scaleRatio)
        U=int(self.boxHalfHeight+(0-self.scaleCenter[1])*self.scaleRatio)
        R=int(self.boxHalfWidth+(self.img.size[0]-self.scaleCenter[0])*self.scaleRatio)-1
        D=int(self.boxHalfHeight+(self.img.size[1]-self.scaleCenter[1])*self.scaleRatio)-1
        if(coord[0]<L):
            coord[0]=L
        elif(coord[0]>R):
            coord[0]=R
        if(coord[1]<U):
            coord[1]=U
        elif(coord[1]>D):
            coord[1]=D
        return coord
    def __LimitTwoCoord(self,rootCoord,moveCoord):#使矩阵落在图片范围内并且宽高比为定值
        self.__multiple=1

        unitW=self.unitW
        unitH=self.unitH
        canvas=self.bgCanvas.canvas
        moveCoord=self.__LimitOneCoord(moveCoord)

        if(unitW==0 or unitH==0 or self.__freeCutting==True):
            return moveCoord
        unit1=(moveCoord[0]-rootCoord[0])/unitW
        unit2=(moveCoord[1]-rootCoord[1])/unitH
        if(abs(unit1)<abs(unit2)):
            unit2=abs(unit1) if unit2>0 else -abs(unit1)
        else:
            unit1=abs(unit2) if unit1>0 else -abs(unit2)
        X=rootCoord[0]+unitW*unit1
        Y=rootCoord[1]+unitH*unit2
        self.__multiple=abs(unit1)/self.scaleRatio
        return [int(X),int(Y)]
    def __DragOnWidget(self,type):#【左键拖拽四点】把函数闭包用在这妖魔的地方里，不合适。。(但没想到更合适的方法
        mouse=eval('self.{}.mouse'.format(type))
        canvas=self.bgCanvas.canvas
        if(type=="UL"):
            def Func():
                X,Y=self.__LimitTwoCoord([self.coord1[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord0[1]=X,Y
                self.__DrawFg(True)
            return Func
        elif(type=="UR"):
            def Func():
                X,Y=self.__LimitTwoCoord([self.coord0[0],self.coord1[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord0[1]=X,Y
                self.__DrawFg(True)
            return Func
        elif(type=="DL"):
            def Func():
                X,Y=self.__LimitTwoCoord([self.coord1[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord0[0],self.coord1[1]=X,Y
                self.__DrawFg(True)
            return Func
        elif(type=="DR"):
            def Func():
                X,Y=self.__LimitTwoCoord([self.coord0[0],self.coord0[1]],[mouse.X,mouse.Y])
                self.coord1[0],self.coord1[1]=X,Y
                self.__DrawFg(True)
            return Func
    def __DragOnBgCanvas(self):#【左键拖拽底图】拖出截选区
        mouse=self.bgCanvas.mouse
        self.coord1=self.__LimitTwoCoord(self.coord0,[mouse.X,mouse.Y])
        self.__DrawFg(True)

    def __DragOnFgCanvas(self):#【左键拖拽顶图】将截选区域移动
        mouse=self.fgCanvas.mouse
        self.coord0[0]+=mouse.OffsetX
        self.coord1[0]+=mouse.OffsetX
        self.coord0[1]+=mouse.OffsetY
        self.coord1[1]+=mouse.OffsetY
                
        BoundL=int(self.boxHalfWidth+(0-self.scaleCenter[0])*self.scaleRatio)
        BoundU=int(self.boxHalfHeight+(0-self.scaleCenter[1])*self.scaleRatio)
        BoundR=int(self.boxHalfWidth+(self.img.size[0]-self.scaleCenter[0])*self.scaleRatio)-1
        BoundD=int(self.boxHalfHeight+(self.img.size[1]-self.scaleCenter[1])*self.scaleRatio)-1
            
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
        L(valLR),R(valLR),U(valUD),D(valUD)
        
        self.__DrawFg(True)
    def __DragScaleCenter(self,canvasMouse):#【右键拖拽底图】移动图片的缩放中心
        preCenter=self.scaleCenter.copy()
        self.scaleCenter[0]-=int(canvasMouse.OffsetX/2)
        self.scaleCenter[1]-=int(canvasMouse.OffsetY/2)
        self.scaleCenter[0]=0 if self.scaleCenter[0]<0 else(self.img.size[0]-1 if self.scaleCenter[0]>=self.img.size[0] else self.scaleCenter[0])
        self.scaleCenter[1]=0 if self.scaleCenter[1]<0 else(self.img.size[1]-1 if self.scaleCenter[1]>=self.img.size[1] else self.scaleCenter[1])
        self.coord0=[self.coord0[0]-(self.scaleCenter[0]-preCenter[0])*self.scaleRatio,self.coord0[1]-(self.scaleCenter[1]-preCenter[1])*self.scaleRatio]
        self.coord1=[self.coord1[0]-(self.scaleCenter[0]-preCenter[0])*self.scaleRatio,self.coord1[1]-(self.scaleCenter[1]-preCenter[1])*self.scaleRatio]
        self.__DrawBg()
        if(self.fgCanvas.canvas.place_info()):
            self.__DrawFg()
    def __ClearFg(self):#【右键双击底图】清空画布
        for key in ['UL','DL','UR','DR']:
            exec("self.{}.canvas.place_forget()".format(key))
        self.fgCanvas.canvas.place_forget()
    def __SetCoord0(self):#【左键点击底图】设置第一个坐标Coord0
        self.preCoord0=self.coord0.copy()
        self.coord0=self.__LimitOneCoord([self.bgCanvas.mouse.X,self.bgCanvas.mouse.Y])
    def __RecoverCoord0(self):#【左键释放底图】如果左键并没有对底图进行拖拽则恢复回之前的coord0
        if(self.coord0==[self.bgCanvas.mouse.X,self.bgCanvas.mouse.Y]):
            self.coord0=self.preCoord0
    def __ScaleImgOnBg(self):#【中键滚动底图】对图片进行缩放
        self.__ScaleImg(self.bgCanvas.mouse.RollUp)
    def __ScaleImgOnFg(self):#【中键滚动顶图】对图片进行缩放
        self.__ScaleImg(self.fgCanvas.mouse.RollUp)
    def __ScaleImg(self,RollUp):#缩放图片
        ratio=self.scaleRatio
        if(RollUp):
            if(self.scaleRatio<5):
                self.scaleRatio=round(self.scaleRatio/0.95,2)
        else:
            if(self.scaleRatio>0.1):
                self.scaleRatio=round(self.scaleRatio*0.95,2)
        ratio=self.scaleRatio/ratio
        self.__DrawBg()
        if(self.fgCanvas.canvas.place_info()):
            self.coord0=[self.boxHalfWidth-(self.boxHalfWidth-self.coord0[0])*ratio,self.boxHalfHeight-(self.boxHalfHeight-self.coord0[1])*ratio]
            self.coord1=[self.boxHalfWidth-(self.boxHalfWidth-self.coord1[0])*ratio,self.boxHalfHeight-(self.boxHalfHeight-self.coord1[1])*ratio]
            self.__DrawFg()        
    def __DrawBg(self):#画底图，底图只在图片移动和缩放时发生变化(底图的频繁处理会造成卡顿
        canvas=self.bgCanvas.canvas
        
        pstC=self.scaleCenter
        pstL=max(pstC[0]-self.boxHalfWidth/self.scaleRatio,0)
        pstU=max(pstC[1]-self.boxHalfHeight/self.scaleRatio,0)
        pstR=min(pstC[0]+self.boxHalfWidth/self.scaleRatio,self.img.size[0])
        pstD=min(pstC[1]+self.boxHalfHeight/self.scaleRatio,self.img.size[1])
        
        bgImg=self.img.crop((pstL,pstU,pstR,pstD))#图片裁剪，后面图片以此为基础处理获得ImageTk图片
        self.bgImg=bgImg.resize((round(bgImg.size[0]*self.scaleRatio),round(bgImg.size[1]*self.scaleRatio)),PIL.Image.ANTIALIAS)#改变图片尺寸
        self.bgTkImg=PIL.ImageTk.PhotoImage(self.bgImg.point(lambda p:p*0.8))#把底图变暗
        imgCenter=(#在合适的中心将图片打上去
            self.boxHalfWidth+(pstL+pstR-2*pstC[0])/2*self.scaleRatio+self.bdWidth,
            self.boxHalfHeight+(pstU+pstD-2*pstC[1])/2*self.scaleRatio+self.bdWidth)
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

        #确定顶图图象
        imgCenter=self.bgCanvas.canvas.coords(self.bgCanvas.canvas.find_withtag('bgTkImg'))
        imgSize=self.bgImg.size
        imgOffset=[imgCenter[0]-imgSize[0]/2,imgCenter[1]-imgSize[1]/2]
        self.fgImg=self.bgImg.crop((L+3-imgOffset[0],U+3-imgOffset[1],R+3-imgOffset[0],D+3-imgOffset[1]))
        self.fgTkImg=PIL.ImageTk.PhotoImage(self.fgImg)
        canvas.delete('fgTkImg')
        canvas.create_image((2,2),anchor=NW,image=self.fgTkImg,tags='fgTkImg')
        canvas.config(width=R-L,height=D-U)
        canvas.place(x=L+self.bdWidth-1,y=U+self.bdWidth-1)

        #绘制四点        
        _U=0
        _D=int(canvas.config('height')[4])-4
        _L=0
        _R=int(canvas.config('width')[4])-5
        if(self.coord0[0]>self.coord1[0]):
            _L,_R=_R,_L
        if(self.coord0[1]>self.coord1[1]):
            _U,_D=_D,_U
        self.UL.canvas.place(x=_L,y=_U)
        self.UR.canvas.place(x=_R,y=_U)
        self.DL.canvas.place(x=_L,y=_D)
        self.DR.canvas.place(x=_R,y=_D)

        if(cropImg):
            L=max(self.scaleCenter[0]+int((self.coord0[0]-self.boxHalfWidth)/self.scaleRatio),0)
            U=max(self.scaleCenter[1]+int((self.coord0[1]-self.boxHalfHeight)/self.scaleRatio),0)
            R=min(self.scaleCenter[0]+int((self.coord1[0]-self.boxHalfWidth)/self.scaleRatio),self.img.size[0])
            D=min(self.scaleCenter[1]+int((self.coord1[1]-self.boxHalfHeight)/self.scaleRatio),self.img.size[1])
            if(L>R):
                L,R=R,L
            if(U>D):
                U,D=D,U
            if(L==R or U==D):
                self.croppedImg=PIL.Image.new(size=(1,1),mode="RGBA",color=self.img.getpixel((L,U)))
            else:
                self.croppedImg=self.img.crop((L,U,R,D))
            if(self.callBack):
                self.callBack()
    def GetMultiple(self):
        return self.__multiple
    def GetCroppedImg(self):
        return self.croppedImg
    def SetCallBackFunc(self,Func):#设置回调函数。当self.croppedImg发生变化时调用该函数
        self.callBack=Func
    def FreshRootCoord(self):#设置根坐标(当整个窗口被拖动的时候调用该函数，以刷新根坐标
        self.master.update()
        rootX=self.bgCanvas.canvas.winfo_rootx()+self.bdWidth
        rootY=self.bgCanvas.canvas.winfo_rooty()+self.bdWidth
        self.bgCanvas.SetRootCoord(rootX,rootY)
        for key in ['UL','DL','UR','DR']:
            exec("self.{}.SetRootCoord(rootX,rootY)".format(key))
    def SetUnitWH(self,unitW,unitH):#设置宽高比值(默认0:0，即自由裁剪
        self.unitW,self.unitH=(0,0) if(unitW<0 or unitH<0)else (unitW,unitH)
        self.__multiple=1
    def LoadImage(self,Img_PIL):#载入PIL的img图片，作为裁剪对象
        if(Img_PIL):
            self.img=Img_PIL.copy()
            self.croppedImg=self.img.copy()
            self.scaleCenter=[int(self.img.size[0]/2),int(self.img.size[1]/2)]
            self.scaleRatio=round(min(2*self.boxHalfWidth/self.img.size[0],2*self.boxHalfHeight/self.img.size[1]),2)
            self.__DrawBg()
            self.FullSizeCrop()
    def FreeCutting(self,flag):
        self.__freeCutting=flag
        self.coord0=self.__LimitTwoCoord(self.coord1,self.coord0)
        self.coord1=self.__LimitTwoCoord(self.coord0,self.coord1)
        self.__DrawFg(True)
    def FullSizeCrop(self):
        self.coord0=self.__LimitTwoCoord([self.boxHalfWidth,self.boxHalfHeight],[0,0])
        self.coord1=self.__LimitTwoCoord(self.coord0,[self.boxHalfWidth*2,self.boxHalfHeight*2])
        self.__DrawFg(True)
        
