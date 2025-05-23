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
        'printl' : [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,
                    0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X0A,0X18,0X00,
                    0X00,0X21], #0

        'print' :  [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,
                    0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X00,0X21], #1

        'prompt' : [0X08,0X00,0X00,0X00,0X22,0X00,0X00,0X22,0X00,0X00,0X22,0X0C,0X00,0X1F,0X11,0X02,
                    0X0C,0X02,0X0C,0X03,0X12,0X00,0X0F,0X0C,0X00,0X0C,0X03,0X1D,0X18,0X0B,0X03,0X01,
                    0X0A,0XFF,0XF0,0X2B,0X2D,0X01,0X00,0X01,0X03,0X19,0X0C,0X01,0X2C,0X19,0X0D,0X00,
                    0X12,0X00,0X01,0X03,0X2D,0X1A,0X01,0X0C,0X01,0X2E,0X03,0X2D,0X1E,0X0A,0XFF,0XF0,
                    0X0C,0X01,0X21], #2

      'toRomnum' : [0X08,0X00,0X0C,0X00,0X3C,0X19,0X0C,0X01,0X2C,0X00,0X01,0X03,0X19,0X0D,0X00,0X12,
                    0X2D,0X1A,0X01,0X2D,0X0C,0X01,0X2E,0X03,0X1E,0X00,0X01,0X03,0X0A,0XFF,0XF0,0X0C,
                    0X01,0X2E,0X03,0X1E,0X0C,0X01,0X21], #3

       'promptn' : [0X08,0X00,0X35,0x08,0x00,0x03,0x01,0x22,0x00,0x00,0x22,0x00,0x00,0x22,0x00,0x00, 
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
        self.code = self.__compileStmtLst(self.AST)
        #print(self.heap)
        self.__compileHeap()
        self.__compileSymbols()
        return (self.heap,self.symbols,self.lvars,self.code)

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
    
    def __compileHeap(self):
        #compiles heap. Only use at the very end
        newHeap = [(ele[0],bool(ele[1]),ele[2:]) for ele in self.heap if ele is not None]
        self.heap = newHeap

    def __addSymbol(self,obj,type):
        #Adds object to symbols
        #Returns object's position in symbol table
        #NOTE: type must be MCS symbol type, not LINGVA_CALCVLI or COMPILATOR type
        pos = len(self.symbols)
        self.symbols.append((type,obj))
        return pos

    def __addVar(self,obj,scope):
        pos = len(self.localVars[scope])
        self.localVars[scope].append(obj)
        return pos

    def __compileSymbols(self):
        #Compiles symbol table. Should be done at the very end. TODO: remove placeholder symbols
        #print(self.symbols)
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
            #TODO: Add global alias support. Also see variable code
            #self.globalAliases[ele] = {}
            #self.localAliases[ele] = {}
            pass
        for ele in self.terminals['NUMBER']:
            nums.add(ele)
        for ele in self.terminals['RATIO']:
            nums.add(ele)
        #print(nums)

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
                    print(self.globalAliases)
                    print(self.localAliases)
                    return "ERROR"
                elif idName in self.globalAliases.keys():
                    code = [0x00,self.globalAliases[idName][scope][0]]
                elif idName in self.localAliases.keys():
                    #TODO: Add float support
                    code = [0x0c,self.localAliases[idName][scope][0]]

            #Binary Arithmetic Operators
            case 'ADD':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x02]
            case 'SUBTRACT':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x03]
            case 'MULTIPLY':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x04]
            case 'DIVIDE':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x05]
            
            #Boolean Operators
            case 'AND':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x06]
            case 'OR':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x07]
            case 'XOR':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x08]
            case 'NOT':
                op1 = self.__compileExpr(expr[1])
                code = op1 + [0x09]
            
            #Comparators
            case 'EQUALS':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                #print(op1,op2)
                code = op1 + op2 + [0x3f]
            case 'GREATER':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x41]
            case 'LESSER':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x42]
            case 'GREATER_OR_EQUAL':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x43]
            case 'LESSER_OR_EQUAL':
                op1 = self.__compileExpr(expr[1])
                op2 = self.__compileExpr(expr[2])
                code = op1 + op2 + [0x44]
            
            #Arrays
            case 'RETRIEVE_ELE':
                #TODO: Add support for floats, and booleans
                arrname = self.__compileExpr(expr[1])
                arrPos = self.__compileExpr(expr[2])
                arrType = self.globalAliases[arrname][scope][1]
                match arrType:
                    case "STRING_ARRAY":
                        code = arrname + arrPos + [0x1d]
                    case "NUMBER_ARRAY":
                        code = arrname + arrPos + [0x1d]
                    case "FLOAT_ARRAY":
                        code = arrname + arrPos + [0x24]
            
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
                if not id in self.localAliases.keys():
                    self.localAliases[id] = {}
                pos = self.__addVar(None,scope)
                print(self.localVars)
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
                print("Alias: ", alias)
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
                #TODO: Fix, add variable obj size, add references
                arrName = stmt[1][1]
                arrSize = self.__compileExpr(stmt[2],scope)
                arrType = stmt[3][1]
                match arrType:
                    #TODO: Add boolean
                    case 'STRING':
                        pos = self.__addHeap(None,'RARR')
                    case 'NUMBER':
                        pos = self.__addHeap(None,'IARR')
                    case 'RATIO':
                        pos = self.__addHeap(None,'FARR')
                if arrName not in self.globalAliases.keys():
                    self.globalAliases[arrName] = {}
                self.globalAliases[arrName][scope] = (pos,arrType+"_ARRAY")
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
                #return arrSize + [0x00,typeCode,0x00,0x00,0x00,size,0x3e]
                return []
            case "$EDIT_ARR":
                #TODO: Add wide support, fix
                arrNameCode = self.__compileExpr(stmt[1],scope)
                #print(arrNameCode)
                arrIndexCode = self.__compileExpr(stmt[2],scope)
                arrValCode = self.__compileExpr(stmt[3],scope)
                code = []
                arrCode = self.globalAliases[stmt[1][1]][scope][0]
                #print(stmt[3][1])
                if isinstance(stmt[3][1],int):
                    code = [0x1e,arrCode,arrIndexCode,arrValCode]
                elif isinstance(stmt[3][1],float):
                    code = [arrCode,arrIndexCode,arrValCode]
                else:
                    print("Arrindcod", arrIndexCode)
                    code = [0x1e] + [arrCode] + arrIndexCode + arrValCode
                return code
            case "$ASSIGN_ARR":
                #TODO: FINISH, add wide support (also add wide support to 0x45 command in MCS)
                #TODO: Make sure Assign Arr only works with arrays
                oldArr = stmt[1][1]
                newArr = stmt[2][1]
                oldSymbolIndex = self.globalAliases[oldArr][scope][0]
                newSymbolIndex = self.globalAliases[newArr][scope][0]
                newSymbol = self.symbols(newSymbolIndex)
                return [0x45,oldSymbolIndex,mcs.stack_machine.ref_dict[newSymbol[0]]] + list(mcs.intToBytes(newSymbol[1],size=32))
            case "$DELETE_ELE":
                #TODO: FINISH
                arrName = stmt[1][1]
                arrIndexCode = self.__compileExpr(stmt[2])
                arrCode = self.globalAliases(arrName,scope)
                pass
            case "$APPEND":
                #TODO: Add support for ints and refs
                arrName = stmt[1][1]
                arrCode = self.globalAliases(arrName,scope)
                newEle = self.__compileExpr(stmt[2])
                return [0x00,0x01,0x00,arrCode,0x34,0x00,arrCode,0x19,0x1f,0x00,0x01,0x03] + newEle + [0x1e]
            case "$IF":
                #Constructs if statement
                #TODO: Test offsets
                allCode = []
                for ifStmt in stmt[1:]:
                    if ifStmt[0] == "ELSE":
                        #TODO: Increase code limit of ifStmt Else
                        code = self.__compileStmtLst(ifStmt[1])
                        clen = len(code)
                        code = [0x46] + list(mcs.intToBytes(clen + 5,size=32)) + code
                    else:
                        code = self.__compileStmtLst(ifStmt[2])
                        clen = len(code)
                        if clen > 32740:
                            remainLen = clen - 32740
                            remainLenList = mcs.intToBytes(10 + remainLen,size=32)
                            #Added small buffer to code length
                            code.insert(32740,0x0a) #Go forward by 6
                            code.insert(32741,0x00)
                            code.insert(32742,0x06)
                            code.insert(32743,0x46)
                            code.insert(32744,remainLenList[0])
                            code.insert(32745,remainLenList[1])
                            code.insert(32746,remainLenList[2])
                            code.insert(32747,remainLenList[3])
                            code = self.__compileExpr(ifStmt[1]) + [0x0d,0x7f,0xea] + code
                        else:
                            code = self.__compileExpr(ifStmt[1]) + [0x0d] + list(mcs.intToBytes(len(code) + 8,size=16)) + code

                        if ifStmt[0] == "ELIF":
                            clen = len(code)
                            code = [0x46] + list(mcs.intToBytes(clen + 5,32)) + code
                    allCode.extend(code)
                return allCode
            case '$WHILE':
                #Constructs while statement
                #TODO: Add offset for longer code segments
                condition = self.__compileExpr(stmt[1])
                statements = self.__compileStmtLst(stmt[2])
                statementLen = len(statements)
                code = condition + [0x0d] + list(mcs.intToBytes(statementLen+6,16)) + statements + [0x0a] + list(mcs.intToBytes(-1*(statementLen+3+len(condition)),16))
                return code
                

                    

            

    def __compileStmtLst(self,stmtList,scope='MAIN'):
        #Compiles statement list
        code = []
        for stmt in stmtList:
            code += self.__compileStmt(stmt)
        return code

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

