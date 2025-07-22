import ply.yacc as yacc
from analizador_lexico import tokens, tabla_simbolos, tipos_con_tamano

reglas_gramaticales = []
reglas_optimizacion = []
codigo_intermedio = []
temporales = {'contador': 1}

def nuevo_temp():
    temp = f"t{temporales['contador']}"
    temporales['contador'] += 1
    return temp

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
    # No asignar aquí, esto debe hacerse en cada función específica

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
    reglas_gramaticales.append("expresion → expresion + termino")
    valor1 = p[1][0].split(': ')[1].split()[0] if isinstance(p[1], tuple) and ': ' in p[1][0] else str(p[1])

    valor3 = p[3][0].split(': ')[1].split()[0] if isinstance(p[3], tuple) and ': ' in p[3][0] else str(p[3])

    temp = nuevo_temp()
    codigo_intermedio.append(f"{temp} = {valor1} + {valor3}")
    tabla_simbolos[temp] = {'tipo': 'int', 'tamaño': 4, 'usada': True}
    p[0] = crear_nodo(temp, [])  # El nodo devuelve solo el nombre del temporal

def p_expresion_resta(p):
    'expresion : expresion MENOS termino'
    reglas_gramaticales.append("expresion → expresion - termino")
    valor1 = p[1][0].split(': ')[1].split()[0] if isinstance(p[1], tuple) and ': ' in p[1][0] else str(p[1])

    valor3 = p[3][0].split(': ')[1].split()[0] if isinstance(p[3], tuple) and ': ' in p[3][0] else str(p[3])

    temp = nuevo_temp()
    codigo_intermedio.append(f"{temp} = {valor1} - {valor3}")
    tabla_simbolos[temp] = {'tipo': 'int', 'tamaño': 4, 'usada': True}
    p[0] = crear_nodo(temp, [])

# Asignación de expresión aritmética a variable: x = 2 + 3;
def p_expresion_asignacion(p):
    'expresion : ID IGUAL expresion PUNTOYCOMA'
    reglas_gramaticales.append("expresion → ID = expresion ;")
    
    var = p[1]
    if var not in tabla_simbolos:
        if var.startswith("t") and var[1:].isdigit():
            tabla_simbolos[var] = {'tipo': 'int', 'tamaño': 4}
        else:
            raise Exception(f"[Error semántico] Variable '{var}' no declarada.")

    # Obtenemos el valor de la expresión (puede ser un temporal)
    if isinstance(p[3], tuple):
        if ": " in p[3][0]:
            valor = p[3][0].split(': ')[1].split()[0]
        else:
            valor = p[3][0]
    else:
        valor = str(p[3])

    tabla_simbolos[var]['usada'] = True
    codigo_intermedio.append(f"{var} = {valor}")
    p[0] = crear_nodo('ASIGNACION', [f"{var} = {valor}"])

def p_expresion_termino(p):
    'expresion : termino'
    reglas_gramaticales.append("expresion → termino")
    p[0] = p[1]

def p_expresion_for(p):
    'expresion : FOR ID IGUAL NUMERO TO NUMERO THEN ID IGUAL NUMERO PUNTOYCOMA'
    reglas_gramaticales.append("expresion → for ID = NUMERO to NUMERO then ID = NUMERO ;")

    indice = p[2]
    inicio_valor = p[4]
    fin_valor = p[6]
    var = p[8]
    valor = p[10]

    # Declarar índice si no existe
    if indice not in tabla_simbolos:
        tabla_simbolos[indice] = {'tipo': 'int', 'tamaño': 4}
    if var not in tabla_simbolos:
        raise Exception(f"[Error semántico] Variable '{var}' no declarada.")

    tabla_simbolos[indice]['usada'] = True
    tabla_simbolos[var]['usada'] = True

    etiqueta_inicio = f"L{temporales['contador']}"
    temporales['contador'] += 1
    etiqueta_cuerpo = f"L{temporales['contador']}"
    temporales['contador'] += 1
    etiqueta_fin = f"END_{etiqueta_inicio}"

    # Código intermedio
    codigo_intermedio.append(f"{indice} = {inicio_valor}")
    codigo_intermedio.append(f"{etiqueta_inicio}:")
    codigo_intermedio.append(f"IF {indice} <= {fin_valor} GOTO {etiqueta_cuerpo}")
    codigo_intermedio.append(f"GOTO {etiqueta_fin}")
    codigo_intermedio.append(f"{etiqueta_cuerpo}: {var} = {valor}")
    codigo_intermedio.append(f"{indice} = {indice} + 1")
    codigo_intermedio.append(f"GOTO {etiqueta_inicio}")
    codigo_intermedio.append(f"{etiqueta_fin}:")

    p[0] = crear_nodo("FOR", [f"{indice} = {inicio_valor} to {fin_valor}", f"{var} = {valor}"])

