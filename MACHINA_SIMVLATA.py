#virtual machine for executing LINGVA CALCVLI code

variables = [] #list of variables
array = [] #list of arrays
funcs = [] #list of functions
call_stack = []
expression_stack = []

"""
Commands:

"""

class stack_machine():
    command_dict = [
        'PUSH', #self.stack.append()
        'ADD', 
        'SUBTRACT'
        'MULTIPLY',
        'DIVIDE',
        'AND',
        'OR',
        'XOR',
        'NEGATE',
        'RETURN'
    ]
    def __init__(self):
        self.stack = []
        self.memory = {}

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

exp.push(23)
exp.push(10)
exp.push(19)
exp.add()
exp.multiply()
print(exp.stack)
# 23 10 19 + *
# 23 29 *
# 667
        