ifTest = '''
IMPERO TIBI
SI PAR SVMMA NO. III NO. II NO. VII TVNC
    DICERE 'SALVE MVNDI I'
FINIS SIN PAR SVMMA NO. II NO. III NO. VI TVNC
    DICERE 'SALVE MVNDI II'
FINIS SIN PAR SVMMA NO. IV NO. II NO. VI TVNC
    DICERE 'SALVE MVNDI III'
FINIS ALITER TVNC
    DICERE 'SALVE MVNDI IV'
FINIS
FINIS_CIRCVITVS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM'''

whileTest = '''
IMPERO TIBI
DECLARO VARIABLE NVMERVS
ASSIGNO VARIABLE NO. VI
DVM NON PAR VARIABLE NO. I TVNC
    DICERE 'SALVE MVNDI\n'
    DECREMENTVM VARIABLE
FINIS
FINIS_CIRCVITVS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM'''

arrTest = '''
IMPERO TIBI
ORDO_DECLARO ARRAY NO. V SCRIPTVM
DECLARO COVNTER NVMERVS
ASSIGNO COVNTER NO. I
ORDO_IMMVTO ARRAY NO. I 'SALVE MVNDI I'
ORDO_IMMVTO ARRAY NO. II 'SALVE MVNDI II'
ORDO_IMMVTO ARRAY NO. III 'SALVE MVNDI III'
ORDO_IMMVTO ARRAY NO. IV 'SALVE MVNDI IV'
ORDO_IMMVTO ARRAY NO. V 'SALVE MVNDI V'
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
    '''

ifCode = '''
PUSH 02
PUSH 02
ADD
PUSH 04
EQL
IFEQ 00 0E
LREF 01
LREF 07
CALL 01'''
ap = parser.parse(arrTest)
#print(ap)
compier = compiler()
apc = compier.compile(ap)
'''
for ele in apc:
    print(ele)


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
'''
print(compier.code)
print(mcs.stack_machine.decompileInstructions(compier.code))
#print(apc)
exe = mcs.stack_machine()
exe.initialize(apc[0],apc[1],apc[2],apc[3])
exe.execute()
print(exe)

#print(compier.processUInt(6554634))