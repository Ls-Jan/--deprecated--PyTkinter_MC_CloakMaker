from MyCropImage import *
from My3DViewer import *
from MyImgsSizeModifier import *
from tkinter.filedialog import *
from tkinter import *
from PIL import Image
import tkinter.colorchooser
import tkinter.messagebox
import os

tk=Tk()
tk.geometry('1200x800')

#添加菜单
menu_Main=Menu(tk)
menu_LoadBar=Menu(menu_Main,tearoff=0)
menu_SaveBar=Menu(menu_Main,tearoff=0)
menu_HelpBar=Menu(menu_Main,tearoff=0)
menu_Main.add_cascade(label="导入", menu=menu_LoadBar)
menu_Main.add_cascade(label="导出", menu=menu_SaveBar)
menu_Main.add_cascade(label="帮助", menu=menu_HelpBar)
tk.config(menu=menu_Main)

#生成框架，便于布局
frame_3DViewer=Frame(tk)#框架，主要包含三维显示器
frame_CropperFront=Frame(tk)#框架，主要包含正面裁剪器
frame_CropperBack=Frame(tk)#框架，主要包含背面裁剪器
frame_ColorChoose=Frame(frame_3DViewer)#框架，选择披风其余4面的颜色
frame_3DViewer.grid(row=0,column=0)
frame_CropperFront.grid(row=0,column=1)
frame_CropperBack.grid(row=0,column=2)
frame_ColorChoose.grid(row=1,column=2,rowspan=2)

#三维显示器
myCv3D=MyCanvas(frame_3DViewer,(480,480),'grey',bdWidth=0)
my3DViewer=My3DViewer(myCv3D)
my3DViewer.blockList.append(Block([(-5,-1,8),(-5,-1,-8),(5,-1,-8),(5,-1,8),(5,0,8),(5,0,-8),(-5,0,-8),(-5,0,8)]))
myCv3D.canvas.grid(row=0,column=0,columnspan=3)

#截图器(正面
myCvFront=MyCanvas(frame_CropperFront,(300,480),'grey',bdWidth=0)
myCrop_Front=MyCropImage(myCvFront)
myCrop_Front.SetUnitWH(10,16)
myCvFront.canvas.grid(row=0,column=0)

#截图器(背面
myCvBack=MyCanvas(frame_CropperBack,(300,480),'grey',bdWidth=0)
myCrop_Back=MyCropImage(myCvBack)
myCrop_Back.SetUnitWH(10,16)
myCvBack.canvas.grid(row=0,column=0)

#披风其余四面的颜色选择
myCvU=MyCanvas(frame_ColorChoose,(60,15),'#b1d2da',bdWidth=0)
myCvD=MyCanvas(frame_ColorChoose,(60,15),'#b1d2da',bdWidth=0)
myCvL=MyCanvas(frame_ColorChoose,(60,15),'#b1d2da',bdWidth=0)
myCvR=MyCanvas(frame_ColorChoose,(60,15),'#b1d2da',bdWidth=0)
myCvU.myLabel=Label(frame_ColorChoose,text='上：')
myCvD.myLabel=Label(frame_ColorChoose,text='下：')
myCvL.myLabel=Label(frame_ColorChoose,text='左：')
myCvR.myLabel=Label(frame_ColorChoose,text='右：')
myCvU.canvas.grid(row=0,column=1)
myCvD.canvas.grid(row=1,column=1)
myCvL.canvas.grid(row=2,column=1)
myCvR.canvas.grid(row=3,column=1)
myCvU.myLabel.grid(row=0,column=0)
myCvD.myLabel.grid(row=1,column=0)
myCvL.myLabel.grid(row=2,column=0)
myCvR.myLabel.grid(row=3,column=0)

#披风数据显示
info_Cloak=Label(frame_3DViewer)
info_Cloak.myStr=StringVar()
info_Cloak.config(textvariable=info_Cloak.myStr)
info_Cloak.grid(row=1,column=0,rowspan=2)

#披风分辨率大小控制条
bar_Scale=Scale(frame_3DViewer,from_=1,to=10,orient='horizontal',length=150,width=15,sliderrelief=RIDGE)
bar_Scale.myInt=IntVar()
bar_Scale.config(variable=bar_Scale.myInt)
bar_Scale.grid(row=1,column=1)

#披风文件大小获取按钮
bt_CloakSize=Button(frame_3DViewer,text='获取披风文件大小')
bt_CloakSize.grid(row=2,column=1)

