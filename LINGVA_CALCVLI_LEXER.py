import re
from dataclasses import dataclass
import ply.lex as lex
import NVMERVS_ROMANVS 

reserved = {

    #ARITHMETIC OPERATORS
    'SVMMA' : 'ADD',
    'DIFFERENTIA' : 'SUBTRACT',
    'PRODVCTVM' : 'MULTIPLY',
    'PROPORTIO' : 'DIVIDE',

    #VARIABLE STATEMENTS
    'DECLARO' : 'DECLARE_VAR',
    'ASSIGNO' : 'ASSIGN_VAR',
    'INCREMENTVM' : 'INCREMENT',
    'DECREMENTVM' : 'DECREMENT',
    'IMAGO' : 'CAST_VAR',

    #COMPARATORS
    'PAR' : 'EQUALS',
    'MAIOR' : 'GREATER',
    'MAIOR_VP' : 'GREATER_OR_EQUAL',
    'MINOR' : 'LESSER',
    'MINOR_VP' : 'LESSER_OR_EQUAL',

    #ARRAYS
    'ORDO_DECLARO' : 'DECLARE_ARR',
    'ORDO_ASSIGNO' : 'ASSIGN_ARR',
    'UT_ORDO' : 'CONVERT_TO_ARRAY',
    'EXPROMO' : 'RETRIEVE_ELE',
    'ERADO' : 'DELETE_ELE',
    'ADDO' : 'APPEND',
    'LONGITVDO' : 'LENGTH',

    #I/O
    'DICERE' : 'PRINT',
    'PROMPTVS' : 'PROMPT',

    #CONTROL FLOW
    'SI' : 'IF',
    'SIN' : 'ELIF',
    'ALITER' : 'ELSE',
    'TVNC' : 'THEN',
    'FINIS' : 'END',
    'FINIS_CIRCVITVS' : 'END_LOOP',
    'DVM' : 'WHILE',

    #LOGIC
    'NON' : 'NOT',
    'VEL' : 'OR',
    'AVT' : 'XOR',
    'ET' : 'AND',
}

tokens = [
    'FILE_BEGINNING',
    'FILE_END',
    'STRING',
    'NUMBER',
    'BOOLEAN',
    "ID"
] + list(reserved.values())

def t_FILE_BEGINNING(t):
    r"IMPERIVM[ ]MEVM[ ]INVOCO[ ]ET[ ]PRAECIPIO[ ]TIBI"
    return t

def t_FILE_END(t):
    r"CETERVM[ ]AVTEM[ ]CENSEO[ ]CARTHAGINEM[ ]ESSE[ ]DELENDAM"
    return t

def t_STRING(t):
    #The program won't recognize " for some reason, so strings are defined with single-quotes
    r"\'[^']+\'"
    t.value = t.value[1:-1]
    return t

def t_NUMBER(t):
    r'NO[.][ ](?:[IVXLCDM]+|NVLLA)'
    t.value = NVMERVS_ROMANVS.to_decimal(t.value[4:])
    return t

def t_BOOLEAN(t):
    r'\b(?:VERVM|FALSVM)\b'
    t.value = t.value == 'VERVM'
    return t

def t_ID(t):
    r'[ABCDEFGHIKLMNOPQRSTVYZ_]+\b'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

t_ignore  = ' \t'

#Build the lexer
lexer = lex.lex()

if __name__ == "__main__":

    data = '''
IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
DECLARO INTCOVNTER PARS_NVMERI
ASSIGNO INTCOVNTER NO. V
DVM MAIOR INTCOVNTER NO. NVLLA TVNC
DICERE 'Hello world'
DICERE VERVM FALSVM
DECREMENTVM INTCOVNTER
FINIS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
'''
    # Give the lexer some input
    lexer.input(data)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: 
            break      # No more input
        print(tok)
