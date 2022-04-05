class MyMouse:
    def __init__(self):
        self.FuncRoll=None#ÖÐ¼ü¹ö¶¯Ê±µ÷ÓÃµÄº¯Êý£¬ÎÞ²Î
        self.FuncDrag=None#×ó¼üÍÏ×§
        self.FuncRelease=None#×ó¼üÊÍ·Å
        self.FuncClick=None#×ó¼ü°´ÏÂ
        self.FuncDoubleClick=None#×ó¼üË«»÷
        self.FuncRightClick=None#ÓÒ¼ü°´ÏÂ
        self.FuncRightDrag=None#ÓÒ¼üÍÏ×§
        self.FuncDoubleRightClick=None#ÓÒ¼üË«»÷
        self.OffsetX=0#Êó±êXÎ»ÒÆ
        self.OffsetY=0#Êó±êYÎ»ÒÆ
        self.RollUp=True#¹öÂÖÏòÉÏ¹ö¶¯
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
