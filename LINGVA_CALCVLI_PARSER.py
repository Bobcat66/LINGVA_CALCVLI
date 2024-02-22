import ply.yacc as yacc
import NVMERVS_ROMANVS as num
from LINGVA_CALCVLI_LEXER import tokens

# '$' marks a statement
# '@' marks a terminal expression

def p_main(p):
    '''main : FILE_BEGINNING statement
            | main FILE_END'''
    if p[1] == "IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI":
        p[0] = [p[2]]
    else:
        p[0] = p[1]

def p_main_statement(p):
    '''main : main statement'''
    p[0] = p[1] + [p[2]]

def p_print_statement(p):
    'statement : PRINT expression'
    p[0] = ("$PRINT",p[2])

def p_prompt(p):
    'expression : PROMPT expression'
    p[0] = ('@PROMPT',p[2])

def p_terminal_string_expr(p):
    'expression : STRING'
    p[0] = ("@STRING",p[1])

def p_terminal_number_expr(p):
    'expression : NUMBER'
    p[0] = ("@NUMBER",p[1])

def p_terminal_boolean_expr(p):
    'expression : BOOLEAN'
    p[0] = ("@BOOLEAN",p[1])

def p_terminal_id_expr(p):
    'expression : ID'
    p[0] = ("@ID",p[1])

def p_binary_operators(p):
    '''expression : ADD expression expression
                  | SUBTRACT expression expression
                  | MULTIPLY expression expression
                  | DIVIDE expression expression'''
    match p[1]:
        case 'SVMMA':
            p[0] = ('ADD',p[2],p[3])
        case 'DIFFERENTIA':
            p[0] = ('SUBTRACT',p[2],p[3])
        case 'PRODVCTVM':
            p[0] = ('MULTIPLY',p[2],p[3])
        case 'PROPORTIO':
            p[0] = ('DIVIDE',p[2],p[3])

def p_logic_operators(p):
    '''expression : AND expression expression
                  | OR expression expression
                  | XOR expression expression
                  | NOT expression'''
    match p[1]:
        case 'ET':
            p[0] = ('AND',p[2],p[3])
        case 'VEL':
            p[0] = ('OR',p[2],p[3])
        case 'AVT':
            p[0] = ('XOR',p[2],p[3])
        case 'NON':
            p[0] = ('NOT',p[2])

def p_comparators(p):
    '''expression : EQUALS expression expression
                  | GREATER expression expression
                  | GREATER_OR_EQUAL expression expression
                  | LESSER expression expression
                  | LESSER_OR_EQUAL expression expression'''
    match p[1]:
        case 'PAR':
            p[0] = ('EQUALS',p[2],p[3])
        case 'MAIOR':
            p[0] = ('GREATER',p[2],p[3])
        case 'MAIOR_VP':
            p[0] = ('GREATER_OR_EQUAL',p[2],p[3])
        case 'MINOR':
            p[0] = ('LESSER',p[2],p[3])
        case 'MINOR_VP':
            p[0] = ('LESSER_OR_EQUAL',p[2],p[3])

def p_if_statement_begin(p):
    'if_statement : IF expression statement_list'
    p[0] = [('IF',p[2],p[3])]

def p_elif_statement(p):
    'if_statement : if_statement ELIF expression statement_list'
    p[0] = p[1] + [('ELIF',p[3],p[4])]

def p_else_statement(p):
    'if_statement : if_statement ELSE statement_list'
    p[0] = p[1] + [('ELSE',p[3])]

def p_end_if_statement(p):
    'statement : if_statement END_LOOP'
    p[0] = tuple(["$IF"] + p[1])

def p_statement_list(p):
    '''statement_list : THEN statement
                      | statement_list END'''
    if p[1] == "TVNC":
        p[0] = [p[2]]
    else:
        p[0] = p[1]

def p_statement_list_expand(p):
    'statement_list : statement_list statement'
    p[0] = p[1] + [p[2]]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

s = """IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
DICERE 'SALVE MVNDI'
SI VEL MAIOR SVMMA NO. VIII NO. VI NO. V MAIOR_VP NO. VI NO. IV TVNC
DICERE 'op one'
FINIS SIN MINOR NO. V PROPORTIO NO. I NO. IV TVNC
DICERE 'op two'
FINIS ALITER TVNC
DICERE 'op three'
FINIS
FINIS_CIRCVITVS
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
"""

# (3 * 4) + (3 / 4)
# should return 12.75
result = parser.parse(s)
#print(result)
for ele in result:
    print(ele)