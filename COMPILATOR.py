from LINGVA_CALCVLI_PARSER import parser
import MACHINA_SIMVLATA as mcs


#COMPILATION PROCEDURE
#FIND TERMINALS
#COMPILE TERMINALS
#FIND AND DEFINE FUNCTIONS
#COMPILE STATEMENTS INTO CODE
class compiler():
    standard_lib = {
        'printl' : [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,
                    0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X0A,0X18,0X00,
                    0X00,0X21],

        'print' :  [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,
                    0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X00,0X21],

        'prompt' : [0X08,0X00,0X00,0X00,0X22,0X00,0X00,0X22,0X00,0X00,0X22,0X0C,0X00,0X1F,0X11,0X02,
                    0X0C,0X02,0X0C,0X03,0X12,0X00,0X0F,0X0C,0X00,0X0C,0X03,0X1D,0X18,0X0B,0X03,0X01,
                    0X0A,0XFF,0XF0,0X2B,0X2D,0X01,0X00,0X01,0X03,0X19,0X0C,0X01,0X2C,0X19,0X0D,0X00,
                    0X12,0X00,0X01,0X03,0X2D,0X1A,0X01,0X0C,0X01,0X2E,0X03,0X2D,0X1E,0X0A,0XFF,0XF0,
                    0X0C,0X01,0X21],
    }
    def __init__(self):
        self.AST = []
        self.terminals = {
            #Lists all terminal expressions in the code
            'STRING' : [],
            'TYPE' : [],
            'NUMBER' : [],
            'BOOLEAN' : [],
            'RATIO' : [],
            'ID' : [],
            'PROMPT' : [] #TODO: FIX PROMPTS
        }
        
        self.funcs = {} #List of functions to process
        self.compiledFuncs = {} #List of processed funcs
        self.scopes = ['MAIN'] #Scopes
        self.localVars = { #Localvars for each scope
            'MAIN' : [],
        }
        self.heap = [[32,0,0]] #First element in heap is a temporary array, for use in intermediate operations
        self.symbols = [('IARR',i)]
        self.lvars = []
        self.code = []
        i = 1
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
        self.constAliases = {}#For constants within the symbol table
    
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
        #Compiles symbol table. Should be done at the very end
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
            self.terminals[obj[0][1:]].append(obj[1])
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
        pass

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
                val = stmt[2][1]
                type = stmt[2][0][1:]
                valCode = self.__compileExpr(val)
                alias = self.localAliases[id][scope] #(pos,type)
                if type != alias[1]:
                    #TODO: Raise error of some kind
                    pass
                self.localVars[scope][alias[0]] = val
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
                return valCode + code
            case "$PRINT":
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
print(ap)
compier = compiler()
compier.compile(ap)
print(compier.terminals)
print(compier.symbols)
print(compier.globalAliases)
print(compier.constAliases)
i = 0
for ele in compier.heap:
    print(ele)
    #print(compier.symbols[i])
    i += 1

print(compier.processUInt(6554634))