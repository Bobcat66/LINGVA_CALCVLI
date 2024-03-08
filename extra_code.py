import NVMERVS_ROMANVS as num

class VARIABLE():
    varType = 'NONE'

    def __init__(self,value):
        self.value = value
    
    def STRING(self):
        val = []
        for ele in self.__str__():
            val.append(CHAR(ele))
        return STRING(val)

class NUMBER(VARIABLE):
    varType = "NUMBER"
    
    def __str__(self):
        return num.to_RomNum(self.value)

class RATIO(VARIABLE):
    varType = "RATIO"
    
    def __str__(self):
        return num.to_RomNum(self.value)

class BOOLEAN(VARIABLE):
    varType = "BOOLEAN"

    def __str__(self):
        return "VERVM" if self.value == True else "FALSVM"

class CHAR(VARIABLE):
    varType = "CHAR"

    def __str__(self):
        return str(self.value)
    
    def STRING(self):
        return STRING(self.value)
    
    def PRINT(self):
        print(self.value)

class ARRAY():
    def __init__(self,size,type,elements=[]):
        self.size = size
        self.type = type
        self.elements = elements
    
    def EDIT_ARR(self,index,value):
        self.elements[index] = value
    
    def ASSIGN_ARR(self,new_arr):
        self.elements = new_arr

    def DELETE_ELE(self,index):
        self.elements.pop(index)
        self.size -= 1

    def __str__(self):
        return str(self.value)
    
    def STRING(self):
        val = []
        for ele in self.__str__():
            val.append(CHAR(ele))
        return STRING(val)
        

class STRING(ARRAY):
    def __init__(self,chars):
        size = len(chars)
        super().__init__(size=size,type='CHAR',elements=chars)
    
    def PRINT(self):
        for chr in self.elements:
            chr.PRINT()

  