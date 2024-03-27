from LINGVA_CALCVLI_PARSER import parser
import NVMERVS_ROMANVS as num

class VARIABLE():
    def __init__(self,type,value=None):
        self.type = type
        self.value = value

class ARRAY():
    def __init__(self,size,type,elements=[]):
        self.size = size
        self.type = type
        self.value = elements
    
    def APPEND_ARR(self,value):
        self.value.append(value)
        self.size += 1
    def EDIT_ARR(self,index,value):
        self.value[index-1] = value
    
    def ASSIGN_ARR(self,new_arr):
        self.value = new_arr

    def DELETE_ELE(self,index):
        self.value.pop(index)
        self.size -= 1

    def __str__(self):
        return str(self.value)

class FUNCTION():
    def __init__(self,return_type,args,statements):
        self.return_type = return_type
        self.args = args
        self.statements = statements

class executer():
    def __init__(self) -> None:
        self.parser = parser
        self.memory = {}
        self.funcs = {}

    def verifyType(self,type,value):
        #Matches type (NUMBER,RATIO,CHAR,BOOLEAN,or STRING) to value
        match type:
            case "NUMBER":
                return isinstance(value,int)
            case "RATIO":
                return isinstance(value,float)
            case "CHAR":
                return isinstance(value,str) and len(value) == 1
            case "BOOLEAN":
                return isinstance(value,bool)
            case "STRING":
                return isinstance(value,str)
            
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
            # TODO: ADD FUNCTIONS 
            return self.memory[expr[1]].value
            
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
                return self.memory[expr[1][1]].value[self.simplifyExpr(expr[2])-1]
            case "CONVERT_TO_ARRAY":
                return self.memory[expr[1][1]].value.split()
            case "LENGTH":
                return len(self.memory[expr[1][1]].value)
             
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
                            ret = self.executeStatement(ifBlockStatement,verbose=verbose)
                            match ret[0]:
                                case 0:
                                    pass
                                case _:
                                    return ret
                        break
                    else:
                        continue
                else:
                    #If the ifblock is an else
                    for ifBlockStatement in ifBlock[1]:
                        ret = self.executeStatement(ifBlockStatement,verbose=verbose)
                        match ret[0]:
                            case 0:
                                pass
                            case _:
                                return ret
                    break
            return (0,None)
        
        if statement[0] == "$WHILE":
            while self.simplifyExpr(statement[1]):
                for whileBlockStatement in statement[2]:
                    ret = self.executeStatement(whileBlockStatement,verbose=verbose)
                    match ret[0]:
                        case 0:
                            pass
                        case _:
                            return ret
            return (0,None)
        
        if statement[0] == "$DECLARE_FUNCTION":
            pass
   
        if verbose:
            print("executing ", statement)

        match statement[0]:
            case "$PRINT":
                print(self.simplifyExpr(statement[1]))

            # VARIABLES & ARRAYS, WIP does not differentiate between types
            # When referring to variable name and not variable value, 
            # directly pull the variable name from the statement with something like statement[1][1] instead of simplifyExpr
                
            case "$DECLARE_VAR":
                #statement[2] = type
                self.memory[statement[1][1]] = VARIABLE(type=self.simplifyExpr(statement[2]))

            case "$ASSIGN_VAR":
                #print(statement)
                #print(statement[1])
                varName = statement[1][1]
                value = self.simplifyExpr(statement[2])

                if not self.verifyType(self.memory[varName].type,value):
                    #WIP
                    return (1,statement)
                self.memory[varName] = VARIABLE(type=self.memory[varName].type,value=value)

            case "$INCREMENT":
                if not self.verifyType("NUMBER",self.simplifyExpr(statement[1])):
                    #WIP
                    return (1,statement)
                self.memory[statement[1][1]].value = self.memory[statement[1][1]].value + 1

            case "$DECREMENT":
                if not self.verifyType("NUMBER",self.simplifyExpr(statement[1])):
                    #WIP
                    return (1,statement)
                self.memory[statement[1][1]].value = self.memory[statement[1][1]].value - 1

            case "$DECLARE_ARR":
                arrayName = statement[1][1]
                size = self.simplifyExpr(statement[2])
                type = self.simplifyExpr(statement[3])
                newList = []

                for i in range(size):
                    newList.append(None)
                self.memory[arrayName] = ARRAY(size,type,newList)
            case "$EDIT_ARR":
                arrayName = statement[1][1]
                index = self.simplifyExpr(statement[2])
                value = self.simplifyExpr(statement[3])

                if not self.verifyType("NUMBER",index):
                    return (1,"ON STATEMENT {0}: ARRAY INDEX '{1}' MVST BE TYPE 'NVMERVS'".format(statement,index))
                temp = self.memory[arrayName]
                if not self.verifyType(temp.type,value):
                    return (1,"ON STATEMENT {0}: TYPE MISMATCH BETWEEN ARRAY '{1}' AND ELEMENT '{2}'".format(statement,arrayName,value))
                temp.EDIT_ARR(index,value)
                if verbose:
                    print(temp)
                self.memory[arrayName] = temp

            case "$ASSIGN_ARR":
                arrayName = statement[1][1]
                newArr = self.simplifyExpr(statement[2])
                self.memory[arrayName] = newArr 
            case "$DELETE_ELE":
                arrayName = statement[1][1]
                index = self.simplifyExpr(statement[2])
                temp = self.memory[arrayName]

                temp.DELETE_ELE[index]
                self.memory[arrayName] = temp

            case "$APPEND":
                arrayName = statement[1][1]
                newVal = self.simplifyExpr(statement[2])

                self.memory[arrayName] = self.memory[arrayName].append(newVal)
        return (0,None)
    
    def execute(self,code,verbose=False):
        parsedCode = self.parser.parse(code)
        for statement in parsedCode:
            ret = self.executeStatement(statement,verbose=verbose)
            match ret[0]:
                #return codes are formatted like this: (code,message)
                case 0:
                    pass
                case 1:
                    print("RETURN CODE 1 TYPE ERROR: " + ret[1])
                    return
                case 2:
                    print("RETURN CODE 2 SYNTAX ERROR: " + ret[1])
                    return
                case _:
                    print("UNKNOWN ERROR: " + ret[1])
                    return
        print("RETURN CODE 0: SUCCESSFUL EXECUTION")
"""
EXECUTER RETURN CODES
0: successful execution
1: type error
2: syntax error
"""

            
executer = executer()


if __name__ == "__main__":
    a = """IMPERO TIBI
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

    b = """IMPERO TIBI
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

    c = """IMPERO TIBI
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

    d = """IMPERO TIBI
DICERE 'SALVE MVNDI'
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
"""


    #executer.printCode(c)
    executer.execute(c)