from LINGVA_CALCVLI_PARSER import parser
import MACHINA_SIMVLATA as mcs


#COMPILATION PROCEDURE
#FIND TERMINALS
#COMPILE TERMINALS
#FIND AND DEFINE FUNCTIONS
#COMPILE STATEMENTS INTO CODE
#TODO: FIX LISTS
class compiler():
    standard_lib = {
        'printl' : [0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,0X0C,0X00,
                    0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X0A,0X18,0X00,0X00,0X21], #0

        'print' :  [0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,0X0C,0X00,
                    0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X00,0X21], #1

        'prompt' : [0X00,0X00,0X22,0X00,0X00,0X22,0X00,0X00,0X22,0X0C,0X00,0X1F,0X11,0X02,0X0C,0X02,
                    0X0C,0X03,0X12,0X00,0X0F,0X0C,0X00,0X0C,0X03,0X1D,0X18,0X0B,0X03,0X01,0X0A,0XFF,
                    0XF0,0X2B,0X2D,0X01,0X00,0X01,0X03,0X19,0X0C,0X01,0X2C,0X19,0X0D,0X00,0X12,0X00,
                    0X01,0X03,0X2D,0X1A,0X01,0X0C,0X01,0X2E,0X03,0X2D,0X1E,0X0A,0XFF,0XF0,0X0C,0X01, #2
                    0X21],

      'toRomnum' : [0X0C,0X00,0X3C,0X19,0X0C,0X01,0X2C,0X00,0X01,0X03,0X19,0X0D,0X00,0X12,0X2D,0X1A,
                    0X01,0X2D,0X0C,0X01,0X2E,0X03,0X1E,0X00,0X01,0X03,0X0A,0XFF,0XF0,0X0C,0X01,0X2E,
                    0X03,0X1E,0X0C,0X01,0X21], #3

       'promptn' : [0x08,0x00,0x35,0x08,0x00,0x03,0x01,0x22,0x00,0x00,0x22,0x00,0x00,0x22,0x00,0x00, 
                    0x22,0x0C,0x00,0x1F,0x11,0x02,0x0C,0x02,0x0C,0x03,0x12,0x00,0x0F,0x0C,0x00,0x0C, 
                    0x03,0x1D,0x18,0x0B,0x03,0x01,0x0A,0xFF,0xF0,0x2B,0x2D,0x01,0x00,0x01,0x03,0x19, 
                    0x0C,0x01,0x2C,0x19,0x0D,0x00,0x12,0x00,0x01,0x03,0x2D,0x1A,0x01,0x0C,0x01,0x2E, 
                    0x03,0x2D,0x1E,0x0A,0xFF,0xF0,0x0C,0x01,0x21], #4
      
    }
    def __init__(self):
        self.AST = []
        self.terminals = {
            #Lists all terminal expressions in the code
            #The items in this are immutable
            'STRING' : set(), #ALSO CONTAINS PROMPT STRINGS
            'TYPE' : set(),
            'NUMBER' : set(),
            'BOOLEAN' : set(),
            'RATIO' : set(),
            'ID' : set(),
        }
        
        self.funcs = {} #List of functions to process
        self.compiledFuncs = {} #List of processed funcs
        self.scopes = ['MAIN'] #Scopes
        self.localVars = { #Localvars for each scope
            'MAIN' : [],
        }
        self.heap = []
        self.symbols = []
        self.lvars = []
        self.code = []
        i = 0
        for func in self.standard_lib.values():
            self.heap.append(func)
            self.symbols.append(('FUNC',i))
            i += 1

        self.globalAliases = {} 
        #Each alias value should be a dict of tuples.
        #Each value should be of format SCOPE: (INDEX,TYPE), 
        #where INDEX is the position within the symbol table, 
        #and scope is the scope of the variable w/in the program. 
        #NOTE: Aliases are only for variables stored in the heap. 
        #Aliases for variables stored in local memory are tracked in self.localvariables

        self.localAliases = {} #Each alias value should be a dict of tuples. 
        #Each value in the dict of format SCOPE: (INDEX,TYPE), where INDEX is the position within the local variables. 
        #NOTE: localAliases are only for values stored in local variables. Also, localAliases stores all localAliases for all scopes
        #Alias dicts are for converting human readable ids into positions in the symbol table/local table
        self.constAliases = {}#For constants within the symbol table. Same format as localAliases
    
    def compile(self,AST):
        self.AST = AST
        self.getTerms(AST)
        self.__compileConsts()
    
    def getTerms(self, obj):
        #gets terminal terms. obj is a list of statements
        for stmt in obj:
            self.__getTermsStmt(stmt)
    
    def __getTermsStmt(self,obj):
        #Gets terminal terms. obj is a statement
        match obj[0]:
            case '$IF':
                for ifSt in obj[1:]:
                    if ifSt[0] == "ELSE":
                        self.getTerms(ifSt[1])
                    else:
                        self.__getTermsExpr(ifSt[1])
                        self.getTerms(ifSt[2])
            case '$WHILE':
                self.__getTermsExpr(obj[1])
                self.getTerms(obj[2])
            case '$DECLARE_FUNCTION':
                self.__getTermsExpr(obj[1][0])
                self.__getTermsExpr(obj[1][1])
                if obj[1][2] is not None:
                    for ele in obj[1][2]:
                        self.__getTermsExpr(ele)
                self.getTerms(obj[2])
            case '$CALL_FUNCTION':
                self.__getTermsExpr(obj[1])
                if obj[2] is not None:
                    self.__getTermsXpl(obj[2])
            case _:
                self.__getTermsXpl(obj[1:])
                    
    def __getTermsXpl(self,obj):
        #Gets terminal terms. obj is an expression list
        for ele in obj:
            self.__getTermsExpr(ele)
    
    def __addHeap(self,obj,type):
        #adds object to heap, and modifies symbol table
        #Returns object's pointer's position in symbol table
        pos = len(self.symbols)
        self.symbols.append((type,len(self.heap)))
        self.heap.append(obj)
        return pos
    
    def __addSymbol(self,obj,type):
        #Adds object to symbols
        #Returns object's position in symbol table
        #NOTE: type must be MCS symbol type, not LINGVA_CALCVLI or COMPILATOR type
        pos = len(self.symbols)
        self.symbols.append((type,obj))
        return pos

    def __addVar(self,obj,scope):
        pos = len(self.localVars[scope])
        self.localVars[scope].append[obj]
        return pos

    def __compileSymbols(self):
        #Compiles symbol table. Should be done at the very end. TODO: remove placeholder symbols
        newSymbols = [(mcs.stack_machine.ref_dict[ele[0]],ele[1]) for ele in self.symbols]
        self.symbols = newSymbols

    def __getTermsExpr(self,obj):
        #Gets terminal terms. obj is an expression

        if obj[0] == "CALL_FUNCTION":
            self.__getTermsExpr(obj[1])
            if obj[2] is not None:
                self.__getTermsXpl(obj[2])
            return
            
        if obj[0][0] == '@':
            self.terminals[obj[0][1:]].add(obj[1])
            return
        else:
            for ele2 in obj[1:]:
                self.__getTermsExpr(ele2)
    
    def __compileConsts(self):
        #Compiles constants. DOES NOT COMPILE ALIASES
        nums = set()
        for ele in self.terminals['ID']:
            self.globalAliases[ele] = {}
            self.localAliases[ele] = {}
        for ele in self.terminals['NUMBER']:
            nums.add(ele)
        for ele in self.terminals['RATIO']:
            nums.add(ele)
        print(nums)

        for ele in nums:
            pos = self.__addSymbol(ele,"CONST")
            self.constAliases[ele] = pos

        for ele in self.terminals['STRING']:
            #Strings are immutable
            strList = [8,0] + [ord(char) for char in ele]
            pos = self.__addHeap(strList,'STRING')
            self.constAliases[ele] = pos

    def __compileExpr(self,expr,scope='MAIN'):
        #Compiles Expr. The code should resolve so that the value of the expression is at the top of the stack
        name = expr[0]
        code = []
        match name:
            case '@STRING':
                strRef = self.constAliases[expr[1]]
                code += [0x1b,strRef]
                #TODO: Add wide modifier
            case '@BOOLEAN':
                bool = expr[1]
                if bool:
                    code = [0x00,0x01]
                else:
                    code = [0x00,0x00]
            case '@NUMBER':
                num = expr[1]
                if num > 65535:
                    code = [0x33,0x00] + list(mcs.intToBytes(num))
                elif num > 65535:
                    code = [0x32,0x00] + list(mcs.intToBytes(num,size=16))
                else:
                    code = [0x00,num]
            case '@RATIO':
                num = expr[1]
                bytes = list(mcs.intToBytes(mcs.floatToInt(num)))
                code = [0x33,0x00] + bytes
            case '@PROMPT':
                promptCode = self.__compileExpr(expr[1])
                code = [0x0c,0x04] +  promptCode + [0x20,0x01]
            case '@ID':
                #TODO: Add wide support
                idName = expr[1]
                if idName in self.globalAliases.keys() and idName in self.localAliases.keys():
                    #TODO: raise compiler error here
                    return "ERROR"
                elif idName in self.globalAliases.keys():
                    code = [0x00,self.globalAliases[idName][scope][0]]
                elif idName in self.localAliases.keys():
                    #TODO: Add float support
                    code = [0x00,self.localAliases[idName][scope][0],0x0c]
            
        return code

    def __compileStmt(self,stmt,scope='MAIN'):
        #compiles a statement into code. Returns the code sequence for each statement
        name = stmt[0]
        match name:
            case "$DECLARE_VAR":
                """
                PUSH 0
                NEWVAR
                """
                id = stmt[1][1]
                type = stmt[2][1]
                pos = self.__addVar(None,scope)
                if not scope in self.localAliases[id]:
                    #TODO: Raise error of some kind
                    pass
                self.localAliases[id][scope] = (pos,type) #Type is LINGVA_CALCVLI type
                return [0x00,0x00,0x22]
            case "$ASSIGN_VAR":
                #TODO: FIX
                """
                for floats
                <VAL CODE>
                FSTORE <ALIAS> 
                for ints/bools
                <VAL CODE>
                RISTORE <ALIAS>
                for strings
                <VAL CODE>
                RISTORE <ALIAS> //stores reference into variable
                """

                id = stmt[1][1]
                val = self.__compileExpr(stmt[2])
                type = stmt[2][0][1:]
                alias = self.localAliases[id][scope] #(pos,type)
                if type != alias[1]:
                    #TODO: Raise error of some kind
                    pass
                code = []
                if alias[0] >= (1 << 16):
                    code.append(0x33)
                elif alias[0] >= (1 << 8):
                    code.append(0x32)
                #code += self.processUInt()
                if type == 'FLOAT':
                    code.append(0x26)
                else:
                    code.append(0x11)
                code += self.processUInt(alias[0])
                return val + code
            case "$PRINT":
                code = [0x1b,0x01]
                code += self.__compileExpr(stmt[1])
                code += [0x20,0x01]
                return code
            case "$INCREMENT":
                varName = stmt[1][1]
                varCode = self.localAliases[varName][scope] #(pos,type)
                if varCode[0] > 255:
                    code = [0x0f] + list(mcs.intToBytes(varCode[0],size=16)) + [0x00,0x01]
                else:
                    code = [0x0b,varCode[0],0x01]
                return code
            case "$DECREMENT":
                varName = stmt[1][1]
                varCode = self.localAliases[varName][scope] #(pos,type)
                code = [0x0f] + list(mcs.intToBytes(varCode[0],size=16)) + [0xff,0xff]
                return code
            case "$DECLARE_ARR":
                #TODO: Fix, add variable obj size
                arrName = stmt[1][1]
                arrSize = self.__compileExpr(stmt[2],scope)
                arrType = stmt[3][1]
                pos = self.__addHeap(None,'ARRAY')
                self.globalAliases[arrName][scope] = pos
                typeCode = 0x00
                size = 32
                match arrType:
                    case 'STRING':
                        typeCode = 0x07
                        size=8
                    case 'NUMBER':
                        typeCode = 0x04
                        size=32
                    case 'RATIO':
                        typeCode = 0x06
                        size=32
                    case 'BOOLEAN':
                        typeCode = 0x0c
                        size=8
                return arrSize + [0x00,typeCode,0x00,0x00,0x00,size,0x3e]
            case "$EDIT_ARR":
                #TODO: Add wide support, fix
                arrName = self.__compileExpr(stmt[1],scope)
                arrIndex = self.__compileExpr(stmt[2],scope)
                arrVal = self.__compileExpr(stmt[3],scope)
                code = []
                arrCode = self.globalAliases[arrName][scope]
                if isinstance(arrVal,int):
                    code = [0x1e,arrCode,arrIndex,arrVal]
                elif isinstance(arrVal,float):
                    code = [arrCode,arrIndex,arrVal]
                return code
            case "$ASSIGN_ARR":
                #TODO: FINISH
                oldArr = stmt[1][1]
                newArr = stmt[2][1]
                newCode = self.globalAliases[newArr][scope]
                self.globalAliases[oldArr][scope] = newCode
                pass
            case "DELETE_ELE":
                #TODO: FINISH
                arrName = stmt[1][1]
                arrIndexCode = self.__compileExpr(stmt[2])
                arrCode = self.globalAliases(arrName,scope)
                pass
            case "APPEND":
                #TODO: Add support for ints and refs
                arrName = stmt[1][1]
                arrCode = self.globalAliases(arrName,scope)
                newEle = self.__compileExpr(stmt[2])
                return [0x00,0x01,0x00,arrCode,0x34,0x00,arrCode,0x19,0x1f,0x00,0x01,0x03] + newEle + [0x1e]

    
    def __processTermSymbols(self):
        #processes terminals and adds them to symbols
        pass

    @staticmethod
    def processUInt(n):
        #converts unsigned integer into list of bytes
        if n >= (1 << 16):
            return [(n >> 24),((n % (1 << 24)) >> 16), ((n % (1 << 16)) >> 8), (n % (1 << 8))]
        elif n >= (1 << 8):
            return [(n >> 8),(n % (1 << 8))]
        else:
            return [n]
    
        