def p_expresion_while(p):
    'expresion : WHILE ID THEN ID IGUAL NUMERO PUNTOYCOMA'
    reglas_gramaticales.append("expresion → while ID then ID = NUMERO ;")
    cond = p[2]
    var = p[4]
    valor = p[6]

    if cond not in tabla_simbolos:
        raise Exception(f"[Error semántico] Variable condicional '{cond}' no declarada.")
    if var not in tabla_simbolos:
        raise Exception(f"[Error semántico] Variable destino '{var}' no declarada.")

    tabla_simbolos[cond]['usada'] = True
    tabla_simbolos[var]['usada'] = True

    inicio = f"L{temporales['contador']}"
    temporales['contador'] += 1
    cuerpo = f"L{temporales['contador']}"
    temporales['contador'] += 1
    fin = f"END_{inicio}"

    codigo_intermedio.append(f"{inicio}:")
    codigo_intermedio.append(f"IF {cond} == true GOTO {cuerpo}")
    codigo_intermedio.append(f"GOTO {fin}")
    codigo_intermedio.append(f"{cuerpo}: {var} = {valor}")
    codigo_intermedio.append(f"GOTO {inicio}")
    codigo_intermedio.append(f"{fin}:")

    p[0] = crear_nodo("WHILE", [f"cond: {cond}", f"{var} = {valor}"])

def p_expresion_if(p):
    'expresion : IF ID THEN ID IGUAL NUMERO PUNTOYCOMA'
    reglas_gramaticales.append("expresion → if ID then ID = NUMERO ;")
    cond = p[2]
    var = p[4]
    valor = p[6]

    # Generar etiquetas
    etiqueta_siguiente = f"L{temporales['contador']}"
    temporales['contador'] += 1

    # Validar existencia de variables
    if cond not in tabla_simbolos:
        raise Exception(f"[Error semántico] Variable condicional '{cond}' no declarada.")
    if var not in tabla_simbolos:
        raise Exception(f"[Error semántico] Variable destino '{var}' no declarada.")

    # Marcar como usada la variable condicional
    tabla_simbolos[cond]['usada'] = True
    tabla_simbolos[var]['usada'] = True

    # Generar código intermedio con salto condicional
    codigo_intermedio.append(f"IF {cond} == true GOTO {etiqueta_siguiente}")
    codigo_intermedio.append(f"GOTO END_{etiqueta_siguiente}")
    codigo_intermedio.append(f"{etiqueta_siguiente}: {var} = {valor}")
    codigo_intermedio.append(f"END_{etiqueta_siguiente}:")

    p[0] = crear_nodo("IF", [f"cond: {cond}", f"{var} = {valor}"])


def p_termino_numero(p):
    'termino : NUMERO'
    reglas_gramaticales.append("termino → NUMERO")
    p[0] = crear_nodo('NUM', [p[1]], 'int')

