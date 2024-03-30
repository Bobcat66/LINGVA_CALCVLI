#virtual machine for executing LINGVA CALCVLI code
import re

variables = [] #list of variables
array = [] #list of arrays
funcs = [] #list of functions
call_stack = []
expression_stack = []

"""
Commands:

"""

class stack_machine():
    #Command dict is for easier readability
    command_dict = {
        'PUSH' : 0x00,
        'POP' : 0x01,
        'ADD' : 0x02,
        'SUB' : 0x03, 
        'MULT' : 0x04,
        'DIV' : 0x05,
        'BAND' : 0x06,
        'BOR' : 0x07,
        'BXOR' : 0x08,
        'BNOT' : 0x09,
        'GOTO' : 0x0a,
        'INC' : 0x0b,
        'LOAD' : 0x0c,
        'IFEQ' : 0x0d, 
        'IFNE' : 0x0e,
        'WINC' : 0x0f,
        'NOP' : 0x10,
        'STORE' : 0x11
    }
    #Parameters are loaded into the instruction stack after their instruction. for example, the instruction stack for PUSH 5 would be [0x00,0x05]
    def __init__(self):
        self.stack = [] # operation stack
        self.memory = [] # local variables
        self.ops = [] # list of instructions to be executed
        self.pointer = 0 # instruction pointer
    
    def getFwd(self,offset):
        #retrieves the element offset forward of the current instruction in the instruction list
        return self.ops[self.pointer + offset]
    
    def getInt16(self,offset=0):
        #retrieves next two elements after the offset from pointer in instruction list and combines them into signed 16 bit integer
        arg1 = self.getFwd(offset+1)
        arg2 = self.getFwd(offset+2)
        a = (arg1 << 8) | arg2
        if a & (1 << 15):
            a -= (1 << 16)
        return a #converts two bytes into signed 16 bit integer
    
    def getuInt16(self,offset=0):
        #retrieves next two elements after the offset from pointer in instruction list and combines them into unsigned 16 bit integer
        arg1 = self.getFwd(offset+1)
        arg2 = self.getFwd(offset+2)
        return ((arg1 << 8) | arg2) #converts two bytes into unsigned 16 bit integer
    
    def decompileOpcode(self,opcode):
        #Decompiles individual opcode
        key_list = list(self.command_dict.keys())
        val_list = list(self.command_dict.values())
        index = val_list.index(opcode)
        return key_list[index]
    
    def formatInstructions(self,showPointer=False):
        #formats instructions into string
        instructions = ['0x%02x' % ele for ele in self.ops]
        iStr = '['
        for i in range(len(instructions)):
            if showPointer and i == self.pointer:
                iStr += '<<{0}>>, '.format(instructions[i])
            else:
                iStr += instructions[i] + ', '
        iStr = iStr[:-2]
        iStr += ']'
        return iStr
    def op(self,opcode):
        #Executes a single opcode
        match opcode:
            case 0x00:
                #PUSH
                #Append value to stack. 
                #Takes one one-byte parameter, the value to be added.
                arg1 = self.getFwd(1) #push value
                self.stack.append(arg1)
                return 1 + 1
            case 0x01:
                #POP
                #Remove top element of stack
                self.stack.pop()
                return 1
            case 0x02:
                #ADD
                #Pop top two elements of stack, add them, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b+a)
                return 1
            case 0x03:
                #SUB
                #Pop top two elements of stack, subtract them, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b-a)
                return 1
            case 0x04:
                #MULT
                #Pop top two elements of stack, multiply them, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b*a)
                return 1
            case 0x05:
                #DIV
                #Pop top two elements of stack, divide them, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b/a)
                return 1
            case 0x06:
                #BAND
                #Pop top two elements of stack, perform boolean AND, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b and a)
                return 1
            case 0x07:
                #BOR
                #Pop top two elements of stack, perform boolean OR, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b or a)
                return 1
            case 0x08:
                #BXOR
                #Pop top two elements of stack, perform boolean XOR, and push result to stack
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append((b and not a) or (not b and a))
                return 1
            case 0x09:
                #BNOT
                #Pop top element of stack, negate it, and push result to stack
                a = self.stack.pop()
                self.stack.append(not a)
                return 1
            case 0x0a:
                #GOTO
                #shifts instruction pointer. 
                #Takes one two-byte parameter, the offset.
                a = self.getInt16() #converts two bytes into signed 16 bit integers
                return a
            case 0x0b:
                #INC
                #Increment local variable by given constant. 
                #Takes two one-byte parameters, the variable index and the constant
                arg1 = self.getFwd(1) #index
                arg2 = self.getFwd(2) #constant
                a = self.memory[arg1]
                a += arg2
                self.memory[arg1] = a
                return 1 + 2
            case 0x0c:
                #LOAD
                #Load local variable into instruction stack.
                #takes one one-byte parameter, the variable index
                arg1 = self.getFwd(1)
                self.stack.append(self.memory[arg1])
                return 1 + 1
            case 0x0d:
                #IFEQ
                #Conditional shift. Pops top element from stack. if it is equal to zero, it shifts. else, execution proceeds as normal
                #takes one two-byte parameter, the offset
                a = self.getInt16() #offset
                b = self.stack.pop()
                if b == 0:
                    return a
                else:
                    return 1 + 2
            case 0x0e:
                #IFNE
                #Conditional shift. Pops top element from stack. if it is not equal to zero, it shifts. else, execution proceeds as normal
                #takes one two-byte parameter, the offset
                a = self.getInt16() #offset
                b = self.stack.pop()
                if b == 1:
                    return a
                else:
                    return 1 + 2
            case 0x0f:
                #WINC (Wide INC)
                #Increment local variable by given constant. 
                #Takes two two-byte parameters, the variable index and the constant
                a = self.getuInt16() #index
                b = self.getInt16(2) #constant
                c = self.memory[a]
                c += b
                self.memory[a] = c
                return 1 + 4
            case 0x10:
                #NOP
                #No operation
                return 1
            case 0x11:
                #STORE
                #Pops top element of stack, and stores it at index in memory
                #Takes one one-byte parameter, the variable index
                arg1 = self.getFwd(1)
                a = self.stack.pop()
                self.memory[arg1] = a
                return 1 + 1
                
    def initializeMemory(self,vars):
        self.memory = vars

    def execute(self,code: list,verbose=False):
        self.pointer = 0
        self.ops = code
        #if statement is up here to minimize the number of times the if statement is called
        if verbose:
            while self.pointer < len(code):
                opcode = self.ops[self.pointer]
                print("Stack:",self.stack)
                print("Memory:",self.memory)
                print("Instructions:",self.formatInstructions(showPointer=True))
                print("Pointer:",self.pointer)
                print("Executing {0} ({1})".format('0x%02x' % opcode,self.decompileOpcode(opcode)))
                print("------------------------------------------------------------")
                a = self.op(opcode) #self.op returns the distance to move the instruction pointer forward
                self.pointer += a
            print("Stack:",self.stack)
            print("Memory:",self.memory)
            print("Instructions:",self.formatInstructions())
                
        else:
            while self.pointer < len(code):
                a = self.op(self.ops[self.pointer]) #self.op returns the distance to move the instruction pointer forward
                self.pointer += a
        
    def compile(self,textCode: str, safe=True):
        # radix is the base of the numbers in the code. default is 10
        # Compiles text code into numerical opcodes
        # DOES NOT COMPILE LINGVA CALCVLI, ONLY COMPILES TEXTUAL REPRESENTATIONS OF MACHINA SIMVLATA OPCODE
        # Variable setup is separated from opcodes by '#### BEGIN CODE ####'
        # Variable setup goes first, code comes second. Variables should be separated by spaces
        # Compiler only supports simple numerical variables right now
        # Safe catches errors, but slows down compilatin
        textTup = textCode.split('#### BEGIN CODE ####')
        prevars = textTup[0].strip().split()
        vars = [int(var) for var in prevars]
        preText = textTup[1].strip()
        precode = re.split('[ ,\n]',preText)
        if safe:
            precode = [x for x in precode if len(x) > 0]
        code = [int(x) if x.isnumeric() else self.command_dict[x] for x in precode]
        return (vars,code)
    
    def __repr__(self):
        return "stack_machine(\n    stack={0},\n    memory={1},\n    ops={2},\n    pointer={3}\n)".format(self.stack,self.memory,self.formatInstructions(),self.pointer)

    def push(self,val):
        self.stack.append(val)

    def add(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b+a)

    def subtract(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b-a)

    def multiply(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b*a)

    def divide(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b/a)

exp = stack_machine()

a = '''
5 13 11
#### BEGIN CODE ####
LOAD 1
LOAD 0
IFEQ 0,14
LOAD 2
ADD
WINC 0,0 255,255
GOTO 255,243
NOP
'''
fibonacci = '''
0 1 20
#### BEGIN CODE ####
LOAD 2
IFEQ 0 24
LOAD 0
LOAD 0
LOAD 1
LOAD 1
STORE 0
ADD
STORE 1
WINC 0 2 255 255
GOTO 255 233
LOAD 0
LOAD 1
'''
b = exp.compile(fibonacci)
print(b)
exp.initializeMemory(b[0])
exp.execute(b[1],verbose=True)
#print(repr(exp))

