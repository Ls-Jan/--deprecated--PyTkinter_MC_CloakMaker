from MyCropImage import *
from MyViewer import *
from tkinter import *
from PIL import Image
import numpy as np

tk=Tk()
tk.geometry('1200x800')

myCv0=MyCanvas(tk,(600,600),'grey',bdWidth=0)
myVr=MyViewer(myCv0)

myCv1=MyCanvas(tk,(300,480),'grey',bdWidth=0)
myCi1=MyCropImage(myCv1)
myCi1.LoadImage(Image.open('Front.png'))
myCi1.SetUnitWH(10,16)

myCv2=MyCanvas(tk,(300,480),'grey',bdWidth=0)
myCi2=MyCropImage(myCv2)
myCi2.LoadImage(Image.open('Back.jpg'))
myCi2.SetUnitWH(10,16)

myCv0.canvas.grid(row=0,column=0)
myCv1.canvas.grid(row=0,column=1)
myCv2.canvas.grid(row=0,column=2)



myBlock=Block([(-5,-1,8),(-5,-1,-8),(5,-1,-8),(5,-1,8),(5,0,8),(5,0,-8),(-5,0,-8),(-5,0,8)],[cv2.imread("Front.png"),cv2.imread("Back.jpg"),cv2.imread("White.png"),cv2.imread("White.png"),cv2.imread("White.png"),cv2.imread("White.png")])
MyViewer.blockList=[myBlock]

def CallBackFunc_1():
    front=myCi1.GetCroppedImg()
    myBlock.LoadImg('Front',cv2.cvtColor(np.asarray(front),cv2.COLOR_RGB2BGR))
    myVr.Work()
def CallBackFunc_2():
    back=myCi2.GetCroppedImg()
    myBlock.LoadImg('Back',cv2.cvtColor(np.asarray(back),cv2.COLOR_RGB2BGR))
    myVr.Work()
myCi1.SetCallBackFunc(CallBackFunc_1)
myCi2.SetCallBackFunc(CallBackFunc_2)
myVr.Work()

tk.bind("<Configure>",lambda Event:myCi1.FreshRootCoord() is myCi2.FreshRootCoord())#绑定坐标刷新函数，以便不会出现偏移问题
tk.mainloop()

