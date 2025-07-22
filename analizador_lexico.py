import ply.lex as lex

tokens = [
    'NUMERO', 'MAS', 'MENOS', 'ID', 'TIPO', 'PUNTOYCOMA',
    'CORCHETE_IZQ', 'CORCHETE_DER'
]

# Tipos y tamaños
tipos_con_tamano = {
    'int': 4,
    'float': 8,
    'char': 1
}

tabla_simbolos = {}

# Tokens simples
t_MAS = r'\+'
t_MENOS = r'-'
t_PUNTOYCOMA = r';'
t_CORCHETE_IZQ = r'\['
t_CORCHETE_DER = r'\]'

def t_TIPO(t):
    r'int|float|char'
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t  # devolvemos el token completo (LexToken)

t_ignore = ' \t'

def t_error(t):
    print(f"[Error léxico] Caracter ilegal: '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
