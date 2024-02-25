from LINGVA_CALCVLI_PARSER import parser

class compiler():
    def __init__(self) -> None:
        self.parser = parser
    def printTree(self,statement):
        #breaks down code and makes it more readable
        if statement[0][0] == '@':
            print(statement)
            return
        else:
            print(statement[0],end=" ")
            for ele in statement[1:]:
                self.printTree(ele)
            return
    def compile(self,code):
        parsedCode = self.parser.parse(code)
        for statement in parsedCode:
            self.printTree(statement)

compiler = compiler()

compiler.compile("""IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
DICERE 'SALVE MVNDI'
SI VERVM TVNC
DICERE 'op one'
SI VERVM TVNC
DICERE 'hello'
FINIS FINIS_CIRCVITVS
FINIS SIN VERVM TVNC
DICERE 'op two'
FINIS ALITER TVNC
DICERE 'op three'
FINIS
FINIS_CIRCVITVS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
""")