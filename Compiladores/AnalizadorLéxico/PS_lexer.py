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
    'STRING',
    'VTRUE',
    'VFALSE',
    'VIDENTIFIER',
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

#regular expressions

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

def t_MLCOMM(t):
    r'/*[^"]*\*/'
    return t

def t_ILCOMM(t):
    r'(//.*)'
    return t

def t_STRING(t):
    r'"[^"]*"'
    return t

def t_VTRUE(t):
    r'duì'
    return t

def t_VFALSE(t):
    r'cuò'
    return t

t_VIDENTIFIER =  r'([a-z]|[A-Z])([a-z]|[A-Z]|[0-9])*'
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
 
 # Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
 
lexer = lex.lex()

#input
data = '''
// Fibonacci numbers in PīnyīnScript
gōngnéng fibonacci(n) {
    rúguǒ (n <= 1) {
        fǎnhuí n;
    } biéde {
        fǎnhuí fibonacci(n - 1) + fibonacci(n - 2);
    }
}

zhǔyàode {
    zhěngshù f = fibonacci(10);
    dǎyìn -> "The first ten numbers of Fibonacci are: ";
    dǎyìn -> f;
}

// Print numbers backwards in PīnyīnScript
gōngnéng printReverse(n) {
    rúguǒ (n >= 1) {
        dǎyìn -> n;
        printReverse(n - 1);
    }
}

zhǔyàode {
    printReverse(100);
}

// Sum function in PīnyīnScript
gōngnéng sum(x, y) {
    fǎnhuí x + y;
}

zhǔyàode {
    zhěngshù result = sum(9, 5);
    dǎyìn -> "The result is: ";
    dǎyìn -> result;
}

// Hello world in PīnyīnScript
zhǔyàode {
    dǎyìn -> "Hello world!!";
}

// Iterative factorial in PīnyīnScript
gōngnéng iterativeFactorial(x) {
    zhěngshù result = 1;
    pàn (zhěngshù i = 1; i <= x; i++)
        result = result * i;
    }
    fǎnhuí result;
}

// Recursive factorial in PīnyīnScript
gōngnéng recursiveFactorial(x) {
    rúguǒ (x <= 1) {
        fǎnhuí 1;
    } biéde {
        fǎnhuí x * recursiveFactorial(x - 1);
    }
}

zhǔyàode {
    zhěngshù n = 5;
    zhěngshù result = recursiveFactorial(n);
    dǎyìn -> "The result is : ";
    dǎyìn -> result;
}
'''

lexer.input(data)

#tokens generator
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    #print(tok)
    print(tok.type, tok.value, tok.lineno, tok.lexpos)