#virtual machine for executing LINGVA CALCVLI code
import re
import dataclasses

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
        self.stack = [] # operation stack, each entry is 4 bytes wide
        self.memory = [] # local variables, each element is 4 bytes wide, and is natively stored as an int
        self.ops = [] # list of instructions to be executed
        self.symbols = [] #Symbol table, keeps track of references. Each entry is a 1 byte data field followed by a 4 byte address or value (NOTE: SYMBOL VALUES ARE SIGNED)
        self.heap = [] #Stores large data structures, like strings and arrays. each element of the heap is a threeple: (<element width in bits>,<signed>,<list of elements>)
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
        instructions = ['%02x' % ele for ele in self.ops]
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
                
    def initialize(self,heap,symbols,vars):
        self.memory = vars
        self.symbols = symbols
        self.heap = heap

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
                print("Executing {0} ({1})".format('%02x' % opcode,self.decompileOpcode(opcode)))
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
            signed = bool(preObj[1])
            obj = (width,signed,[])
            byteArray = [int(x,base=16) for x in ele.split()[2:]]
            for i in range(len(byteArray)//byteWidth):
                bytes = []
                for j in range(byteWidth):
                    bytes.append(byteArray[(byteWidth*i)+j])
                obj[2].append(bytesToInt(*bytes,width=width,signed=signed))
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
        return "stack_machine(\n    stack={0},\n    memory={1},\n    ops={2},\n    pointer={3}\n)".format(self.stack,self.memory,self.formatInstructions(),self.pointer)

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
IPRINT
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
IPRINT
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
IPRINT
INC 01 01
GOTO FF F0
'''
    dc = exe.compile(d)
    dp = pack(dc)
    f = open("helloWorld.mcs",'wb')
    f.write(dp)
    f.close()
    cc = exe.compile(c)
    cp = pack(cc)
    f = open("helloWorld2.mcs",'wb')
    f.write(cp)
    f.close()


