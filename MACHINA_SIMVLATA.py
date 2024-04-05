#virtual machine for executing LINGVA CALCVLI code
import re
from dataclasses import dataclass
import copy

variables = [] #list of variables
array = [] #list of arrays
funcs = [] #list of functions
call_stack = []
expression_stack = []

"""
Commands:

"""

@dataclass
class frame:
    #frames are 
    pc: int #program counter for frame
    localVars: list[int] #localvars
    opcodes: list[int] #opcodes to execute
    returnVal: int = None #return value


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
        'STORE' : 0x11,
        'IFCEQ' : 0x12, #Equality comparison between two values
        'IFCNE' : 0x13, #Notequal
        'IFCGR' : 0x14, #Greater
        'IFCLS' : 0x15, #Lesser
        'IFCGE' : 0x16, #Greater_or_Equal
        'IFCLE' : 0x17, #Lesser_or_Equal
        'CPRINT' : 0x18, #Prints top element of stack
        'DUP' : 0x19, #Duplicates last element of stack
        'DUP2' : 0x1a, #Duplicates last element of stack twice
        'LREF' : 0x1b, #Load ref from Symbol table
        'WLREF' : 0x1c,  #Load ref from Symbol table (wide) WIP
        'LARR' : 0x1d, #Load element from array WIP
        'STARR' : 0x1e, #Store element in array WIP
        'ARRLEN' : 0x1f, #get array length
        'CALL' : 0x20, #calls function based on reference from top of the stack
        'RETURN' : 0x21, #pops top element of stack and returns it
        'NEWVAR' : 0x22, #Pops top element and initializes new local variable
    }

    type_dict = {
        #Fundamental Variable types
        'BYTE' : 0x00,
        'SHORT' : 0x01,
        'INT' : 0x02,
        'FLOAT' : 0x03,
        'CHAR' : 0x04,
    }

    ref_dict = {
        #Reference types
        'VAR' : 0x01,
        'FUNC' : 0x02,
        'STRING' : 0x03,
        'IARR' : 0x04, #Int array
        'LARR' : 0x05, #Long array
        'FARR' : 0x06, #Float array
        'RARR' : 0x07, #Ref array
        'STRUCT' : 0x08, #WIP, to be implemented when Structs are added
    }

    #Parameters are loaded into the instruction stack after their instruction. for example, the instruction stack for PUSH 5 would be [0x00,0x05]
    def __init__(self):
        self.verbose = False
        self.stack = [] # operation stack, each entry is 4 bytes wide
        self.symbols = [] #Symbol table, keeps track of references. Each entry is a 1 byte data field followed by a 4 byte address or value (NOTE: SYMBOL VALUES ARE SIGNED)
        self.heap = [] #Stores large data structures, like strings and arrays. each element of the heap is a threeple: (<element width in bits>,<signed>,<list of elements>)
        self.frames = [] #keeps track of frames. self.frames acts like a stack. when the topmost frame completes execution, it is destroyed and control shifts immediately to the next-highest frame
        self.frame: frame = None #keeps track of the current frame. By default, main frame=0
    
    def getFwd(self,offset):
        #retrieves the element offset forward of the current instruction in the instruction list
        return self.frame.opcodes[self.frame.pc + offset]
    
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
        instructions = ['%02x' % ele for ele in self.frame.opcodes]
        iStr = '['
        for i in range(len(instructions)):
            if showPointer and i == self.frame.pc:
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
                a = self.frame.localVars[arg1]
                a += arg2
                self.frame.localVars[arg1] = a
                return 1 + 2
            case 0x0c:
                #LOAD
                #Load local variable into instruction stack.
                #takes one one-byte parameter, the variable index
                arg1 = self.getFwd(1)
                self.stack.append(self.frame.localVars[arg1])
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
                c = self.frame.localVars[a]
                c += b
                self.frame.localVars[a] = c
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
                self.frame.localVars[arg1] = a
                return 1 + 1
            case 0x12:
                #IFCEQ
                #Compares top two elements of stack. shifts if they are equal
                #Takes one two-byte parameter, the location it should shift to
                a = self.getInt16() 
                b = self.stack.pop()
                c = self.stack.pop()
                if b == c:
                    return a
                else:
                    return 1 + 2
            case 0x13:
                #IFCNE
                #Compares top two elements of stack. shifts if they are equal
                #Takes one two-byte parameter, the location it should shift to
                a = self.getInt16() 
                b = self.stack.pop()
                c = self.stack.pop()
                if b != c:
                    return a
                else:
                    return 1 + 2
            case 0x14:
                #IFCGR
                #Compares top two elements of stack. shifts if value1 is greater than value2
                #Takes one two-byte parameter, the location it should shift to
                a = self.getInt16() 
                b = self.stack.pop()
                c = self.stack.pop()
                if c > b:
                    return a
                else:
                    return 1 + 2
            case 0x15:
                #IFCLS
                #Compares top two elements of stack. shifts if value1 is lesser than value2
                #Takes one two-byte parameter, the location it should shift to
                a = self.getInt16() 
                b = self.stack.pop()
                c = self.stack.pop()
                if c < b:
                    return a
                else:
                    return 1 + 2
            case 0x16:
                #IFCGE
                #Compares top two elements of stack. shifts if value1 is greater or equal to value2
                #Takes one two-byte parameter, the location it should shift to
                a = self.getInt16() 
                b = self.stack.pop()
                c = self.stack.pop()
                if c >= b:
                    return a
                else:
                    return 1 + 2
            case 0x17:
                #IFCLE
                #Compares top two elements of stack. shifts if value1 is lesser or equal to value2
                #Takes one two-byte parameter, the location it should shift to
                a = self.getInt16() 
                b = self.stack.pop()
                c = self.stack.pop()
                if c <= b:
                    return a
                else:
                    return 1 + 2
            case 0x18:
                #IPRINT
                #Prints top element of stack as ASCII character
                a = self.stack.pop()
                print(chr(a),end="")
                return 1
            case 0x19:
                #DUP
                #Duplicates top element of stack
                a = self.stack.pop()
                self.stack.append(a)
                self.stack.append(a)
                return 1
            case 0x1a:
                #DUP2
                #Duplicates top two elements of stack. Preserves order
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b)
                self.stack.append(b)
                self.stack.append(a)
                self.stack.append(a)
                return 1
            case 0x1b:
                #LREF
                #Loads reference from symbol table
                #takes one 1-byte parameter, the index of the reference in the symbol table
                arg1 = self.getFwd(1)
                self.stack.append(self.symbols[arg1][1])
                return 1 + 1
            case 0x1c:
                #WLREF
                #Loads reference from symbol table (WIDE)
                #takes one 2-byte parameter, the index of the reference in the symbol table
                arg1 = self.getInt16()
                self.stack.append(self.symbols[arg1][1])
                return 1 + 2
            case 0x1d:
                #LARR
                #Load element of array
                index = self.stack.pop()
                arrayref = self.stack.pop()
                self.stack.append(self.heap[arrayref][2][index])
                return 1
            case 0x1e:
                #STARR
                #Store element in array
                value = self.stack.pop()
                index = self.stack.pop()
                arrayref = self.stack.pop()
                self.heap[arrayref][2][index] = value
                return 1
            case 0x1f:
                #ARRLEN
                #Get array length
                arrayref = self.stack.pop()
                self.stack.append(len(self.heap[arrayref][2]))
                return 1
            case 0x20:
                #TODO: Finish call command
                #CALL
                #Pops top element of operand stack, and creates a frame based off it, and transfers control to new frame. It also adds current frame to frame stack
                #Takes one 1-byte parameter, the number of arguments the function
                self.frames.append(copy.deepcopy(self.frame))
                arg1 = self.getFwd(1)
                args = []
                for i in range(arg1):
                    args.append(self.stack.pop())
                funcRef = self.stack.pop()
                returnAddress = len(self.stack)
                funcOps = self.heap[funcRef][2]
                newFrame = frame(0,args,funcOps)
                self.frame = newFrame
                ret = self.execute(verbose=self.verbose)

                #Return of control to parent frame
                self.frame = self.frames.pop()
                self.stack = self.stack[0:returnAddress] #removes any residual stack elements from the frame executions
                self.stack.append(ret)
                return 1 + 1
            case 0x21:
                #RETURN
                #pops top element of operand stack, and returns it
                a = self.stack.pop()
                self.frame.returnVal = a
                return "RETURN"
            case 0x22:
                #NEWVAR
                #pops top element of operand stack, and stores it in a new local variable
                a = self.stack.pop()
                self.frame.localVars.append(a)
                return 1
           
    def initialize(self,heap,symbols,vars,code):
        self.frames = []
        self.symbols = symbols
        self.heap = heap
        newFrame = frame(0,vars,code)
        self.frame = newFrame

        #DEPRECIATED
        self.ret = None

    def execute(self,verbose=False):
        #executes current frame, returns output
        #if statement is up here to minimize the number of times the if statement is called
        self.verbose = verbose
        if verbose:
            while self.frame.pc < len(self.frame.opcodes):
                opcode = self.frame.opcodes[self.frame.pc]
                print("Stack:",self.stack)
                print("Local Vars:",self.frame.localVars)
                print("Instructions:",self.formatInstructions(showPointer=True))
                print("Program Counter:",self.frame.pc)
                print("Executing {0} ({1})".format('%02X' % opcode,self.decompileOpcode(opcode)))
                print("------------------------------------------------------------")
                a = self.op(opcode) #self.op returns the distance to move the instruction pointer forward, or a flag signaling the executer to return a value
                if a == "RETURN":
                    return self.frame.returnVal
                self.frame.pc += a
                
        else:
            while self.frame.pc < len(self.frame.opcodes):
                a = self.op(self.frame.opcodes[self.frame.pc]) #self.op returns the distance to move the instruction pointer forward
                if a == "RETURN":
                    return self.frame.returnVal
                self.frame.pc += a
        
    def compile(self,textCode: str, safe=True):
        # Compiles text code into numerical opcodes
        # DOES NOT COMPILE LINGVA CALCVLI, ONLY COMPILES TEXTUAL REPRESENTATIONS OF MACHINA SIMVLATA OPCODE
        # Sections of the code are separated by '#### #### #### ####'
        # Heap setup goes first, then symbols, then Local memory, then code.
        # Heap elements should be series of numerical bytes separated by spaces
        # Symbols should be tuples of the following format: <info byte> <4-byte address>
        # Variables should be separated by spaces
        # Compiler only supports simple numerical variables right now
        # Safe catches errors, but slows down compilation
        # All numbers should be in hexadecimal, and should be broken up into bytes of exactly two digits
        textTup = textCode.split('#### #### #### ####')

        preheap = textTup[0].strip().split('\n')
        heap = []
        for ele in preheap:
            preObj = ele.split()
            width = int(preObj[0],base=16) #size of each element in bits
            byteWidth = width//8
            signed = bool(int(preObj[1],16))
            obj = (width,signed,[])
            byteArray = []
            for x in ele.split()[2:]:
                inNum = int(x,16)
                if not signed and inNum < 0:
                    inNum += (1 << width)
                byteArray.append(inNum)
            for i in range(len(byteArray)//byteWidth):
                bytes = []
                for j in range(byteWidth):
                    bytes.append(byteArray[(byteWidth*i)+j])
                inInt = bytesToInt(*bytes,width=width,signed=signed)
                obj[2].append(inInt)
            heap.append(obj)

        preSymbols = textTup[1].strip().split('\n')
        symbols = []
        for sele in preSymbols:
            ele = sele.split()
            bele1 = [int(x,16) for x in ele[1:]]
            if not len(ele[0]) == 2:
                symbol = (self.ref_dict[ele[0]],bytesToInt(*bele1,signed=True))
            else:
                symbol = (int(ele[0],base=16),bytesToInt(*bele1,signed=True))
            symbols.append(symbol)

        prevars = textTup[2].strip().split('\n')
        #vars = [int(var) for var in prevars]
        vars = []
        for ele in prevars:
            ele1 = [int(x,16) for x in ele.split()]
            vars.append(bytesToInt(*ele1,signed=True))

        preText = textTup[3].strip()
        precode = re.split('[ ,\n]',preText)
        if safe:
            precode = [x for x in precode if len(x) > 0]
        code = [int(x,base=16) if len(x) == 2 else self.command_dict[x] for x in precode]
        return (heap,symbols,vars,code)
    
    def __repr__(self):
        #return "stack_machine(\n    stack={0},\n    memory={1},\n    ops={2},\n    pointer={3}\n)".format(self.stack,self.memory,self.formatInstructions(),self.pointer)
        return "WIP"

def pack(codeTuple):
    '''
    packs codetuple into byte array that can be written to a .mcs file
    '''
    # codeTuple should be a 4-tuple formatted in the following way:
    # (<heap>,<symbols>,<vars>,<code>)
    heap = codeTuple[0]
    symbols = codeTuple[1]
    vars = codeTuple[2]
    code = codeTuple[3]
    heapsize = len(heap)
    symbolsize = len(symbols)
    varsize = len(vars)
    codesize = len(code)
    beginLst = []
    beginLst += list(intToBytes(heapsize))
    beginLst += list(intToBytes(symbolsize))
    beginLst += list(intToBytes(varsize))
    beginLst += list(intToBytes(codesize))

    heapLst = []
    for obj in heap:
        width = obj[0]
        signed = obj[1]
        heapLst += list(intToBytes(len(obj[2])))
        heapLst.append(width)
        heapLst.append(signed)
        for ele in obj[2]:
            tempbytes = list(intToBytes(ele,size=width))
            heapLst += tempbytes

    symbolLst = []
    for ele in symbols:
        symbolLst.append(ele[0])
        for byte in intToBytes(ele[1]):
            symbolLst.append(byte)

    varLst = []
    for ele in vars:
        for byte in intToBytes(ele):
            varLst.append(byte)
    cLst = []
    for ele in code:
        cLst.append(ele)
    finLst = beginLst
    finLst += heapLst
    finLst += symbolLst
    finLst += varLst
    finLst += cLst
    outBytes = bytes(finLst)
    return outBytes

def unpack(bytecode):
    '''
    Unpacks raw bytes from .mcs file to useable code tuple
    '''
    heapLen = int.from_bytes(bytecode[0:4],'big',signed=False)
    symbolLen = int.from_bytes(bytecode[4:8],'big',signed=False)
    varLen = int.from_bytes(bytecode[8:12],'big',signed=False)
    codeLen = int.from_bytes(bytecode[12:16],'big',signed=False)

    heap = []
    p = 16 # pointer byte being analyzed
    for i in range(heapLen):
        objLen = int.from_bytes(bytecode[p:p+4],'big',signed=False)
        p += 4
        width = int(bytecode[p]) #Width in bits
        byteWidth = width//8 #Width in bytes
        p += 1
        signed = bool(bytecode[p])
        p += 1
        objSize = byteWidth * objLen #Size of object in memory, in bytes

        objBytes = bytecode[p:p+objSize]
        objList = []
        for j in range(objLen):
            tempBytes = []
            for k in range(byteWidth):
                tempBytes.append(objBytes[(j*byteWidth)+k])
            objList.append(int.from_bytes(tempBytes,'big',signed=signed))
        
        obj = (width,signed,objList)
        heap.append(obj)
        p += objSize
    
    symbols = []
    for i in range(symbolLen):
        sType = int(bytecode[p])
        p += 1
        sVal = int.from_bytes(bytecode[p:p+4],'big',signed=True)
        p += 4
        symbol = (sType,sVal)
        symbols.append(symbol)
    
    vars = []
    for i in range(varLen):
        vars.append(int.from_bytes(bytecode[p:p+4],'big',signed=True))
        p += 4
    
    code = []
    for i in range(codeLen):
        code.append(bytecode[p])
        p += 1
    
    return (heap,symbols,vars,code)

def intToBytes(num,size=32):
    #Converts int32s into 4 bytes
    if num < 0:
        num += (1 << 32) 
    bytes = []
    for i in range(size//8):
        byte = (num % (1 << size-(8*i))) >> (size - 8 * (i+1))
        bytes.append(byte)
    return tuple(bytes)

def bytesToInt(*args,width=32,signed=True):
    #converts bytes into a single integer
    bytes = []
    iargs = [int(x) for x in args]
    for i in range(width//8):
        bytes.append(iargs[i] << (width - 8*(i+1)))
    num = 0
    for byte in bytes:
        num |= byte
    if signed:
        if (num & (1 << (width-1))):
            num -= (1 << width)
    return num
    

if __name__ == '__main__':
    #for testing
    exe = stack_machine()
    c = '''
08 00 48 65 6C 6C 6F 2C 20 77 6F 72 6C 64 0A
08 00 53 65 63 6F 6E 64 20 73 74 72 69 6E 67
#### #### #### ####
STRING 00 00 00 00
STRING 00 00 00 01
#### #### #### ####
00 00 00 00
00 00 00 00
#### #### #### ####
LREF 00
ARRLEN
STORE 00
LOAD 00
LOAD 01
IFCEQ 00 0F
LREF 00
LOAD 01
LARR
CPRINT
INC 01 01
GOTO FF F0
LREF 01
ARRLEN
STORE 00
PUSH 00
STORE 01
LOAD 00
LOAD 01
IFCEQ 00 0F
LREF 01
LOAD 01
LARR
CPRINT
INC 01 01
GOTO FF F0
'''
    d = '''
08 00 48 65 6C 6C 6F 2C 20 77 6F 72 6C 64 0A
#### #### #### ####
STRING 00 00 00 00
#### #### #### ####
00 00 00 00
00 00 00 00
#### #### #### ####
LREF 00
ARRLEN
STORE 00
LOAD 00
LOAD 01
IFCEQ 00 0F
LREF 00
LOAD 01
LARR
CPRINT
INC 01 01
GOTO FF F0
PUSH 00
RETURN
'''
    #Print method. Reference to string being printed is passed as argument
    #Raw code: 08 00 0C 00 1F 22 00 00 22 0C 01 0C 02 12 00 0F 0C 00 0C 02 1D 18 0B 02 01 0A FF F0 00 20 00 00 21
    g = '''
08 00 48 65 6C 6C 6F 2C 20 77 6F 72 6C 64 0A
#### #### #### ####
STRING 00 00 00 00
#### #### #### ####
00 00 00 00
#### #### #### ####
LOAD 00
ARRLEN
NEWVAR
PUSH 00
NEWVAR
LOAD 01
LOAD 02
IFCEQ 00 0F
LOAD 00
LOAD 02
LARR
CPRINT
INC 02 01
GOTO FF F0
PUSH 20
PUSH 00
RETURN
'''

    #Uses print method
    e = '''
08 00 0C 00 1F 22 00 00 22 0C 01 0C 02 12 00 0F 0C 00 0C 02 1D 18 0B 02 01 0A FF F0 00 20 00 00 21
08 00 48 65 6C 6C 6F 2C 20 77 6F 72 6C 64 0A
08 00 53 65 63 6F 6E 64 20 73 74 72 69 6E 67
#### #### #### ####
FUNC 00 00 00 00
STRING 00 00 00 01
STRING 00 00 00 02
#### #### #### ####
00 00 00 00
#### #### #### ####
LREF 00
LREF 01
CALL 01
LREF 00
LREF 02
CALL 01
PUSH 00
RETURN
'''
    '''
    dc = exe.compile(g)
    print(dc[0])
    for ele in dc[3]:
        print("{0:02X} ".format(ele),end="")
    print()
    exe.initialize(dc[0],dc[1],dc[2],dc[3])
    exe.execute()
'''
    '''
    ec = exe.compile(e)
    f = open('helloWorldMethod.mcs','wb')
    f.write(pack(ec))
    f.close()
    '''
    f = open('lcbin/helloWorld3.mcs','rb')
    fg = f.read()
    f.close()
    fe = unpack(fg)
    exe.initialize(fe[0],fe[1],fe[2],fe[3])
    exe.execute()



