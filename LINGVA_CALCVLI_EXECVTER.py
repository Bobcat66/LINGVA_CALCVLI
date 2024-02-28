from LINGVA_CALCVLI_PARSER import parser

class executer():
    def __init__(self) -> None:
        self.parser = parser
        self.memory = {}
            
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

    def printCode(self,code):
        parsedCode = self.parser.parse(code)
        for statement in parsedCode:
            self.printTree(statement)
    
    def simplifyExpr(self,expr):

        if expr[0] == "@ID":
            return self.memory[expr[1]]
            
        if expr[0] == "@PROMPT":
            return input(self.simplifyExpr(expr[1]))
        
        if expr[0][0] == "@":
            return expr[1]
        
        match expr[0]:

            #Arithmetic
            case "ADD":
                return self.simplifyExpr(expr[1]) + self.simplifyExpr(expr[2])
            case "SUBTRACT":
                return self.simplifyExpr(expr[1]) - self.simplifyExpr(expr[2])
            case "MULTIPLY":
                return self.simplifyExpr(expr[1]) * self.simplifyExpr(expr[2])
            case "DIVIDE":
                return self.simplifyExpr(expr[1]) / self.simplifyExpr(expr[2])
            
            #Logic
            case "AND":
                return self.simplifyExpr(expr[1]) and self.simplifyExpr(expr[2])
            case "OR":
                return self.simplifyExpr(expr[1]) or self.simplifyExpr(expr[2])
            case "XOR":
                return (self.simplifyExpr(expr[1]) and not self.simplifyExpr(expr[2])) or (not self.simplifyExpr(expr[1]) and self.simplifyExpr(expr[2]))
            case "NOT":
                return not self.simplifyExpr(expr[1])
            
            #Comparators
            case "EQUALS":
                return self.simplifyExpr(expr[1]) == self.simplifyExpr(expr[2])
            case "GREATER":
                return self.simplifyExpr(expr[1]) > self.simplifyExpr(expr[2])
            case "GREATER_OR_EQUAL":
                return self.simplifyExpr(expr[1]) >= self.simplifyExpr(expr[2])
            case "LESSER":
                return self.simplifyExpr(expr[1]) < self.simplifyExpr(expr[2])
            case "LESSER_OR_EQUAL":
                return self.simplifyExpr(expr[1]) <= self.simplifyExpr(expr[2])
            
            case "CAST_VAR":
                match self.simplifyExpr(expr[2]):
                    case "STRING":
                        return str(self.simplifyExpr(expr[1]))
                    case "NUMBER":
                        return int(self.simplifyExpr(expr[1]))
                    case "BOOLEAN":
                        return bool(self.simplifyExpr(expr[1]))
                    case "RATIO":
                        return float(self.simplifyExpr(expr[1]))
                    
            case "RETRIEVE_ELE":
                return self.memory[expr[1][1]][self.simplifyExpr(expr[2])-1]
            case "CONVERT_TO_ARRAY":
                return self.memory[expr[1][1]].split()
            case "LENGTH":
                return len(self.memory[expr[1][1]])
            

            
    
    def executeStatement(self,statement,verbose=False):

        #Verbose is for debugging
        
        #if and while
        if statement[0] == "$IF":
            for ifBlock in statement[1:]:
                #Iterates through all ifblocks
                if ifBlock[0] == "IF" or ifBlock[0] == "ELIF":
                    #checks to make sure if Ifblock is if, elif, or else
                    if self.simplifyExpr(ifBlock[1]):
                        for ifBlockStatement in ifBlock[2]:
                            self.executeStatement(ifBlockStatement,verbose=verbose)
                        break
                    else:
                        continue
                else:
                    #If the ifblock is an else
                    for ifBlockStatement in ifBlock[1]:
                        self.executeStatement(ifBlockStatement,verbose=verbose)
                    break
            return
        
        if statement[0] == "$WHILE":
            while self.simplifyExpr(statement[1]):
                for whileBlockStatement in statement[2]:
                    self.executeStatement(whileBlockStatement,verbose=verbose)
            return
        
        if verbose:
            print("executing ", statement)

        match statement[0]:
            case "$PRINT":
                print(self.simplifyExpr(statement[1]))

            #VARIABLES & ARRAYS, WIP does not differentiate between types
            #When referring to variable name and not variable value, directly pull the variable name from the statement with something like statement[1][1] instead of simplifyExpr
            case "$DECLARE_VAR":
                self.memory[statement[1][1]] = None
            case "$ASSIGN_VAR":
                self.memory[statement[1][1]] = self.simplifyExpr(statement[2])
            case "$INCREMENT":
                self.memory[statement[1][1]] = self.memory[statement[1][1]] + 1
            case "$DECREMENT":
                self.memory[statement[1][1]] = self.memory[statement[1][1]] - 1

            case "$DECLARE_ARR":
                newList = []
                for i in range(self.simplifyExpr(statement[2])):
                    newList.append(None)
                self.memory[statement[1][1]] = newList
            case "$EDIT_ARR":
                temp = self.memory[statement[1][1]]
                temp[self.simplifyExpr(statement[2])-1] = self.simplifyExpr(statement[3])
                self.memory[statement[1][1]] = temp
            case "$ASSIGN_ARR":
                self.memory[statement[1][1]] = self.simplifyExpr(statement[2])
            case "$DELETE_ELE":
                temp = self.memory[statement[1][1]]
                temp.pop(self.simplifyExpr(statement[2])-1)
                self.memory[statement[1][1]] = temp
            case "$APPEND":
                self.memory[statement[1][1]] = self.memory[statement[1]].append(self.simplifyExpr(statement[2]))
    
    def execute(self,code,verbose=False):
        parsedCode = self.parser.parse(code)
        for statement in parsedCode:
            self.executeStatement(statement,verbose=verbose)
            

executer = executer()


if __name__ == "__main__":
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
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM"""

    d = """IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
DICERE 'SALVE MVNDI'
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
"""


    executer.printCode(c)
    #executer.execute(c,verbose=False)