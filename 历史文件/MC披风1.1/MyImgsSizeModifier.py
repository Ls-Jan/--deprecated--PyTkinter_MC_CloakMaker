import PIL.Image as Image
class MyImgsSizeModifier:
    def __init__(self):
        self.__imgs={}
        self.__imgsAltered={}
        self.__imgsUnitSize={}
        self.__imgsMultiple=1
    def AddImg(self,name,img,unitSize=(1,1)):
        self.__imgs[name]=img
        self.__imgsUnitSize[name]=(int(unitSize[0]) if unitSize[0]>0 else 1,int(unitSize[1]) if unitSize[1]>0 else 1)
        self.__AlterImg(name)
    def DeleteImg(self,name):
        if(list(self.__imgs.keys()).count(name)==1):
            self.__imgs.pop(name)
            self.__imgsUnitSize.pop(name)
            self.__imgsAltered.pop(name)
    def SetMultiple(self,m):
        self.__imgsMultiple=m
        for name in self.__imgs:
            self.__AlterImg(name)
    def GetImg(self,name):#因为这个会频繁调用所以不将图片的大小调整放在这里而转移到另一处
        if(list(self.__imgsAltered.keys()).count(name)):
            return self.__imgsAltered[name]
    def __AlterImg(self,name):
        if(self.__imgsMultiple>0):
            W=self.__imgsUnitSize[name][0]*self.__imgsMultiple
            H=self.__imgsUnitSize[name][1]*self.__imgsMultiple
            self.__imgsAltered[name]=self.__imgs[name].resize((int(W),int(H)),Image.ANTIALIAS)
    
    
    