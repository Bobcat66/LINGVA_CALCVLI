from LINGVA_CALCVLI_PARSER import parser

class compiler():
    standard_lib = {
        'printl' : [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X0A,0X18,0X00,0X00,0X21],
        'print' : [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X00,0X21]
    }
    def __init__(self):
        self.AST = []
        self.terminals = {
            #Lists all terminal expressions in the code
            'STRINGS' : [],
            'TYPES' : [],
            'NUMBERS' : [],
            'BOOLS' : [],
            'RATIOS' : []
        }
        self.compiledVals = {
            'HEAP' : [],
            'SYMBOLS' : [],
            'LOCALVARS' : [],
            'CODE' : []
        }
    
    def getTerms(self,AST):
        for ele in AST:
            if ele[0][0] == '@':
                match ele[0]:
                    case '':
                        pass