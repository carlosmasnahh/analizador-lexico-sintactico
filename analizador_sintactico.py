import ply.yacc as yacc
from analizador_lexico import tokens, tabla_simbolos, tipos_con_tamano

reglas_gramaticales = []
codigo_intermedio = []

def p_inicio(p):
    '''inicio : lista_expresiones'''
    p[0] = crear_nodo('INICIO', p[1])

def p_lista_expresiones_multiple(p):
    '''lista_expresiones : lista_expresiones expresion'''
    p[0] = p[1] + [p[2]]

def p_lista_expresiones_una(p):
    '''lista_expresiones : expresion'''
    p[0] = [p[1]]

def agregar_regla(p, definicion):
    reglas_gramaticales.append(definicion)
    p[0] = crear_nodo(p[2], [p[1], p[3]])

def crear_nodo(nombre, hijos=None, tipo=None):
    if isinstance(hijos, list) and len(hijos) == 1 and not isinstance(hijos[0], tuple):
        tipo_info = f" (tipo={tipo})" if tipo else ""
        return (f"{nombre}: {hijos[0]}{tipo_info}", [])
    return (nombre, hijos or [])

# Declaración simple: int x;
def p_declaracion_variable(p):
    'expresion : TIPO ID PUNTOYCOMA'
    reglas_gramaticales.append("expresion → TIPO ID ;")
    tipo = p[1]
    nombre = p[2]
    tabla_simbolos[nombre] = {'tipo': tipo, 'tamaño': tipos_con_tamano[tipo]}
    p[0] = crear_nodo('DECLARACION', [f"{tipo} {nombre}"], tipo)

# Arreglo: int lista[10];
def p_declaracion_arreglo(p):
    'expresion : TIPO ID CORCHETE_IZQ NUMERO CORCHETE_DER PUNTOYCOMA'
    reglas_gramaticales.append("expresion → TIPO ID [ NUMERO ] ;")
    tipo = p[1]
    nombre = p[2]
    tamaño_total = tipos_con_tamano[tipo] * p[4]
    tabla_simbolos[nombre] = {'tipo': f'{tipo}[{p[4]}]', 'tamaño': tamaño_total}
    p[0] = crear_nodo('ARREGLO', [f"{tipo} {nombre}[{p[4]}]"], tipo)

# Suma y resta
def p_expresion_suma(p):
    'expresion : expresion MAS termino'
    agregar_regla(p, "expresion → expresion + termino")
    temp = f"t{len(codigo_intermedio)+1}"
    codigo_intermedio.append(f"{temp} = {p[1][0]} + {p[3][0]}")
    p[0] = (temp, [])

def p_expresion_resta(p):
    'expresion : expresion MENOS termino'
    agregar_regla(p, "expresion → expresion - termino")
    temp = f"t{len(codigo_intermedio)+1}"
    codigo_intermedio.append(f"{temp} = {p[1][0]} - {p[3][0]}")
    p[0] = (temp, [])

def p_expresion_termino(p):
    'expresion : termino'
    reglas_gramaticales.append("expresion → termino")
    p[0] = p[1]

def p_termino_numero(p):
    'termino : NUMERO'
    reglas_gramaticales.append("termino → NUMERO")
    p[0] = crear_nodo('NUM', [p[1]], 'int')

def p_termino_id(p):
    'termino : ID'
    reglas_gramaticales.append("termino → ID")
    if p[1] not in tabla_simbolos:
        raise Exception(f"[Error semántico] Variable '{p[1]}' no declarada.")
    tipo = tabla_simbolos[p[1]]['tipo']
    p[0] = crear_nodo('ID', [p[1]], tipo)

def p_error(p):
    if p:
        p[0] = (f"[Error sintáctico] Token inesperado: {p.value}", [])
    else:
        p[0] = ("[Error sintáctico] Fin de entrada inesperado", [])

parser = yacc.yacc(start='inicio')