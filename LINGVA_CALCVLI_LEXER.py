import re
from dataclasses import dataclass
import ply.lex as lex
import NVMERVS_ROMANVS 

#TODO: properly Conjugate reserved words
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
    'ORDO_DECLARO' : 'DECLARE_ARR', #statement
    'ORDO_IMMVTO' : 'EDIT_ARR', #statement
    'ORDO_ASSIGNO' : 'ASSIGN_ARR', #statement
    'VT_ORDO' : 'CONVERT_TO_ARRAY', #expression
    'EXPROMO' : 'RETRIEVE_ELE', #expression
    'ERADO' : 'DELETE_ELE', #statement
    'ADDO' : 'APPEND', #statement
    'LONGITVDO' : 'LENGTH', #expression

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
    'DECLARARE_FVNCTIO' : 'DECLARE_FUNCTION',
    'FINIS_FVNCTIO' : 'END_FUNCTION',
    'ARGVMENTVM' : 'ARGUMENT_KEYWORD',
    'INITIVM_ARGVMENTORVM' : 'BEGIN_ARGUMENTS',
    'FINIS_ARGVMENTORVM' : 'END_ARGUMENTS',
    'INITIVM_TITVLI' : 'BEGIN_HEADER',
    'FINIS_TITVLI' : 'END_HEADER',
    'NVLLVM_ARGVMENTVM' : 'NO_ARGUMENTS',
    'REDIRE' : 'RETURN',
    'VOCATERE' : 'CALL_FUNCTION',
    'VOCATERE_SICVT_IMPERIVM' : 'CALL_FUNCTION_STATEMENT',

    #LOGIC
    'NON' : 'NOT',
    'VEL' : 'OR',
    'AVT' : 'XOR',
    'ET' : 'AND',

    #TYPE
    'SCRIPTVM' : 'STRING_TYPE',
    'NVMERVS' : 'NUMBER_TYPE',
    'PARS_NVMERI' : 'RATIO_TYPE',
    'PROPOSITIO' : 'BOOLEAN_TYPE',
    'CHARACTER' : 'CHARACTER_TYPE',

    #BOOLEAN VALUES
    'VERVM' : 'TRUE',
    'FALSVM' : 'FALSE'
}

tokens = [
    'FILE_BEGINNING',
    'FILE_END',
    'STRING',
    'NUMBER',
    'CHARACTER',
    'ID'
] + list(reserved.values())

def t_FILE_BEGINNING(t):
    r"IMPERO[ ]TIBI"
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

def t_CHARACTER(t):
    r'CHAR .'
    t.value = t.value[5]

def t_ID(t):
    r'[ABCDEFGHIKLMNOPQRSTVXYZ_]+\b'
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
IMPERO TIBI
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
