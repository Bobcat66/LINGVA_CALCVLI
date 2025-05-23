#virtual machine for executing LINGVA CALCVLI code
import re
from dataclasses import dataclass
import copy
import math
import sys
import io
import NVMERVS_ROMANVS as romNum
import msvcrt

#TODO: Finish romnum function
@dataclass
class frame:
    pc: int #program counter for frame
    localVars: list[int] #localvars, Signed ints
    opcodes: list[int] #opcodes to execute
    returnVal: int = None #return value
    def __repr__(self):
        return "frame(pc={0},localVars={1},opcodes={2},returnVal={3})".format(self.pc,self.localVars,self.opcodes,self.returnVal)


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
        'INC' : 0x0b, #Increment variable
        'RILOAD' : 0x0c, #Load int or reference from local variable
        'IFEQ' : 0x0d, 
        'IFNE' : 0x0e,
        'WINC' : 0x0f,
        'NOP' : 0x10,
        'RISTORE' : 0x11, #Stores int in variable
        'IFCEQ' : 0x12, #Equality comparison between two values
        'IFCNE' : 0x13, #Notequal
        'IFCGR' : 0x14, #Greater
        'IFCLS' : 0x15, #Lesser
        'IFCGE' : 0x16, #Greater_or_Equal
        'IFCLE' : 0x17, #Lesser_or_Equal
        'CPRINT' : 0x18, #Prints top element of stack
        'DUP' : 0x19, #Duplicates last element of stack
        'DUP2' : 0x1a, #Duplicates last element of stack twice
        'LREF' : 0x1b, #Load ref from Symbol table. Can be widened
        'WLREF' : 0x1c,  #Load ref from Symbol table (wide) 
        'ILARR' : 0x1d, #Load int from array 
        'ISTARR' : 0x1e, #Store int in array 
        'ARRLEN' : 0x1f, #get array length
        'CALL' : 0x20, #calls function based on reference from top of the stack
        'RETURN' : 0x21, #pops top element of stack and returns it
        'NEWVAR' : 0x22, #Pops top element and initializes new local variable
        'FLOAD' : 0x23, #Load float from local variable into op stack
        'FLARR' : 0x24, #Load float from array
        'FSTARR' : 0x25, #Store top ele in opstack into array as float
        'FSTORE' : 0x26, #Store top ele in opstack into local var as float
        'ITOSI' : 0x27, #Converts int to signed int
        'SITOI' : 0x28, #Converts signed int to int
        'SITOFL' : 0x29, #Converts signed int to float
        'ITOFL' : 0x2a, #Converts int to float
        'INPUT' : 0x2b, #Reads line from input stream and appends it to stack sequentially
        'RSARR' : 0x2c, #Resizes array. Takes two parameters: the array length and the width of each element
        'SWAP' : 0x2d, #Swaps topmost element and second topmost element on stack
        'MSWAP' : 0x2e,
        'LICONST' : 0x2f, #Loads global integer constant from symbol table. Can be widened
        'LSCONST' : 0x30, #Loads global signed integer constant from symbol table. Can be widened
        'LFCONST' : 0x31, #Loads global float constant from symbol table. Can be widened
        'WIDE' : 0x32, #Modifies next opcode to take double the normal number of params #TODO WIP
        'YOUR_MOTHER' : 0x33, #Modifies next opcode to take quadruple the normal number of params #TODO WIP
        'EXARR' : 0x34,
        'NEWOBJ' : 0x35,
        'MOD' : 0x36,
        'IDIV' : 0x37,
        'FRONT' : 0x38, #Brings element in stack to front. takes one parameter, the position in the stack to move to the front
        'SFRONT' : 0x39,
        'BACK' : 0x3a, #Pushes top of stack back a certain number of spaces. takes one parameter, the position in the stack to push to. 1 = push to top of stack
        'SBACK' : 0x3b, #Pushes top of stack back a certain number of spaces. parameter is in stack. 1 = push to second to top of stack (top is the parameter)
        'ITOSTR' : 0x3c,
        'STRTOI' : 0x3d,
        'NEWOBJS' : 0x3e,
        'EQL' : 0x3f,
        'NEQL' : 0x40,
        'GTR' : 0x41,
        'LSR' : 0x42,
        'GEQ' : 0x43,
        'LEQ' : 0x44,
        'ASSIGN' :0x45,
        'WGOTO' : 0x46
    }

    #Dict of instruction offsets, for formatting instructions. Any instruction not listed on the offset dict has an offset of 1
    offsetDict = {
        0x00 : 2,
        0x0a : 3,
        0x0b : 3,
        0x0c : 2,
        0x0d : 3,
        0x0e : 3,
        0x0f : 5,
        0x11 : 2,
        0x12 : 3,
        0x13 : 3,
        0x14 : 3,
        0x15 : 3,
        0x16 : 3,
        0x17 : 3,
        0x1b : 2,
        0x1c : 3,
        0x20 : 2,
        0x23 : 2,
        0x26 : 2,
        0x2e : 2,
        0x2f : 2,
        0x30 : 2,
        0x31 : 2,
        0x32 : 'Double',
        0x33 : 'Quad',
        0x35 : 5,
        0x38 : 2,
        0x45 : 7,
        0x46 : 5,
    }

    type_dict = {
        #Fundamental Variable types
        #TODO
        'BYTE' : 0x00,
        'SHORT' : 0x01,
        'INT' : 0x02,
        'FLOAT' : 0x03,
        'CHAR' : 0x04,
    }

    ref_dict = {
        #Reference types
        'VAR' : 0x01, #Global Variable, Not used
        'FUNC' : 0x02, #Bytecode, 8 bits
        'STRING' : 0x03, #String, 8 bits
        'IARR' : 0x04, #Int array, 32 bits 
        'LARR' : 0x05, #Long array, 64 bits
        'FARR' : 0x06, #Float array, 32 bits
        'RARR' : 0x07, #Ref array, 32 bits
        'STRUCT' : 0x08, #WIP, to be implemented when Structs are added
        'SIARR' : 0x09, #Signed int array
        'CONST' : 0x0a, #Global constant
        'SLARR' : 0x0b, #Signed Long array 
        'BARR' : 0x0c, #Byte array, 8 bits
    }

    #Parameters are loaded into the instruction stack after their instruction. for example, the instruction stack for PUSH 5 would be [0x00,0x05]
    def __init__(
            self,
            verbose: bool = False,
            stack: list[int] = None, #operation stack, each entry is 4 bytes wide
            symbols: list[int] = None, #Symbol table, keeps track of references. Each entry is a 1 byte data field followed by a 4 byte address
            heap: list[tuple] = None, #Stores large data structures, like strings and arrays. each element of the heap is a threeple: (<element width in bits>,<signed>,<list of elements>)
            frames: list[frame] = None, #keeps track of frames. self.frames acts like a stack. when the topmost frame completes execution, it is destroyed and control shifts immediately to the next-highest frame
            frame: frame = None, #keeps track of the current frame. By default, main frame=0
            input: io.StringIO = sys.stdin,
            output: io.StringIO = sys.stdout
        ):

        self.verbose = verbose

        if stack is None:
            self.stack = []
        else:
            self.stack = stack

        if symbols is None:
            self.symbols = []
        else:
            self.symbols = symbols

        if heap is None:
            self.heap = []
        else:
            self.heap = heap

        if frames is None:
            self.frames = []
        else:
            self.frames = frame

        self.frame = frame
        self.inStream = input
        self.outStream = output
    
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
    
    def getuInt32(self,offset=0):
        #retrieves next four elements after the offset from pointer in instruction list and combines them into unsigned 32 bit integer
        arg1 = self.getFwd(offset+1)
        arg2 = self.getFwd(offset+2)
        arg3 = self.getFwd(offset+3)
        arg4 = self.getFwd(offset+4)
        return ((arg1 << 24) | (arg2 << 16) | (arg3 << 8) | arg4) #converts two bytes into unsigned 32 bit integer
    
    @classmethod
    def decompileOpcode(cls,opcode):
        #Decompiles individual opcode
        key_list = list(cls.command_dict.keys())
        val_list = list(cls.command_dict.values())
        index = val_list.index(opcode)
        return key_list[index]
    
    @classmethod
    def decompileRef(cls,ref):
        key_list = list(cls.ref_dict.keys())
        val_list = list(cls.ref_dict.values())
        index = val_list.index(ref)
        return key_list[index]
    
    @staticmethod
    def getDictKey(dict,val):
        key_list = list(dict.keys())
        val_list = list(dict.values())
        index = val_list.index(val)
        return key_list[index]
    
    def formatInstructions(self,showPointer=False):
        #formats instructions into string
        instructionPosList = set() #list of indexes of instructions
        i = 0
        while i < len(self.frame.opcodes):
            instructionPosList.add(i)
            try:
                off = self.offsetDict[self.frame.opcodes[i]]
                if off == 'Double':
                    instructionPosList.add(i)
                    instructionPosList.add(i+1)
                    a = self.offsetDict[self.frame.opcodes[i+1]]
                    i += (2 + 2*(a-1))
                elif off == 'Quad':
                    instructionPosList.add(i)
                    instructionPosList.add(i+1)
                    a = self.offsetDict[self.frame.opcodes[i+1]]
                    i += (2 + 4*(a-1))
                else:
                    i += self.offsetDict[self.frame.opcodes[i]]
            except KeyError:
                i += 1
        instructions = [self.decompileOpcode(self.frame.opcodes[i]) if i in instructionPosList else '%02X' % self.frame.opcodes[i] for i in range(len(self.frame.opcodes))]
        iStr = '['
        for i in range(len(instructions)):
            if showPointer and i == self.frame.pc:
                iStr += '<<{0}>>, '.format(instructions[i])
            else:
                iStr += instructions[i] + ', '
        iStr = iStr[:-2]
        iStr += ']'
        return iStr
    
    @staticmethod
    def rawFormatInstructions(inlist):
        #formats instructions into raw numbers
        return ['%02X' % ele for ele in inlist]
    
    @classmethod
    def compileInstructions(cls, codetext: str):
        #Compiles MS code into string of hexadecimal integers. Useful for working directly with MS code
        code1 = codetext.split('\n')
        uncommentedCode = ""
        for line in code1:
            #Removes comments
            lineSplit = line.split('//')
            uncommentedCode += (lineSplit[0] + '\n')
        precode = re.split('[ ,\n]',uncommentedCode)
        precode = [x for x in precode if len(x) > 0]
        code = [int(x,base=16) if len(x) == 2 else cls.command_dict[x] for x in precode]
        outStr = ""
        for ele in code:
            outStr += "%02X " % ele
        return outStr
    
    def op(self,opcode):
        #Executes a single opcode
        match opcode:
            case 0x00:
                #PUSH
                #Append value to stack. 
                #Takes one one-byte parameter, the value to be added.
                # In: ...
                # Out ... value
                arg1 = self.getFwd(1) #push value
                self.stack.append(arg1)
                return 1 + 1
            case 0x01:
                #POP
                #Remove top element of stack
                # In: ... value
                # Out: ...
                self.stack.pop()
                return 1
            case 0x02:
                #ADD
                #Pop top two elements of stack, add them, and push result to stack
                # In: ... b a
                # Out: ... (b+a)
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b+a)
                return 1
            case 0x03:
                #SUB
                #Pop top two elements of stack, subtract them, and push result to stack
                # In: ... b a
                # Out: ... (b-a)
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b-a)
                return 1
            case 0x04:
                #MULT
                #Pop top two elements of stack, multiply them, and push result to stack
                # In: ... b a
                # Out: ... (b*a)
                a, b = self.stack.pop(), self.stack.pop()
                self.stack.append(b*a)
                return 1
            case 0x05:
                #DIV
                #Pop top two elements of stack, divide them, and push result to stack
                # In: ... b a
                # Out: ... (b/a)
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
                #RILOAD
                #Load local variable into operand stack.
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
                #RISTORE
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
                self.outStream.write(chr(a))
                self.outStream.flush()
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
                arg1 = self.getuInt16()
                self.stack.append(self.symbols[arg1][1])
                return 1 + 2
            case 0x1d:
                #ILARR
                #Load element of array
                index = self.stack.pop()
                arrayref = self.stack.pop()
                self.stack.append(self.heap[arrayref][2][index])
                return 1
            case 0x1e:
                #ISTARR
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
                newFrame = frame(pc=0,localVars=args,opcodes=funcOps)
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
            case 0x23:
                #FLOAD
                #Loads local variable as float into operand stack 
                #Takes one parameter, the variable index 
                #MACHINA_CALCVLI uses the IEEE 754 standard for floating-point numbers
                arg1 = self.getFwd(1)
                var = self.frame.localVars[arg1]
                var = intToFloat(var)
                self.stack.append(var)
                return 1 + 1
            case 0x24:
                #FLARR
                #Load float from array
                index = self.stack.pop()
                arrayref = self.stack.pop()
                num = self.heap[arrayref][2][index]
                self.stack.append(intToFloat(num))
                return 1
            case 0x25:
                #FSTARR
                #Store float in array
                value = self.stack.pop()
                index = self.stack.pop()
                arrayref = self.stack.pop()
                value = intToFloat(value)
                self.heap[arrayref][2][index] = value
                return 1
            case 0x26:
                #FSTORE
                #Pops top element of stack, Stores as float in variable
                #Takes one one-byte parameter, the variable index
                arg1 = self.getFwd(1)
                a = self.stack.pop()
                a = floatToInt(a)
                self.frame.localVars[arg1] = a
                return 1 + 1
            case 0x27:
                #ITOSI
                #Converts top element from int to signed int
                a = self.stack.pop()
                a = UintToInt(a)
                self.stack.append(a)
                return 1
            case 0x28:
                #SITOI
                #Converts top element from signed into to int
                a = self.stack.pop()
                a = intToUint(a)
                self.stack.append(a)
                return 1
            case 0x29:
                #ITOFL
                a = self.stack.pop()
                a = float(a)
                self.stack.append(a)
                return 1
            case 0x2a:
                #SITOFL
                a = self.stack.pop()
                a = float(a)
                self.stack.append(a)
                return 1
            case 0x2b:
                #INPUT
                #Reads line from inStream, and pushes characters to top of stack. first character is the first in, last char is the last in.
                #After that, it pushes the number of characters added to the top of the stach
                a = self.inStream.readline()
                for char in a:
                    self.stack.append(ord(char))
                self.stack.append(len(a))
                return 1
            case 0x2c:
                #RSARR
                #resizes array
                #Also wipes data from array
                # In: ... newSize aRef
                # Out: ... 
                arrayRef = self.stack.pop()
                newSize = self.stack.pop()
                newLst = [0] * newSize
                self.heap[arrayRef] = (self.heap[arrayRef][0],self.heap[arrayRef][1],newLst)
                return 1
            case 0x2d:
                #SWAP
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a)
                self.stack.append(b)
                return 1
            case 0x2e:
                #MSWAP
                #Swaps top element and nth element from top in stack
                #takes one parameter, the position to swap with in the stack. Top of the stack = 1
                arg1 = self.getFwd(1)
                pos = len(self.stack) - arg1
                a = self.stack[pos]
                self.stack[pos] = self.stack.pop()
                self.stack.append(a)
                return 1 + 1
            case 0x2f:
                #LICONST
                #Loads integer constant from symbol table
                #takes one 1-byte parameter, the index of the constant in the symbol table
                arg1 = self.getFwd(1)
                self.stack.append(self.symbols[arg1][1])
                return 1 + 1
            case 0x30:
                #LSCONST
                #Loads signed integer constant from symbol table
                #Takes one 1-byte parameter, the index of the constant in the symbol table
                arg1 = self.getFwd(1)
                self.stack.append(UintToInt(self.symbols[arg1][1]))
                return 1 + 1
            case 0x31:
                #FLCONST
                #Loads float constant from symbol table
                #Takes one 1-byte parameter, the index of the constant in the symbol table
                arg1 = self.getFwd(1)
                self.stack.append(intToFloat(self.symbols[arg1][1]))
                return 1 + 1
            case 0x32:
                #WIDE
                #Widens next operation
                #Takes one 1-byte parameter, the next operation
                #Ops that can be widened: 0x31, 0x30, 0x2f, 0x1b, 0x11, 0x0c, 0x26, 0x23, 0x00
                nextOp = self.getFwd(1)
                match nextOp:
                    case 0x1b:
                        arg1 = self.getuInt16(1)
                        self.stack.append(self.symbols[arg1][1])
                    case 0x2f:
                        arg1 = self.getuInt16(1)
                        self.stack.append(self.symbols[arg1][1])
                    case 0x30:
                        arg1 = self.getuInt16(1)
                        self.stack.append(UintToInt(self.symbols[arg1][1]))
                    case 0x31:
                        arg1 = self.getuInt16(1)
                        self.stack.append(intToFloat(self.symbols[arg1][1]))
                    case 0x11:
                        arg1 = self.getuInt16(1)
                        a = self.stack.pop()
                        self.frame.localVars[arg1] = a
                    case 0x0c:
                        arg1 = self.getuInt16(1)
                        self.stack.append(self.frame.localVars[arg1])
                    case 0x26:
                        arg1 = self.getuInt16(1)
                        a = self.stack.pop()
                        a = floatToInt(a)
                        self.frame.localVars[arg1] = a
                    case 0x23:
                        arg1 = self.getuInt16(1)
                        var = self.frame.localVars[arg1]
                        var = intToFloat(var)
                        self.stack.append(var)
                    case 0x00:
                        arg1 = self.getuInt16(1) #push value
                        self.stack.append(arg1)

                params = (self.offsetDict[nextOp]-1)
                params *= 2
                return 1 + 1 + params
            case 0x33:
                #YOUR_MOTHER
                #Double Widens next operation
                #Takes one 1-byte parameter, the next operation
                #Ops that can be widened: 0x31, 0x30, 0x2f, 0x1b, 0x11, 0x0c, 0x26, 0x23, 0x00
                nextOp = self.getFwd(1)
                match nextOp:
                    case 0x1b:
                        arg1 = self.getuInt32(1)
                        self.stack.append(self.symbols[arg1][1])
                    case 0x2f:
                        arg1 = self.getuInt32(1)
                        self.stack.append(self.symbols[arg1][1])
                    case 0x30:
                        arg1 = self.getuInt32(1)
                        self.stack.append(UintToInt(self.symbols[arg1][1]))
                    case 0x31:
                        arg1 = self.getuInt32(1)
                        self.stack.append(intToFloat(self.symbols[arg1][1]))
                    case 0x11:
                        arg1 = self.getuInt32(1)
                        a = self.stack.pop()
                        self.frame.localVars[arg1] = a
                    case 0x0c:
                        arg1 = self.getuInt32(1)
                        self.stack.append(self.frame.localVars[arg1])
                    case 0x26:
                        arg1 = self.getuInt32(1)
                        a = self.stack.pop()
                        a = floatToInt(a)
                        self.frame.localVars[arg1] = a
                    case 0x23:
                        arg1 = self.getuInt32(1)
                        var = self.frame.localVars[arg1]
                        var = intToFloat(var)
                        self.stack.append(var)
                    case 0x00:
                        arg1 = self.getuInt32(1) #push value
                        self.stack.append(arg1)
                params = (self.offsetDict[nextOp])
                params *= 4
                return 1 + 1 + params
            case 0x34:
                #EXARR
                #Extends array
                # ... val aRef
                # ...
                ref = self.stack.pop()
                val = self.stack.pop()
                for i in range(val):
                    self.heap[ref][2].append(0) 
                return 1
            case 0x35:
                #NEWOBJ
                #Creates new object in heap
                #Also creates symbol in symbol stack
                #Pushes reference to object to stack
                #Takes four 1-byte parameters: obj width, obj signed, object type, initial size
                objWidth = self.getFwd(1)
                objSigned = bool(self.getFwd(2))
                objType = self.getFwd(3)
                objSize = self.getFwd(4)
                newObj = (objWidth,objSigned,[0]*objSize)
                pos = len(self.heap)
                self.heap.append(newObj)
                self.symbols.append((objType,pos))
                self.stack.append(pos)
                return 1 + 4
            case 0x36:
                #MOD
                #Modulo operator
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b % a)
                return 1
            case 0x37:
                #IDIV
                #Integer division operator
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b // a)
                return 1
            case 0x38:
                #FRONT
                #Moves element to front
                #Takes one argument, the position in te stack to move to the front. 1= the element at the top of the stack
                arg1 = self.getFwd(1)
                a = self.stack.pop(-arg1)
                self.stack.append(a)
                return 1 + 1
            case 0x39:
                #SFRONT
                #Moves element to front, but takes parameter from the stack itself. 1 = the element second highest in the stack (the highest element in the stack is the parameter itself)
                b = self.stack.pop()
                a = self.stack.pop(-b)
                self.stack.append(a)
                return 1
            case 0x3a:
                # BACK
                # Moves top element back in stack. Takes one parameter, the number of spaces to move back 1 = move to second to top
                arg1 = self.getFwd(1)
                a = self.stack.pop()
                self.stack.insert(-arg1,a)
                return 1 + 1
            case 0x3b:
                # SBACK
                # Moves second to top element back in stack. Top element is parameter.
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.insert(b,a)
                return 1
            case 0x3c:
                #ITOSTR
                #Converts top element of stack to roman numeral, puts result on stack sequentially, and puts length of number
                num = self.stack.pop()
                outStr = romNum.to_RomNum(num)
                lenNum = len(outStr)
                for ele in outStr:
                    self.stack.append(ord(ele))
                self.stack.append(lenNum)
                return 1
            case 0x3d:
                #STRTOI
                #Converts top x elements to a string, then converts that string from a roman numeral to a decimal number. The topmost element is the number of elements to convert
                strLen = self.stack.pop()
                outStr = ""
                for ele in range(strLen):
                    char = chr(self.stack.pop())
                    outStr.append(char)
                outNum = romNum.to_decimal(outStr)
                self.stack.append(outNum)
                return 1
            case 0x3e:
                #NEWOBJS
                #Stack-based NEWOBJ command
                #TODO: verify that returning 1 is necessary
                objWidth = self.stack.pop()
                objSigned = bool(self.stack.pop())
                objType = self.stack.pop()
                objSize = self.stack.pop()
                newObj = (objWidth,objSigned,[0]*objSize)
                pos = len(self.heap)
                self.heap.append(newObj)
                self.symbols.append((objType,pos))
                self.stack.append(pos)
                return 1
            case 0x3f:
                #EQL
                #Equality operator. Unlike IFEQ, EQL does not shift, and simply appends the boolean result to stack
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a == b else 0)
                return 1
            case 0x40:
                #NEQL
                #Non-Equality operator. Unlike IFNE, NEQL does not shift, and simply appends the boolean result to stack
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a == b else 0)
                return 1
            case 0x41:
                #GTR
                #Greater than operator. Does not shift
                # ... a b
                # ... (a > b)
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a > b else 0)
                return 1
            case 0x42:
                #LSR
                #Lesser than operator. Does not shift
                # ... a b
                # ... (a < b)
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a < b else 0)
                return 1
            case 0x43:
                #GEQ
                #Greater than or equal to operator. Does not shift
                # ... a b
                # ... (a >= b)
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a >= b else 0)
                return 1
            case 0x44:
                #LEQ
                #Lesser than or equal to operator. Does not shift
                # ... a b
                # ... (a <= b)
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a <= b else 0)
                return 1
            case 0x45:
                #ASSIGN
                #Assigns symbol
                #Takes three parameters: the symbol index to be reassigned (1 byte), the new data type (1 byte), and the new symbol (4 bytes)
                #TODO: Add to wide and quad
                symbolIndex = self.getFwd(1)
                symbolType = self.getFwd(2)
                newSymbol = self.getuInt32(2)
                self.symbols[symbolIndex] = (symbolType,newSymbol)
                return 1 + 1 + 1 + 4
            case 0x46:
                #WGOTO
                #Wide GOTO
                #Takes 1 4-byte parameter: the shift
                arg1 = UintToInt(self.getuInt32())
                return arg1


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
            #print("OPCODES: ", self.frame.opcodes) #Debugging
            while self.frame.pc < len(self.frame.opcodes):
                opcode = self.frame.opcodes[self.frame.pc]
                print("Stack:",self.stack)
                print("Local Vars:",self.frame.localVars)
                print("Heap:")
                for ele in self.heap:
                    print(ele)
                print("Instructions:",self.formatInstructions(showPointer=True))
                print("Program Counter:",self.frame.pc)
                print("Executing {1} ({0})".format('%02X' % opcode,self.decompileOpcode(opcode)))
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
    
    @classmethod
    def compile(cls,textCode: str, safe=True):
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
        # '//' comments out everything after it on the line
        code1 = textCode.split('\n')
        uncommentedCode = ""
        for line in code1:
            #Removes comments
            lineSplit = line.split('//')
            uncommentedCode += (lineSplit[0] + '\n')
        textTup = uncommentedCode.split('#### #### #### ####')

        preheap = textTup[0].strip().split('\n---- ----\n')
        heap = []
        for ele in preheap:
            preObj = re.split('[ \n]',ele)
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
                symbol = (cls.ref_dict[ele[0]],bytesToInt(*bele1,signed=False))
            else:
                symbol = (int(ele[0],base=16),bytesToInt(*bele1,signed=False))
            symbols.append(symbol)

        prevars = textTup[2].strip().split('\n')
        #vars = [int(var) for var in prevars]
        vars = []
        for ele in prevars:
            ele1 = [int(x,16) for x in ele.split()]
            vars.append(bytesToInt(*ele1,signed=False))

        preText = textTup[3].strip()
        precode = re.split('[ ,\n]',preText)
        if safe:
            precode = [x for x in precode if len(x) > 0]
        code = [int(x,base=16) if len(x) == 2 else cls.command_dict[x] for x in precode]
        return (heap,symbols,vars,code)
    
    @classmethod
    def decompileInstructions(cls,code):
        #Decompiles instructions
        #formats instructions into string
        instructionPosList = set() #list of indexes of instructions
        i = 0
        while i < len(code):
            instructionPosList.add(i)
            try:
                off = cls.offsetDict[code[i]]
                if off == 'Double':
                    instructionPosList.add(i)
                    instructionPosList.add(i+1)
                    a = cls.offsetDict[code[i+1]]
                    i += (2 + 2*(a-1))
                elif off == 'Quad':
                    instructionPosList.add(i)
                    instructionPosList.add(i+1)
                    a = cls.offsetDict[code[i+1]]
                    i += (2 + 4*(a-1))
                else:
                    i += cls.offsetDict[code[i]]
            except KeyError:
                i += 1
        instructions = [cls.decompileOpcode(code[i]) if i in instructionPosList else '%02X' % code[i] for i in range(len(code))]
        iStr = '['
        for i in range(len(instructions)):
            iStr += instructions[i] + ', '
        iStr = iStr[:-2]
        iStr += ']'
        return iStr
    def __str__(self):

        symbolstr = ""
        cur = None
        for i in range(len(self.symbols)):
            if i > 0:
                symbolstr += '\n'
            cur = self.symbols[i]
            symbolstr += "{0}: {1} {2}".format(i,self.decompileRef(cur[0]),cur[1])

        heapstr = ""
        cur = None
        for i in range(len(self.heap)):
            if i > 0:
                heapstr += '\n'
            cur = self.heap[i]
            heapstr += "Object {0}: Width={1} Signed={2}\n".format(i,cur[0],cur[1])
            for i in range(len(cur[2])):
                heapstr += '%02X' % cur[2][i]
                if i == len(cur[2]) - 1:
                    break
                if i % 16 == 15:
                    heapstr += '\n'
                else:
                    heapstr += ' '
        
        memstr = ""
        cur = None
        for i in range(len(self.frame.localVars)):
            if i > 0:
                memstr += '\n'
            memstr += "{0}: {1}".format(i,self.frame.localVars[i])
        
        

        outStr = """---------Machina Simvlata Stack Machine---------
verbose: {0}
stack: {1}
symbols:
{2}
heap:
{3}
---------Current Frame---------
program counter: {4}
memory:
{5}
instructions:
{6}
-------------------------------
input stream: {7}
output stream: {8}
------------------------------------------------""".format(self.verbose,self.stack,symbolstr,heapstr,self.frame.pc,memstr,self.formatInstructions(),self.inStream,self.outStream)
        return outStr
    

    def __repr__(self):
        #return "stack_machine(\n    stack={0},\n    memory={1},\n    ops={2},\n    pointer={3}\n)".format(self.stack,self.memory,self.formatInstructions(),self.pointer)
        outstr = "<stack_machine verbose={0} stack={1} symbols={2} heap={3} frames={4} frame={5} inStream={6} outStream={7}>".format(self.verbose,self.stack,self.symbols,self.heap,self.frames,self.frame,self.inStream,self.outStream)
        return outstr

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
        sVal = int.from_bytes(bytecode[p:p+4],'big',signed=False)
        p += 4
        symbol = (sType,sVal)
        symbols.append(symbol)
    
    vars = []
    for i in range(varLen):
        vars.append(int.from_bytes(bytecode[p:p+4],'big',signed=False))
        p += 4
    
    code = []
    for i in range(codeLen):
        code.append(bytecode[p])
        p += 1
    
    return (heap,symbols,vars,code)