#图片自由裁剪按钮
freeCutting_Front=Checkbutton(frame_CropperFront, text = "自由裁剪",command=lambda:print(freeCutting_Front.myVar.get()))
freeCutting_Front.myVar=IntVar()
freeCutting_Front.config(variable=freeCutting_Front.myVar)
freeCutting_Back=Checkbutton(frame_CropperBack, text = "自由裁剪",command=lambda:print(freeCutting_Back.myVar.get()))
freeCutting_Back.myVar=IntVar()
freeCutting_Back.config(variable=freeCutting_Back.myVar)
freeCutting_Back.grid(row=1,column=0)
freeCutting_Front.grid(row=1,column=0)

#图片大小约束器
myModifier=MyImgsSizeModifier()

#功能函数
def GetClock():#获取披风图
    unit=bar_Scale.myInt.get()#单位长度
    cloak=Image.new("RGBA",(64*unit,32*unit))#披风~
    cloak.paste(myModifier.GetImg('Up'),(unit,0))#上位置
    cloak.paste(myModifier.GetImg('Down'),(11*unit,0))#下位置
    cloak.paste(myModifier.GetImg('Left'),(0,unit))#左位置
    cloak.paste(myModifier.GetImg('Right'),(11*unit,unit))#右位置
    cloak.paste(myModifier.GetImg('Front'),(unit,unit))#正披风
    cloak.paste(myModifier.GetImg('Back'),(12*unit,unit))#背披风	
    return cloak
def GetCloakSize():#获取披风大小(采取曲线救国的方式，这方法卡顿严重所以不能实时调用只能扔在按钮里
    path='获取披风文件大小的临时文件.png'
    cloak=GetClock()
    cloak.save(path)
    size=int(os.stat(path).st_size/1024)+1
    tkinter.messagebox.showinfo(title='【披风文件大小】', message='披风文件大小：\n{}kb'.format(size))
def SetCloakInfo():#设置info_Cloak的文本内容
    text="正背面图片分辨率：(10x16)*{}\n披风图片分辨率：(64x32)*{}"
    scale=bar_Scale.myInt.get()#比例数
    info_Cloak.myStr.set(text.format(scale,scale))
def CallBackFunc_Front():#用于正面截图器的回调
    front=myCrop_Front.GetCroppedImg()
    bar_Scale.config(to=max(myCrop_Front.GetMultiple(),myCrop_Back.GetMultiple()))
    myModifier.AddImg('Front',front,(10,16))
    my3DViewer.blockList[0].SetImg('Front',myModifier.GetImg('Front'))
    my3DViewer.Work()
def CallBackFunc_Back():#用于背面截图器的回调
    back=myCrop_Back.GetCroppedImg()
    bar_Scale.config(to=max(myCrop_Front.GetMultiple(),myCrop_Back.GetMultiple()))
    myModifier.AddImg('Back',back,(10,16))
    my3DViewer.blockList[0].SetImg('Back',myModifier.GetImg('Back'))
    my3DViewer.Work()    
def DragBarScale():#用于拖拽分辨率控制条的回调
    myModifier.SetMultiple(bar_Scale.myInt.get())
    my3DViewer.blockList[0].SetImg('Front',myModifier.GetImg('Front'))
    my3DViewer.blockList[0].SetImg('Back',myModifier.GetImg('Back'))
    SetCloakInfo()
    my3DViewer.Work()
def SetColor(direction):#用于颜色选择器的回调，参数为'UDLR'的其中一个字母，即'上下左右'的意思
    dictName={'U':'Up','D':'Down','L':'Left','R':'Right'}
    dictSize={'U':(10,1),'D':(10,1),'L':(1,16),'R':(1,16)}
    if(['U','D','L','R'].count(direction)==1):
        myCv=eval('myCv{}'.format(direction))
        color=tkinter.colorchooser.Chooser(tk).show()
        if(color[0]):
            myCv.canvas.config(bg=color[1])
            color=tuple(map(lambda x:int(x),color[0]))
        else:
            color=myCvU.canvas.config('bg')[4]
        size=dictSize[direction]
        direction=dictName[direction]
        myModifier.AddImg(direction,Image.new('RGB',(1,1),color),size)
        my3DViewer.blockList[0].SetImg(direction,myModifier.GetImg(direction))
        my3DViewer.Work()
def LoadImg():#读取图片(PIL.Image
    path = askopenfilename(filetypes=[('png','.png')])
    if(path):
        return Image.open(path)
def SaveImg(img):#保存图片(PIL.Image
    path = asksaveasfilename(filetypes=[('png','.png')],defaultextension=True)
    if(path):
        img.save(path)
def LoadImg_Front():#载入正面图
    front=LoadImg()
    myCrop_Front.LoadImage(front)
    CallBackFunc_Front()
