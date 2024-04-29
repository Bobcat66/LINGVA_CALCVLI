import ply.yacc as yacc
import NVMERVS_ROMANVS as num
from LINGVA_CALCVLI_LEXER import tokens

# '$' marks a statement
# '@' marks a terminal expression

def p_main(p):
    '''main : FILE_BEGINNING statement
            | main FILE_END'''
    if p[1] == "IMPERO TIBI":
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

def p_terminal_ratio_expr(p):
    'expression : RATIO'
    p[0] = ("@RATIO",p[1])

def p_terminal_char_expr(p):
    'expression : CHARACTER'
    p[0] = ('@CHARACTER',p[1])

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
                      | END_HEADER statement
                      | statement_list END'''
    if p[1] == "TVNC":
        p[0] = [p[2]]
    elif p[1] == "FINIS_TITVLI":
        p[0] = [p[2]]
    else:
        p[0] = p[1]

def p_statement_list_expand(p):
    'statement_list : statement_list statement'
    p[0] = p[1] + [p[2]]

def p_argument(p):
    '''argument : ARGUMENT_KEYWORD expression expression'''
    p[0] = (p[2],p[3])

def p_function_header(p):
    'func_header : BEGIN_HEADER expression expression argument_list'
    p[0] = (p[2],p[3],p[4])
    #p[2] = return type
    #p[3] = name
    #p[4] = arguments

def p_argument_list(p):
    '''argument_list : BEGIN_ARGUMENTS argument
                     | NO_ARGUMENTS
                     | argument_list END_ARGUMENTS'''
    match p[1]:
        case 'INITIVM_ARGVMENTORVM':
            p[0] = [p[2]]
        case 'NVLLVM_ARGVMENTVM':
            p[0] = None
        case _:
            p[0] = p[1]

def p_argument_list_expand(p):
    '''argument_list : argument_list argument'''
    p[0] = p[1] + [p[2]]

def p_function_statement(p):
    '''statement : DECLARE_FUNCTION func_header statement_list END_FUNCTION'''
    p[0] = ('$DECLARE_FUNCTION',p[2],p[3])
    #p[1] = header, p[2] = statement list

def p_return_statement(p):
    '''statement : RETURN expression'''
    p[0] = ('$RETURN',p[2])

def p_call_function_expr(p):
    '''expression : CALL_FUNCTION expression expression_list END_ARGUMENTS
                  | CALL_FUNCTION expression NO_ARGUMENTS'''
    if p[3] == "NVLLVM_ARGVMENTVM":
        p[0] = ('CALL_FUNCTION',p[2],None)
    else:
        p[0] = ('CALL_FUNCTION',p[2],p[3])

def p_call_function_stmt(p):
    '''statement : CALL_FUNCTION_STATEMENT expression expression_list END_ARGUMENTS
                 | CALL_FUNCTION_STATEMENT expression NO_ARGUMENTS'''
    if p[3] == "NVLLVM_ARGVMENTVM":
        p[0] = ('$CALL_FUNCTION',p[2],None)
    else:
        p[0] = ('$CALL_FUNCTION',p[2],p[3])


def p_expression_list(p):
    'expression_list : BEGIN_ARGUMENTS expression'
    p[0] = [p[2]]

def p_expression_list_expand(p):
    'expression_list : expression_list expression'
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
    s = """IMPERO TIBI
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
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM
"""
    a = """IMPERO TIBI
DECLARARE_FVNCTIO INITIVM_TITVLI SCRIPTVM FVNCTION_VNVS INITIVM_ARGVMENTORVM ARGVMENTVM ARG_ONE NVMERVS ARGVMENTVM ARG_TVVO SCRIPTVM FINIS_ARGVMENTORVM FINIS_TITVLI
    DECLARARE_FVNCTIO INITIVM_TITVLI SCRIPTVM FVNCTION_DOS NVLLVM_ARGVMENTVM FINIS_TITVLI
        REDIRE 'HELLO WORLD'
        FINIS
    FINIS_FVNCTIO
    DICERE VOCATERE FVNCTION_DOS NVLLVM_ARGVMENTVM
    REDIRE 'HELLO WORLD'
    FINIS
FINIS_FVNCTIO
VOCATERE_SICVT_IMPERIVM FVNCTION_VNVS INITIVM_ARGVMENTORVM NO. III 'HELLO' FINIS_ARGVMENTORVM
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM"""

    b = """IMPERO TIBI
DECLARARE_FVNCTIO INITIVM_TITVLI SCRIPTVM FVNCTION_VNVS INITIVM_ARGVMENTORVM ARGVMENTVM ARG_ONE NVMERVS ARGVMENTVM ARG_TVVO SCRIPTVM FINIS_ARGVMENTORVM FINIS_TITVLI
    REDIRE 'HELLO WORLD'
FINIS
FINIS_FVNCTIO
VOCATERE_SICVT_IMPERIVM FVNCTION_VNVS INITIVM_ARGVMENTORVM NO. III NO. II FINIS_ARGVMENTORVM
CETERVM AVTEM CENSEO CARTHAGINEM ESSE DELENDAM"""

    result = parser.parse(a)
    print(result)
    #print(result)
#parser structure of code snippet a

[('$DECLARE_FUNCTION', (('@TYPE', 'STRING'), ('@ID', 'FVNCTION_VNVS'), [(('@ID', 'ARG_ONE'), ('@TYPE', 'NUMBER')), (('@ID', 'ARG_TVVO'), ('@TYPE', 'STRING'))]), [
    ('$DECLARE_FUNCTION', (('@TYPE', 'STRING'), ('@ID', 'FVNCTION_DOS'), None), [
        ('$RETURN', ('@STRING', 'HELLO WORLD'))
    ]), 
    ('$PRINT', ('CALL_FUNCTION', ('@ID', 'FVNCTION_DOS'), None)), 
    ('$RETURN', ('@STRING', 'HELLO WORLD'))]), 
 ('$CALL_FUNCTION', ('@ID', 'FVNCTION_VNVS'), [('@NUMBER', 3), ('@STRING', 'HELLO')])]