b = '''
IMPERO TIBI
SI FALSVM TVNC
    SI VERVM TVNC
        DICERE 'SALVE MVNDI'
    FINIS ALITER TVNC
        DICERE 'SALVE MVNDI'
        SI VEL MAIOR SVMMA NO. VIII NO. VI NO. V MAIOR_VP NO. VI NO. IV TVNC
            DICERE 'op one'
        FINIS SIN MINOR NO. V PROPORTIO NO. I NO. IV TVNC
            DICERE 'op two'
        FINIS ALITER TVNC
            DICERE 'op three'
        FINIS
        FINIS_CIRCVITVS
    FINIS
    FINIS_CIRCVITVS    
FINIS ALITER TVNC
    DECLARO COVNTER NVMERVS
    ASSIGNO COVNTER NO. I
    ORDO_DECLARO ARRAY NO. V NVMERVS
    ORDO_IMMVTO ARRAY NO. I NO. I
    ORDO_IMMVTO ARRAY NO. II NO. II
    ORDO_IMMVTO ARRAY NO. III NO. III
    ORDO_IMMVTO ARRAY NO. IV NO. IV
    ORDO_IMMVTO ARRAY NO. V NO. V
    DVM MINOR_VP COVNTER NO. V TVNC
        DICERE IMAGO EXPROMO ARRAY COVNTER SCRIPTVM
        INCREMENTVM COVNTER
    FINIS
    FINIS_CIRCVITVS
FINIS_CIRCVITVS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM'''

ap = parser.parse(b)
#print(ap)
compier = compiler()
compier.compile(ap)
print('terminals:',compier.terminals)
print()
print('symbols:',compier.symbols)
print()
print('globalAliases:',compier.globalAliases)
print()
print('constAliases:',compier.constAliases)
print()
for ele in compier.heap:
    print(ele)
print(compier.symbols)
#print(compier.processUInt(6554634))