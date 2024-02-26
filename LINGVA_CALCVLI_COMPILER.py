from LINGVA_CALCVLI_PARSER import parser

class compiler():
    def __init__(self) -> None:
        self.parser = parser
            
    def printTree(self,statement,front=""):
        #breaks down trees and makes them more readable
        if statement[0] == '$WHILE':

            print(front,end="")
            print('WHILE',statement[1])

            print(front,end="")
            print('{')

            for ele in statement[2]:
                #print(ele)
                self.printTree(ele,front=front + "    ")

            print(front,end="")
            print('}')

        elif statement[0] == '$IF':
            for ele in statement[1:]:
                if ele[0] == "ELIF" or ele[0] == "IF":
                    print(front,end="")
                    print(ele[0],ele[1])

                    print(front,end="")
                    print('{')

                    for ele2 in ele[2]:
                        self.printTree(ele2,front=front+"    ")
                    
                    print(front,end="")
                    print('}')

                else:

                    print(front,end="")
                    print(ele[0])

                    print(front,end="")
                    print('{')

                    for ele2 in ele[1]:
                        self.printTree(ele2,front=front+"    ")
                    
                    print(front,end="")
                    print('}')

        elif statement[0][0] == '$':
            print(front,end="")
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

a = """IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
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
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM"""

b = """IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
DICERE 'SALVE MVNDI'
SI VEL MAIOR SVMMA NO. VIII NO. VI NO. V MAIOR_VP NO. VI NO. IV TVNC
DICERE 'op one'
FINIS SIN MINOR NO. V PROPORTIO NO. I NO. IV TVNC
DICERE 'op two'
FINIS ALITER TVNC
DICERE 'op three'
FINIS
FINIS_CIRCVITVS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM"""

c = """IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
SI VERVM TVNC
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
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM"""


compiler.compile(c)