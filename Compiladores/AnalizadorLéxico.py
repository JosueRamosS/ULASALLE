#library
import ply.lex as lex

#tokens
tokens = (
    'MLCOMM',
    'ILCOMM',
    'MAIN',
    'RETURN',
    'FOR',
    'IF',
    'ELSE',
    'PRINT',
    'DTINTEGER',
    'DTFLOAT',
    'DTSTRING',   
    'DTCHAR',
    'DTBOOL',
    'DTVOID',
    'IDENTIFIER',
    'EQUAL',
    'ASSIGN',
    'VINTEGER',
    'VFLOAT',
    'VSTRING',
    'VCHAR',
    'VTRUE',
    'VFALSE',
    'OPINC',
    'OPDC',
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'MOD',
    'AND',
    'OR',
    'NOT',
    'GREATERTH',
    'LESSTH',
    'GREATEQTH',
    'LESSEQTH',
    'NOTEQUAL',  
    'OKEY',
    'CKEY',
    'OPAR',
    'CPAR',
    'DOTCOMMA',
    'COMMA'
)

#regular expressions in functions
def t_MLCOMM(t):
    r'/*[^"]*\*/'
    return t

def t_ILCOMM(t):
    r'(//.*)'
    return t

def t_MAIN(t):
    r'主'
    return t

def t_RETURN(t):
    r'回'
    return t

def t_FOR(t):
    r'圈'
    return t

def t_IF(t):
    r'如果'
    return t

def t_ELSE(t):
    r'否则'
    return t

def t_PRINT(t):
    r'打印'
    return t

def t_DTINTEGER(t):
    r'整数'
    return t

def t_DTFLOAT(t):
    r'小数 '
    return t

def t_DTSTRING(t):
    r'文本'
    return t

def t_DTCHAR(t):
    r'字'
    return t

def t_DTBOOL(t):
    r'逻辑 '
    return t

def t_DTVOID(t):
    r'空 '
    return t

def t_IDENTIFIER(t):
    r'([a-z]|[A-Z])([a-z]|[A-Z]|[0-9])*'
    return t

def t_EQUAL(t):
    r'\=\='
    return t

def t_ASSIGN(t):
    r'\='
    return t

def t_VFLOAT(t):
    r'[0-9]+\.[0-9]+'
    return t

def t_VINTEGER(t):
    r'[0-9]+'
    return t

def t_VSTRING(t):
    r'"[^"]*"'
    return t

def t_VCHAR(t):
    r'"[^"]"'

def t_VTRUE(t):
    r'对'
    return t

def t_VFALSE(t):
    r'错'
    return t

def t_OPINC(t):
    r'\+\+'
    return t

def t_PLUS(t):
    r'\+'
    return t

def t_OPDC(t):
    r'--'
    return t

def t_MINUS(t):
    r'-'
    return t

#regular expressions in variables
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'%'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_GREATERTH = r'>'
t_LESSTH = r'<'
t_GREATEQTH = r'>='
t_LESSEQTH = r'<='
t_NOTEQUAL = r'!='
t_OKEY = r'\{'
t_CKEY = r'\}'
t_OPAR = r'\('
t_CPAR = r'\)'
t_DOTCOMMA = r';'
t_COMMA = r','

#line break
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#ignore spaces and tabs
t_ignore  = ' \t'
 
 #error handling 
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
 
lexer = lex.lex()

#read PS_examples.txt (source code examples)
#output tokens in tokens.txt

def parse_file(filename):
    types_string = ""  # Inicializa una cadena vacía para acumular los tipos de los tokens
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok: 
                break
            types_string += tok.type + " "  # Concatena el tipo de cada token a la cadena de tipos

    return types_string.strip()  # Elimina el espacio extra al final

def parse_file_to_list(filename):
    token_values = []  # Lista para almacenar los valores de los tokens

    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok: 
                break
            token_values.append(tok.value)  # Almacena el valor del token en la lista

    # token_values_str = ' '.join(token_values)
    return token_values

# Ejemplo de uso
listaCodFuente = parse_file_to_list('Entrada.txt')
# print(listaCodFuente)
# print(token_values_list)

# Usar la función y almacenar los tipos de los tokens en una variable
token_types = parse_file('Entrada.txt')
# print(token_types)