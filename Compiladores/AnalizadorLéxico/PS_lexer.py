#library
import ply.lex as lex

#tokens
tokens = (
    'MAIN',
    'FUNCTION',
    'FOR',
    'IF',
    'ELSE',
    'DTSTRING',   
    'DTINTEGER',
    'DTFLOAT',
    'DTBOOL',
    'PRINT',
    'RETURN',
    'MLCOMM',
    'ILCOMM',
    'VSTRING',
    'VTRUE',
    'VFALSE',
    'IDENTIFIER',
    'VINTEGER',
    'VFLOAT',
    'EQUAL',
    'INEQUAL',  
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'GREATERTH',
    'LESSTH',
    'OPENKEY',
    'CLOSEKEY',
    'OPENPAR',
    'CLOSEPAR',
    'PRINTOP',
    'ENDST',
    'COMMA'
)

#regular expressions in functions
def t_MAIN(t):
    r'zhǔyàode'
    return t

def t_FUNCTION(t):
    r'gōngnéng'
    return t

def t_FOR(t):
    r'pàn'
    return t

def t_IF(t):
    r'rúguǒ'
    return t

def t_ELSE(t):
    r'biéde'
    return t

def t_DTSTRING(t):
    r'liàn'
    return t

def t_DTINTEGER(t):
    r'zhěngshù'
    return t

def t_DTFLOAT(t):
    r'fúliú'
    return t

def t_DTBOOL(t):
    r'bùér'
    return t

def t_PRINT(t):
    r'dǎyìn'
    return t

def t_RETURN(t):
    r'fǎnhuí'
    return t

def t_VTRUE(t):
    r'duì'
    return t

def t_VFALSE(t):
    r'cuò'
    return t
    
def t_MLCOMM(t):
    r'/*[^"]*\*/'
    return t

def t_ILCOMM(t):
    r'(//.*)'
    return t

def t_VSTRING(t):
    r'"[^"]*"'
    return t

#regular expressions in variables
t_IDENTIFIER =  r'([a-z]|[A-Z])([a-z]|[A-Z]|[0-9])*'
t_VINTEGER = r'[0-9]+'
t_VFLOAT = r'[0-9]*\.[0-9]+'
t_EQUAL = r'\='
t_INEQUAL = r'≠'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_GREATERTH = r'>'
t_LESSTH = r'<'
t_OPENKEY = r'\{'
t_CLOSEKEY = r'\}'
t_OPENPAR = r'\('
t_CLOSEPAR = r'\)'
t_PRINTOP = r'->'
t_ENDST = r';'
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
def parse_file(filename, output_file):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
        lexer.input(data)
        with open(output_file, 'w', encoding='utf-8') as output:
            while True:
                tok = lexer.token()
                if not tok: 
                    break
                output.write(f"{tok.type} {tok.value} {tok.lineno} {tok.lexpos}\n")

parse_file('PS_examples.txt', 'tokens.txt')