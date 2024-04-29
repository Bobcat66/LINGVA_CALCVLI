from LINGVA_CALCVLI_PARSER import parser
import MACHINA_SIMVLATA as mcs

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
            '@STRING' : [],
            '@TYPE' : [],
            '@NUMBER' : [],
            '@BOOLEAN' : [],
            '@RATIO' : [],
            '@ID' : []
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

        self.aliases = {} #Each alias value should be a list of tuples. Each tuple should be of format (INDEX,SCOPE), where INDEX is the value of the variable within the symbol table, and scope is the scope of the variable w/in the program
        
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
        pos = len(self.heap) #position of object in self.heap
        self.symbols.append((type,pos))
        self.heap.append(obj)
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
            self.terminals[obj[0]].append(obj[1])
            return
        else:
            for ele2 in obj[1:]:
                self.__getTermsExpr(ele2)
    
    def __compileConsts(self):
        #Compiles constants
        for ele in self.terminals['@ID']:
            self.aliases[ele] = None
        nums = set()
        for ele in self.terminals['@NUMBER']:
            nums.add(ele)
        for ele in self.terminals['@RATIO']:
            nums.add(ele)
        print(nums)
        for ele in nums:
            a = self.__addHeap(ele,"CONST")
            self.constAliases[ele] = a
        for ele in self.terminals['@STRING']:
            self.__addHeap(ele,'STRING')
        
    
    def compileStmt(self,stmt):
        #compiles a statement into code
        name = stmt[0]
        match name:
            case "$DECLARE_VAR":
                id = stmt[1][1]
                type = stmt[2][1]
                
                
        

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
print(compier.terminals)
print(compier.symbols)
print(compier.aliases)
print(compier.constAliases)
i = 0
for ele in compier.heap:
    print(ele)
    print(compier.symbols[i])
    i += 1