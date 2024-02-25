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
    '''expression : TRUE
                  | FALSE'''
    val = p[1] == 'VERVM'
    p[0] = ("@BOOLEAN",val)

def p_terminal_type_expr(p):
    '''expression : STRING_TYPE
                  | NUMBER_TYPE
                  | RATIO_TYPE
                  | BOOLEAN_TYPE'''
    val = 'NONE'
    match p[1]:
        case 'SCRIPTVM':
            val = 'STRING'
        case 'NVMERVS':
            val = 'NUMBER'
        case 'PARS_NVMERI':
            val = 'RATIO'
        case 'PROPOSITIO':
            val = 'BOOLEAN'
    p[0] = ("@TYPE",val)

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

def p_while_statement(p):
    'statement : WHILE expression statement_list END_LOOP'
    p[0] = ('$WHILE',p[2],p[3])

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

def p_variables(p):
    '''statement : DECLARE_VAR expression expression
                 | ASSIGN_VAR expression expression
                 | INCREMENT expression
                 | DECREMENT expression'''
    match p[1]:
        case 'DECLARO':
            p[0] = ('$DECLARE_VAR',p[2],p[3])
        case 'ASSIGNO':
            p[0] = ('$ASSIGN_VAR',p[2],p[3])
        case 'INCREMENTVM':
            p[0] = ('$INCREMENT',p[2])
        case 'DECREMENTVM':
            p[0] = ('$DECREMENT',p[2])

def p_variable_expr(p):
    '''expression : CAST_VAR expression expression'''
    match p[1]:
        case 'IMAGO':
            p[0] = ('CAST_VAR',p[2],p[3])
        
def p_array_statements(p):
    '''statement : DECLARE_ARR expression expression expression
                 | EDIT_ARR expression expression expression
                 | ASSIGN_ARR expression expression
                 | DELETE_ELE expression expression
                 | APPEND expression expression'''
    
    match p[1]:
        case 'ORDO_DECLARO':
            p[0] = ('$DECLARE_ARR',p[2],p[3],p[4])
        case 'ORDO_IMMVTO':
            p[0] = ('$EDIT_ARR',p[2],p[3],p[4])
        case 'ORDO_ASSIGNO':
            p[0] = ('$ASSIGN_ARR',p[2],p[3])
        case 'ERADO':
            p[0] = ('$DELETE_ELE',p[2],p[3])
        case 'ADDO':
            p[0] = ('$APPEND',p[2],p[3])

def p_array_expr(p):
    '''expression : RETRIEVE_ELE expression expression
                  | CONVERT_TO_ARRAY expression
                  | LENGTH expression'''
    match p[1]:
        case 'EXPROMO':
            p[0] = ('RETRIEVE_ELE',p[2],p[3])
        case 'VT_ORDO':
            p[0] = ('CONVERT_TO_ARRAY',p[2])
        case 'LONGITVDO':
            p[0] = ('LENGTH',p[2])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

if __name__ == '__main__':
    s = """IMPERIVM MEVM INVOCO ET PRAECIPIO TIBI
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
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
"""
    result = parser.parse(s)
    for ele in result:
        print(ele)
    #print(result)