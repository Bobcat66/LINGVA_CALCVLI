from LINGVA_CALCVLI_PARSER import parser

class compiler():
    standard_lib = {
        'printl' : [0X08,0X00,0X0C,0X00,0X1F,0X22,0X00,0X00,0X22,0X0C,0X01,0X0C,0X02,0X12,0X00,0X0F,
                    0X0C,0X00,0X0C,0X02,0X1D,0X18,0X0B,0X02,0X01,0X0A,0XFF,0XF0,0X00,0X0A,0X18,0X00,0X00,0X21],

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