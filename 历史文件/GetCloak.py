#使用说明：
#①正反面的大小要一致
#②正面的宽是10的倍数，高是16的倍数
#③正面的宽高比是10:16

from PIL import Image

frontPict="正面.jpg"
backPict="背面.jpg"
cloakPict="披风.png"
ColorU=(255,0,0)#上位置颜色
ColorD=(0,255,0)#下位置颜色
ColorL=(0,0,255)#左位置颜色
ColorR=(255,255,0)#右位置颜色

def GetCloak(frontPictName,backPictName,cloakName):
	front=Image.open(frontPictName)
	back=Image.open(backPictName)

	if(front.size!=back.size):#如果正背面的图片尺寸不一致那退出
		return None
	if(front.size[0]%10!=0):#如果正面的宽不是10的倍数则退出
		return None
	if(front.size[1]%16!=0):#如果正面的高不是16的倍数则退出
		return None
	if(front.size[0]/10!=front.size[1]/16):#如果正面的宽高比并不是10:16则退出
		return None
	unit=int(front.size[0]/10) #unit为单位长度
	
	cloak=Image.new("RGBA",(64*unit,32*unit))#披风~
	cloak.paste(Image.new("RGB",(10*unit,unit),ColorU),(unit,0))#上位置
	cloak.paste(Image.new("RGB",(10*unit,unit),ColorD),(11*unit,0))#下位置
	cloak.paste(Image.new("RGB",(unit,16*unit),ColorL),(0,unit))#左位置
	cloak.paste(Image.new("RGB",(unit,16*unit),ColorR),(11*unit,unit))#右位置
	cloak.paste(front,(unit,unit))#正披风
	cloak.paste(back,(12*unit,unit))#背披风	
	cloak.save(cloakName);

GetCloak(frontPict,backPict,cloakPict)