def LoadImg_Back():#载入背面图
    back=LoadImg()
    myCrop_Back.LoadImage(back)
    CallBackFunc_Back()
def LoadImg_Cloak():#载入披风图
    cloak=LoadImg()
    if(cloak):
        size=cloak.size
        unit=int(size[0]/64)
        bar_Scale.config(to=unit)
        bar_Scale.myInt.set(unit)
        myModifier.SetMultiple(unit)
        dict={
            'Up':[(unit,0,11*unit,unit),(10,1)],
            'Down':[(11*unit,0,21*unit,unit),(10,1)],
            'Left':[(0,unit,unit,17*unit),(1,16)],
            'Right':[(11*unit,unit,12*unit,17*unit),(1,16)],
            'Front':[(unit,unit,11*unit,17*unit),(10,16)],
            'Back':[(12*unit,unit,22*unit,17*unit),(10,16)]}
        for key in dict:
            myModifier.AddImg(key,cloak.crop(dict[key][0]),dict[key][1])
            my3DViewer.blockList[0].SetImg(key,myModifier.GetImg(key))
        myCrop_Front.LoadImage(myModifier.GetImg('Front'))
        myCrop_Back.LoadImage(myModifier.GetImg('Back'))
        SetCloakInfo()
        my3DViewer.Work()
def InterfaceInit():#所有内容的初始化
    myCrop_Front.LoadImage(Image.open('Back.png'))
    myCrop_Back.LoadImage(Image.open('Back.jpg'))
    myModifier.AddImg('Front',myCrop_Front.GetCroppedImg(),(10,16))
    myModifier.AddImg('Back',myCrop_Back.GetCroppedImg(),(10,16))
    bar_Scale.config(to=max(myCrop_Front.GetMultiple(),myCrop_Back.GetMultiple()))
    bar_Scale.myInt.set(int(bar_Scale.config('to')[4]))
    myModifier.SetMultiple(bar_Scale.myInt.get())
    my3DViewer.blockList[0].SetImg('Front',myModifier.GetImg('Front'))
    my3DViewer.blockList[0].SetImg('Back',myModifier.GetImg('Back'))

    dict={'U':['Up',(10,1)],'D':['Down',(10,1)],'L':['Left',(1,16)],'R':['Right',(1,16)]}
    for key in dict:
        myCv=eval('myCv{}'.format(key))
        myModifier.AddImg(dict[key][0],Image.new('RGBA',(1,1),myCv.canvas.config('bg')[4]),dict[key][1])
        my3DViewer.blockList[0].SetImg(dict[key][0],myModifier.GetImg(dict[key][0]))
    SetCloakInfo()
    my3DViewer.Work()

#功能绑定
myCrop_Front.SetCallBackFunc(CallBackFunc_Front)
myCrop_Back.SetCallBackFunc(CallBackFunc_Back)
menu_LoadBar.add_command(label="正面图",command=LoadImg_Front)
menu_LoadBar.add_command(label="背面图",command=LoadImg_Back)
menu_LoadBar.add_command(label="披风文件",command=LoadImg_Cloak)
menu_SaveBar.add_command(label="披风文件",command=lambda :SaveImg(GetClock()))
menu_HelpBar.add_command(label="使用介绍",command=None)
menu_HelpBar.add_command(label="版本",command=None)
freeCutting_Front.config(command=lambda:myCrop_Front.FreeCutting(bool(freeCutting_Front.myVar.get())))
freeCutting_Back.config(command=lambda:myCrop_Back.FreeCutting(bool(freeCutting_Back.myVar.get())))
bar_Scale.config(command=lambda Event:DragBarScale())
myCvU.mouse.FuncClick=lambda :SetColor('U')
myCvD.mouse.FuncClick=lambda :SetColor('D')
myCvL.mouse.FuncClick=lambda :SetColor('L')
myCvR.mouse.FuncClick=lambda :SetColor('R')
bt_CloakSize.config(command=GetCloakSize)

InterfaceInit()
tk.update()#鬼知道为啥得执行这条语句(这还是拍脑袋想到的)，不执行的话部分组件不能正常初始化显示
tk.bind("<Configure>",lambda Event:myCrop_Front.FreshRootCoord() is myCrop_Back.FreshRootCoord())#绑定坐标刷新函数，以便不会出现偏移问题
tk.mainloop()




#filepath = askopenfilename(filetypes=[('png','.png')])
#filenewpath = asksaveasfilename(filetypes=[('png','.png')])   # 设置保存文件，并返回文件名，指定文件名后缀为.png