def p_termino_id(p):
    'termino : ID'
    reglas_gramaticales.append("termino → ID")
    
    nombre = p[1]

    # Aceptar automáticamente los temporales generados
    if nombre not in tabla_simbolos:
        if re.match(r't\d+', nombre):
            # Registrar temporal si aún no está
            tabla_simbolos[nombre] = {'tipo': 'int', 'tamaño': 4, 'usada': True}
        else:
            raise Exception(f"[Error semántico] Variable '{nombre}' no declarada.")

    tabla_simbolos[nombre]['usada'] = True
    tipo = tabla_simbolos[nombre]['tipo']
    p[0] = crear_nodo('ID', [nombre], tipo)


# CORRECCIÓN: Función de error sin asignación a p[0]
def p_error(p):
    if p:
        print(f"[Error sintáctico] Token inesperado: {p.value}")
        # Opcional: intentar recuperarse del error
        parser.errok()
    else:
        print("[Error sintáctico] Fin de entrada inesperado")

parser = yacc.yacc(start='inicio')

import re

def optimizar_codigo():
    optimizado = []
    reglas_optimizacion.clear()  # Limpiamos las anteriores

    for linea in codigo_intermedio:
        # Regla 1: Eliminación de asignaciones redundantes (ej. x = x)
        if re.match(r'(\w+)\s*=\s*\1$', linea):
            reglas_optimizacion.append("Regla 1: Eliminación de asignaciones redundantes (x = x)")
            continue

        # Regla 2: Evaluación constante (ej. t1 = 2 + 3 → t1 = 5)
        match = re.match(r'(\w+)\s*=\s*(\d+)\s*([\+\-\*/])\s*(\d+)', linea)
        if match:
            destino, op1, operador, op2 = match.groups()
            resultado = eval(f"{op1} {operador} {op2}")
            optimizado.append(f"{destino} = {resultado}")
            reglas_optimizacion.append("Regla 2: Evaluación constante")
            continue

        # Regla 3: Eliminación de suma o resta con 0 (ej. x + 0 → x)
        match = re.match(r'(\w+)\s*=\s*(\w+)\s*([\+\-])\s*0$', linea)
        if match:
            destino, var, _ = match.groups()
            optimizado.append(f"{destino} = {var}")
            reglas_optimizacion.append("Regla 3: Eliminación de suma/resta con 0")
            continue

        # Regla 4: Eliminación de multiplicación/división por 1 (ej. x * 1 → x)
        match = re.match(r'(\w+)\s*=\s*(\w+)\s*([\*/])\s*1$', linea)
        if match:
            destino, var, _ = match.groups()
            optimizado.append(f"{destino} = {var}")
            reglas_optimizacion.append("Regla 4: Eliminación de multiplicación/división por 1")
            continue

        # Si no aplica ninguna regla, dejamos la línea igual
        optimizado.append(linea)

    return optimizado

def generar_codigo_assembler(codigo_opt):
    import os
    asm = []
    asm.append("section .data")

    # Declarar variables
    for nombre, props in tabla_simbolos.items():
        if 'tipo' in props and props['tipo'] == 'int':
            asm.append(f"{nombre} dd 0")

    asm.append("\nsection .text")
    asm.append("global _start")
    asm.append("_start:")

    for linea in codigo_opt:
        if "=" in linea:
            destino, expr = map(str.strip, linea.split("="))

            if re.match(r"^\d+$", expr):
                asm.append(f"    mov eax, {expr}")
            elif re.match(r"^\w+\s*[\+\-\*/]\s*\w+$", expr):
                op1, oper, op2 = re.findall(r"(\w+)\s*([\+\-\*/])\s*(\w+)", expr)[0]
                asm.append(f"    mov eax, [{op1}]" if op1 in tabla_simbolos else f"    mov eax, {op1}")
                if oper == '+':
                    asm.append(f"    add eax, [{op2}]" if op2 in tabla_simbolos else f"    add eax, {op2}")
                elif oper == '-':
                    asm.append(f"    sub eax, [{op2}]" if op2 in tabla_simbolos else f"    sub eax, {op2}")
                elif oper == '*':
                    asm.append(f"    imul eax, [{op2}]" if op2 in tabla_simbolos else f"    imul eax, {op2}")
                elif oper == '/':
                    asm.append(f"    mov ebx, [{op2}]" if op2 in tabla_simbolos else f"    mov ebx, {op2}")
                    asm.append("    xor edx, edx")
                    asm.append("    div ebx")
            elif expr in tabla_simbolos:
                asm.append(f"    mov eax, [{expr}]")
            else:
                asm.append(f"    mov eax, {expr}")

            asm.append(f"    mov [{destino}], eax")

    # Finalización del programa
    asm.append("    mov eax, 1")
    asm.append("    int 0x80")

    # Guardar el resultado en archivo .asm
    carpeta = "ensamblador"
    os.makedirs(carpeta, exist_ok=True)

    numero = 1
    nombre_base = "codigo"
    ruta_archivo = os.path.join(carpeta, f"{nombre_base}_{numero}.asm")
    while os.path.exists(ruta_archivo):
        numero += 1
        ruta_archivo = os.path.join(carpeta, f"{nombre_base}_{numero}.asm")

    with open(ruta_archivo, "w") as f:
        f.write('\n'.join(asm))

    return '\n'.join(asm)