def intToBytes(num,size=32):
    #Converts int32s into 4 bytes
    if num < 0:
        num += (1 << size) 
    bytes = []
    for i in range(size//8):
        byte = (num % (1 << size-(8*i))) >> (size - 8 * (i+1))
        bytes.append(byte)
    return tuple(bytes)

def bytesToInt(*args,width=32,signed=False):
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

def intToFloat(var: int):
    #Converts signed or unsigned int into signed float
    #Uses IEEE 754 Binary32 standard
    if var < 0:
        var += (1 << 31)
    sign = var >> 31
    power = ((var % (1 << 31)) >> 23)
    mantissa = (var % (1 << 23))
    mantissa *= (2**-23)
    match power:
        case 0:
            return (-1)**sign * (mantissa * (2**-126))
        case 255:
            if mantissa == 0:
                if sign == 0:
                    return float('inf')
                else:
                    return float('-inf')
            else:
                return float('nan')
        case _:
            mantissa += 1
            power -= 127
            return (-1)**sign * mantissa * (2**power)

def floatToInt(var: float):
    #Converts signed float to unsigned int
    sign = (1 if (var < 0) else 0)
    sign = sign << 31
    var = abs(var)
    vals = math.frexp(var)
    mantissa = vals[0] * 2
    power = vals[1] - 1
    power += 127
    mantissa -= 1
    mantissa = int(mantissa * (2**23))
    power <<= 23 
    a = sign | power | mantissa
    return a

def intToUint(num: int):
    if num < 0:
        return num + (1 << 32)
    else:
        return num

def UintToInt(num: int):
    if (num & (1 << 31)):
        num -= (1 << 32)
    return num



if __name__ == '__main__':
    exe = stack_machine(input=sys.stdin,output=sys.stdout)

    ''' 
    ec = exe.compile(e)
    f = open('lcbin/helloWorld3.mcs','wb')
    f.write(pack(ec))
    f.close()
'''
    '''f = open('lcbin/helloWorld3.mcs','rb')
    fg = f.read()
    f.close()
    fe = unpack(fg)
    exe.initialize(fe[0],fe[1],fe[2],fe[3])
    exe.execute()'''

    romnum = '''
// takes one variable, the integer to be converted to roman numerals
08 00 00
#### #### #### ####
STRING 00 00 00 00
#### #### #### ####
00 04 02 D2
#### #### #### ####
NEWOBJ 08 00 03 01
NEWVAR //Reference string. 2nd var (01)
PUSH 00
NEWVAR //Variable character counter for romnum into string. 3rd var (02)
RILOAD 00
IFEQ 00 06
GOTO 00 2E
PUSH 05 // returns 'NVLLA'
RILOAD 01 // Reference string
RSARR
PUSH 01
PUSH 00
PUSH 4E // N
ISTARR
PUSH 01
PUSH 01
PUSH 56 // V
ISTARR
PUSH 01
PUSH 02
PUSH 4C // L
ISTARR
PUSH 01
PUSH 03
PUSH 4C // L
ISTARR
PUSH 01
PUSH 04
PUSH 41 // A
ISTARR
RILOAD 01 // Reference string
RETURN

PUSH 1B //1B is a special character signifying the beginning of the string TODO
RILOAD 00

IFEQ 01 2B // Begin while loop 0 
RILOAD 00
WIDE PUSH 27 10
MOD
DUP // Stack: temp temp
WIDE PUSH 0F 9F // 3999

IFCLE 00 0B // Begin if conditional 0. Stack: ... temp
WIDE PUSH 03 E8
MOD // Stack ... temp % 1000
GOTO 00 0A // Else
DUP
RILOAD 00
SWAP
SUB // Stack ... temp (Var 00 - (n % 10000))
RISTORE 00 // End if conditional 0

RILOAD 00
WIDE PUSH 03 E8 // 1000
IDIV
RISTORE 00 // Stack: ... temp

DUP // Stack: ... 0x1B temp temp
WIDE PUSH 03 E8
IDIV
DUP // Stack: ... 0x1B temp (temp // 1000) (temp // 1000)

IFEQ 00 0E // Begin while loop 1 Stack: ... 0x1B temp (temp // 1000)
PUSH 4D // Stack: 1 ... 0x1B temp (temp // 1000) 0x4D
MSWAP 03 // Stack: 1 ... 0x1B 0x4D (temp // 1000) temp
SWAP // Stack: 1 ... 0x1B 0x4D temp (temp // 1000)
PUSH 01 // Stack: 1 ... 0x1B 0x4D temp (temp // 1000) 0x01
SUB // Stack: 1 ... 0x1B 0x4D temp ((temp // 1000)-1)
GOTO FF F4 // -12 End while loop 1

POP // Stack: ... (M...M) temp
WIDE PUSH 03 E8 // 1000
MOD // Stack: ... (M...M) (temp % 1000)
DUP // Stack: ... (M...M) temp temp

WIDE PUSH 03 84 // 900 Stack: ... temp temp 900
IFCGE 00 06 // Stack: ... temp
GOTO 00 0E
PUSH 43
SWAP
PUSH 4D
SWAP
WIDE PUSH 03 84
SUB // Stack: ... 0x43 0x4D temp-900
DUP // Stack: ... temp temp

WIDE PUSH 01 F4 // 500
IFCGE 00 06
GOTO 00 0B
PUSH 44
SWAP
WIDE PUSH 01 F4
SUB
DUP // Stack: ... temp temp

WIDE PUSH 01 90 // 400
IFCGE 00 06
GOTO 00 0E
PUSH 43 // Stack: ... temp 0x43
SWAP
PUSH 44
SWAP
WIDE PUSH 01 90
SUB // Stack: ... 0x43 0x44 (temp-400)
DUP

PUSH 64 // 100
IDIV
DUP // Stack: ... temp (temp // 100) (temp // 100)
IFEQ 00 0E // Begin while loop 1 Stack: ... temp (temp // 100)
PUSH 43
MSWAP 03
SWAP // Stack: 1 ... 0x43 temp (temp // 100)
PUSH 01
SUB // Stack: 1 ... 0x43 temp ((temp // 100)-1)
GOTO FF F4 // -12 End while loop 1

POP // Stack: ... temp
PUSH 64 // 100
MOD
DUP // Stack: ... temp temp

PUSH 5A // 90 
IFCGE 00 06
GOTO 00 0C
PUSH 58 // Stack: ... temp 0x58
SWAP
PUSH 43 // D
SWAP
PUSH 5A
SUB
DUP

PUSH 32 // 50
IFCGE 00 06
GOTO 00 09
PUSH 4C
SWAP
PUSH 32
SUB
DUP

PUSH 28 // 40
IFCGE 00 06
GOTO 00 0C
PUSH 58 // Stack: ... temp 0x58
SWAP
PUSH 4C // L
SWAP
PUSH 28
SUB
DUP

PUSH 0A // 10
IDIV
DUP
IFEQ 00 0E // Begin while loop 1 Stack: ... temp (temp // 10)
PUSH 58
MSWAP 03 // Stack: 1 ... 58 (temp // 10) temp
SWAP
PUSH 01
SUB // Stack: 1 ... 58 temp ((temp // 10)-1)
GOTO FF F4 // -12 End while loop 1

POP // Stack: ... temp
PUSH 0A // 10
MOD
DUP // Stack: ... temp temp

PUSH 09 // 9
IFCGE 00 06
GOTO 00 0C
PUSH 49 // Stack: ... temp I
SWAP
PUSH 58 // X
SWAP
PUSH 09
SUB
DUP

PUSH 05
IFCGE 00 06
GOTO 00 09
PUSH 56 // V
SWAP
PUSH 05
SUB
DUP

PUSH 04 //
IFCGE 00 06
GOTO 00 0C
PUSH 49 // Stack: ... temp I
SWAP
PUSH 56 // V
SWAP
PUSH 04
SUB
DUP // Stack: ... temp temp

IFEQ 00 0C // Begin while loop 1 Stack: ... temp
PUSH 49 // Stack: 1 ... temp 0x49
SWAP
PUSH 01
SUB // Stack: 1 ... 0x49 temp-1
GOTO FF F6 // -12 End while loop 1

POP
PUSH 7C
GOTO FE D6

POP
PUSH 02 // Initializes counter, Beginning of outloop, #0
DUP // Stack: (elems) counter counter
SFRONT // Stack: (elems) counter (SeqElem) SeqElem stands for sequenced elem
DUP
DUP
PUSH 1B //Checks for end of string
IFCEQ 00 35 // If end of string, go to #3

PUSH 7C // Stack: (elems) counter (SeqElem) (SeqElem) 7C
IFCEQ 00 0A // GOTO #1 IF TRUE

SWAP // Stack: (elems) (SeqElem) counter
PUSH 01
ADD // Stack: (elems) (seqElems) counter
GOTO FF EE

SWAP // #1 Stack: (elems) 7C counter
DUP // Stack: (elems) 7C counter counter
RILOAD 01
EXARR
SBACK

DUP //Begin if loop
PUSH 7C
IFCEQ 00 10
RILOAD 02
RILOAD 01 //Stack: (elems) Element Index Arref
MSWAP 03
ISTARR
INC 02 01
GOTO FF F0

RILOAD 02
RILOAD 01 //Stack: (elems) Element Index Arref
MSWAP 03
ISTARR
INC 02 01
GOTO FF C6

POP // #3
POP
PUSH 02
SUB
DUP
RILOAD 01
EXARR
DUP
IFEQ 00 15//begin if loop. Stack: (seqElems) counter. Goto #5

SWAP
RILOAD 02
RILOAD 01
MSWAP 03
ISTARR
INC 02 01
PUSH 01
SUB
DUP
GOTO FF EE

RILOAD 01
RETURN
'''

    romnumFunc = '''
08 00 00
#### #### #### ####
STRING 00 00 00 00
#### #### #### ####
00 00 8F FC
00 00 00 00
#### #### #### ####
//Var0 is the number to be converted to romnum
//Var1 is the reference to the string
RILOAD 00
ITOSTR
DUP
RILOAD 01
RSARR
PUSH 01
SUB

DUP //Beginning of if loop. Stack before: (elems) counter | stack after: (elems) counter counter
IFEQ 00 12
SWAP
DUP2
POP //Stack: (elems) counter counter elem
SWAP
RILOAD 01
MSWAP 03
ISTARR
PUSH 01
SUB
GOTO FF F0

RILOAD 01
MSWAP 03
ISTARR
RILOAD 01
RETURN
'''

    rfunc = '''
//Var0 is the number to be converted to romnum
//Var1 is the reference to the string
RILOAD 00
ITOSTR
DUP
RILOAD 01
RSARR
PUSH 01
SUB

DUP //Beginning of if loop. Stack before: (elems) counter | stack after: (elems) counter counter
IFEQ 00 12
SWAP
DUP2
POP //Stack: (elems) counter counter elem
SWAP
RILOAD 01
MSWAP 03
ISTARR
PUSH 01
SUB
GOTO FF F0

RILOAD 01
MSWAP 03
ISTARR
RILOAD 01
RETURN'''

#IDEAS: Add section counter and char counter
#Length of each section will be listed in the stack
#Likely computationally intensive
    newTest = '''
08 00 35 08 00 03 01 22 0C 00 0D 00 06 0A 00 2E // Romnum func. Unfortunately is backwards
00 05 0C 01 2C 00 01 00 00 00 4E 1E 00 01 00 01 
00 56 1E 00 01 00 02 00 4C 1E 00 01 00 03 00 4C 
1E 00 01 00 04 00 41 1E 0C 01 21 00 1B 0C 00 0D 
01 2B 0C 00 32 00 27 10 36 19 32 00 0F 9F 17 00 
0B 32 00 03 E8 36 0A 00 0A 19 0C 00 2D 03 11 00 
0C 00 32 00 03 E8 37 11 00 19 32 00 03 E8 37 19 
0D 00 0E 00 4D 2E 03 2D 00 01 03 0A FF F4 01 32 
00 03 E8 36 19 32 00 03 84 16 00 06 0A 00 0E 00 
43 2D 00 4D 2D 32 00 03 84 03 19 32 00 01 F4 16 
00 06 0A 00 0B 00 44 2D 32 00 01 F4 03 19 32 00 
01 90 16 00 06 0A 00 0E 00 43 2D 00 44 2D 32 00 
01 90 03 19 00 64 37 19 0D 00 0E 00 43 2E 03 2D 
00 01 03 0A FF F4 01 00 64 36 19 00 5A 16 00 06 
0A 00 0C 00 58 2D 00 43 2D 00 5A 03 19 00 32 16 
00 06 0A 00 09 00 4C 2D 00 32 03 19 00 28 16 00 
06 0A 00 0C 00 58 2D 00 4C 2D 00 28 03 19 00 0A 
37 19 0D 00 0E 00 58 2E 03 2D 00 01 03 0A FF F4 
01 00 0A 36 19 00 09 16 00 06 0A 00 0C 00 49 2D 
00 58 2D 00 09 03 19 00 05 16 00 06 0A 00 09 00 
56 2D 00 05 03 19 00 04 16 00 06 0A 00 0C 00 49 
2D 00 56 2D 00 04 03 19 0D 00 0C 00 49 2D 00 01 
03 0A FF F6 01 00 7C 0A FE D6 01 00 00 22 0C 01 
2D 0C 02 2D 1E 0B 02 01 19 00 1B 12 00 15 00 01 
0C 01 34 0C 01 2D 0C 02 2D 1E 0B 02 01 0A FF EB 
0C 01 21
---- ----
08 00 35 08 00 03 01 22 00 00 22 00 00 22 00 00 // prompt func
22 0C 00 1F 11 02 0C 02 0C 03 12 00 0F 0C 00 0C 
03 1D 18 0B 03 01 0A FF F0 2B 2D 01 00 01 03 19 
0C 01 2C 19 0D 00 12 00 01 03 2D 1A 01 0C 01 2E 
03 2D 1E 0A FF F0 0C 01 21
---- ----
08 00 0C 00 1F 22 00 00 22 0C 01 0C 02 12 00 0F // printl func
0C 00 0C 02 1D 18 0B 02 01 0A FF F0 00 0A 18 00
00 21
---- ----
08 00 45 6E 74 65 72 20 74 65 78 74 20 68 65 72 65 3A 20
#### #### #### ####
FUNC 00 00 00 00
FUNC 00 00 00 01
FUNC 00 00 00 02
STRING 00 00 00 03
#### #### #### ####
00 00 4B 9C
#### #### #### ####
LREF 01 //prompt
LREF 03 //String constant
CALL 01
LREF 02 //printl
SWAP
CALL 01
LREF 00
RILOAD 00
CALL 01
LREF 02 //printl
SWAP
CALL 01
'''

    promptTest = """
08 00 00 00 22 00 00 22 00 00 22 0C 00 1F 11 02
0C 02 0C 03 12 00 0F 0C 00 0C 03 1D 18 0B 03 01
0A FF F0 2B 2D 01 00 01 03 19 0C 01 2C 19 0D 00
12 00 01 03 2D 1A 01 0C 01 2E 03 2D 1E 0A FF F0
0C 01 21
---- ----
08 00 0C 00 1F 22 00 00 22 0C 01 0C 02 12 00 0F
0C 00 0C 02 1D 18 0B 02 01 0A FF F0 00 0A 18 00 
00 21
---- ----
08 00 50 6C 65 61 73 65 20 65 6E 74 65 72 20 61
20 73 74 72 69 6E 67 3A 20
---- ----
08 00 00
#### #### #### ####
FUNC 00 00 00 00
FUNC 00 00 00 01
STRING 00 00 00 02
STRING 00 00 00 03
FUNC 00 00 00 04
#### #### #### ####
00 00 00 00
#### #### #### ####
LREF 00
LREF 03
LREF 02 //testing comments
CALL 02 //compiler won't read this
LREF 01
SWAP
CALL 01
PUSH 00
RETURN
"""
    '''
    ac = exe.compile(promptTest)
    f = open('lcbin/promptTest.mcs','wb')
    f.write(pack(ac))
    f.close()
    '''
    #f = open('lcbin/promptTest.mcs','rb')
    #am = f.read()
    #f.close()
    #print("UNPACK")
    #unpack(am)
    ac = exe.compile(promptTest)
    print(exe.compileInstructions(rfunc))
    print(ac)
    exe.initialize(ac[0],ac[1],ac[2],ac[3])
    #print(exe)
    print("INIT")
    exe.execute()
    print(exe)

    newprompt = '''
NEWOBJ 08 00 03 01
NEWVAR //Var 01
PUSH
00
NEWVAR
PUSH
00
NEWVAR
PUSH
00
NEWVAR
RILOAD 00
ARRLEN
RISTORE 02
RILOAD 02
RILOAD 03
IFCEQ 00 0F
RILOAD 00
RILOAD 03
ILARR
CPRINT
INC 03 01
GOTO FF F0
INPUT
SWAP
POP
PUSH 01
SUB
DUP
RILOAD 01
RSARR
DUP
IFEQ 00 12
PUSH 01
SUB
SWAP
DUP2
POP
RILOAD 01
MSWAP 03
SWAP
ISTARR
GOTO FF F0
RILOAD 01
RETURN
'''