from math import cos,sin,tan
import numpy as np
import cv2

class Block:#方块
    __SurfaceToPoints={'Front':(0,1,2,3),'Back':(4,5,6,7),'Left':(7,6,1,0),'Right':(3,2,5,4),'Up':(7,0,3,4),'Down':(1,6,5,2)}#面点对应关系(还是带顺序的
    __SurfacePoints={'Front':0x0F,'Back':0xF0,'Left':0xC3,'Right':0x3C,'Up':0x99,'Down':0x66}#索引,方便判断哪个被隐盖的点所关联的面是不用显示的。用位判断(更快，更爽
    __ImgsOrder=['Front','Back','Left','Right','Up','Down']
    def __init__(self,points,cvImgs=None):
    #points为列表，是方块的八个顶点(三元元组)，分别是前面的四个顶点和后面的四个顶点，顺序为从左上角开始的逆时针
    #points:[左上(前),左下(前),右下(前),右上(前),左上(后),左下(后),右下(后),右上(后)]
    #cvImgs:为列表，是方块的六个面，最好就大小合理点，要不然会让方块不闭合或者方块某个面伸出。图片格式为cv2读取的图片
    #cvImgs:[前,后,左,右,上,下]。如果某个面不需要图那直接None
        self.points=[]
        for P in points:
            self.points.append(list(P)+[1])#制作成4维向量
        self.points=np.matrix(self.points)#制作成矩阵，方便运算
        self.imgs={}
        if(type(cvImgs)!=list):
            cvImgs=[None]*6
        for key in Block.__ImgsOrder:
            self.imgs[key]=cvImgs[len(self.imgs)]
    def GetMatrix(Camera,ViewSize):#根据相机位置返回变换矩阵
        sinA=sin(Camera.a)
        sinB=sin(Camera.b)
        cosA=cos(Camera.a)
        cosB=cos(Camera.b)
        r=Camera.r

        Matrix=np.matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[r*cosA*cosB,r*sinA*cosB,r*sinB,1]])#投影中心移动到原点
        Matrix=Matrix*np.matrix([[cosA,sinA,0,0],[sinA,-cosA,0,0],[0,0,1,0],[0,0,0,1]])#绕z转动-a角度
        Matrix=Matrix*np.matrix([[sinB,0,cosB,0],[0,1,0,0],[-cosB,0,sinB,0],[0,0,0,1]])#绕y转动pi/2-b角度
        Matrix=Matrix*np.matrix([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])#绕z转动-pi/2角度
        
        d_CameraToView=20#镜头到观察面距离。观察面与前后截面的距离固定为0.8*d【这参数为啥发挥不了作用】
        Matrix=Matrix*np.matrix([[(10/9)/ViewSize[0],0,0,0],[0,(10/9)/ViewSize[1],0,0],[0,0,(5/9)/d_CameraToView,0],[0,0,0,1]])#比例变换变成规范化透视投影
        Matrix=Matrix*np.matrix([[1,0,0,0],[0,1,0,0],[0,0,2.5,1],[0,0,-1.5,0]])#变换成规范化平行投影
        return Matrix
    def GetImg(self,Camera,VSize):#转换图片，获取映射变化后的图片，格式仍为cv2(格式稍加转换就可打到canvas上显示
        VSizeHalf=(int(VSize[0]/2),int(VSize[1]/2))
        TM=Block.GetMatrix(Camera,VSize)*100*Camera.r#转换矩阵(顺带把它给放大一下

        Points=[]#取出转换后的点
        for P in self.points*TM:
            Points.append((VSizeHalf[0]+P[(0,0)],VSizeHalf[1]+P[(0,1)],P[(0,2)]))#取出P的坐标
        nullP=[0]#被隐盖的点(必然有一个，但有可能有多个，所以用列表
        for pst in range(8):
            dist=Points[pst][2]-Points[nullP[0]][2]
            if dist==0:
                nullP.append(pst)
            elif dist<0:
                nullP=[pst]
        if(nullP.count(0)==2):#【经典翻车事故】
            nullP.remove(0)
        nullP.append(0)
        for pst in nullP[:-1]:#也是将它转换为位的方式，一样的理由———更快、更爽
            nullP[-1]+=(1<<pst)
        nullP=nullP[-1]
        
        targetImg=np.zeros((VSize[0],VSize[1],3),np.uint8)
        for key in Block.__ImgsOrder:#逐个显示图片
            if(Block.__SurfacePoints[key]&nullP):#如果命中了就说明这个面有顶点是无效的，即这个面不需要显示
                continue
            if(type(self.imgs[key]) is not np.ndarray):#如果是空的那就跳过本段
                continue
            args=self.imgs[key].shape#图片的高宽
            before=np.float32([[0,0],[0,args[0]],[args[1],args[0]]])#取3个点就够了
            after=[]
            for i in Block.__SurfaceToPoints[key][:3]:
                after.append([Points[i][0],Points[i][1]])
            after=np.float32(after)
            targetImg=cv2.add(targetImg,cv2.warpAffine(self.imgs[key],cv2.getAffineTransform(before,after),tuple(VSize),flags=cv2.INTER_NEAREST))#仿射变换，并将结果加入到targetImg中
        return targetImg
    def SetImg(self,surfaceName,img):
        if(Block.__ImgsOrder.count(surfaceName)==1):
            if(type(img)==np.ndarray):
                self.imgs[surfaceName]=img
            else:
                self.imgs[surfaceName]=cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)