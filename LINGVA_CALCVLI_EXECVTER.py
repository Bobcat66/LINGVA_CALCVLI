from LINGVA_CALCVLI_PARSER import parser

class compiler():
    def __init__(self) -> None:
        self.parser = parser
            
    def printTree(self,statement):
        #breaks down code and makes it more readable
        if statement[0] == '$WHILE':
            print('WHILE',statement[1])
            print('{')
            for ele in statement[2]:
                #print(ele)
                self.printTree(ele)
            print('}')
        elif statement[0] == '$IF':
            for ele in statement:
                print(ele[0])
                print('{')
                for ele2 in ele[1]:
                    self.printTree(ele2)
                print('}')
        elif statement[0][0] == '$':
            print(statement[0][1:], end=" ")
            for ele in statement[1:]:
                self.printTree(ele)
            print()
        else:
            print(statement, end=" ")

    def compile(self,code):
        parsedCode = self.parser.parse(code)
        for statement in parsedCode:
            self.printTree(statement)

compiler = compiler()

compiler.compile("""IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
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
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
""")

compiler.compile("""""")