reglas_optimizacion_usadas = []

def optimizar_codigo():
    optimizado = []
    reglas_optimizacion_usadas.clear()
    for linea in codigo_intermedio:
        # Eliminar asignaciones redundantes
        if re.match(r'(\w+)\s*=\s*\1$', linea):
            reglas_optimizacion_usadas.append("x = x ⇒ Eliminado")
            continue

        # Evaluación constante: t1 = 2 + 3
        match = re.match(r'(\w+)\s*=\s*(\d+)\s*([\+\-\*/])\s*(\d+)', linea)
        if match:
            destino, op1, operador, op2 = match.groups()
            resultado = eval(f"{op1} {operador} {op2}")
            reglas_optimizacion_usadas.append(f"{linea} ⇒ {destino} = {resultado}")
            optimizado.append(f"{destino} = {resultado}")
            continue

        # Suma o resta con 0
        if re.match(r'(\w+)\s*=\s*(\w+)\s*([\+\-])\s*0$', linea):
            destino, var, _ = re.findall(r'(\w+)\s*=\s*(\w+)\s*([\+\-])\s*0$', linea)[0]
            reglas_optimizacion_usadas.append(f"{linea} ⇒ {destino} = {var}")
            optimizado.append(f"{destino} = {var}")
            continue

        # Resta de cero (x - 0 = x)
        if re.match(r'(\w+)\s*=\s*(\w+)\s*-\s*0$', linea):
            destino, var = re.findall(r'(\w+)\s*=\s*(\w+)\s*-\s*0$', linea)[0]
            reglas_optimizacion_usadas.append(f"{linea} ⇒ {destino} = {var}")
            optimizado.append(f"{destino} = {var}")
            continue

        # Multiplicación por 0
        if re.match(r'(\w+)\s*=\s*(\w+)\s*\*\s*0$', linea):
            destino = re.findall(r'(\w+)\s*=', linea)[0]
            reglas_optimizacion_usadas.append(f"{linea} ⇒ {destino} = 0")
            optimizado.append(f"{destino} = 0")
            continue

        # Multiplicación por 1
        if re.match(r'(\w+)\s*=\s*(\w+)\s*\*\s*1$', linea):
            destino, var = re.findall(r'(\w+)\s*=\s*(\w+)\s*\*\s*1$', linea)[0]
            reglas_optimizacion_usadas.append(f"{linea} ⇒ {destino} = {var}")
            optimizado.append(f"{destino} = {var}")
            continue

        # División entre 1
        if re.match(r'(\w+)\s*=\s*(\w+)\s*/\s*1$', linea):
            destino, var = re.findall(r'(\w+)\s*=\s*(\w+)\s*/\s*1$', linea)[0]
            reglas_optimizacion_usadas.append(f"{linea} ⇒ {destino} = {var}")
            optimizado.append(f"{destino} = {var}")
            continue

        optimizado.append(linea)
    return optimizado

