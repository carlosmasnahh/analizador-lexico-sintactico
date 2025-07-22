import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from analizador_lexico import lexer, tabla_simbolos
from analizador_sintactico import parser, reglas_gramaticales, codigo_intermedio
from analizador_sintactico import optimizar_codigo
from PIL import Image, ImageTk
from graphviz import Digraph
import os
from analizador_sintactico import reglas_optimizacion_usadas
from analizador_sintactico import reglas_optimizacion
import re


def mostrar_reglas_optimizacion():
    ventana = tk.Toplevel()
    ventana.title("🧠 Reglas de Optimización Aplicadas")
    ventana.geometry("500x400")
    area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
    if reglas_optimizacion:
        for regla in sorted(set(reglas_optimizacion)):
            area.insert(tk.END, regla + "\n")
    else:
        area.insert(tk.END, "(ninguna aplicada)\n")
    area.config(state=tk.DISABLED)
    area.pack(expand=True, fill="both")

def imprimir_arbol(nodo, prefijo="", es_ultimo=True):
    nombre, hijos = nodo
    rama = "└── " if es_ultimo else "├── "
    resultado = prefijo + rama + str(nombre) + "\n"
    if isinstance(hijos, list):
        for i, hijo in enumerate(hijos):
            es_ultimo_hijo = (i == len(hijos) - 1)
            if isinstance(hijo, tuple):
                resultado += imprimir_arbol(hijo, prefijo + ("    " if es_ultimo else "│   "), es_ultimo_hijo)
            else:
                resultado += prefijo + ("    " if es_ultimo else "│   ")
                resultado += ("└── " if es_ultimo_hijo else "├── ") + str(hijo) + "\n"
    return resultado

def generar_arbol_grafico(nodo):
    grafo = Digraph(format='png')
    contador = [0]

    def agregar_nodo(nodo_actual):
        idx = str(contador[0])
        contador[0] += 1
        nombre, hijos = nodo_actual
        grafo.node(idx, label=nombre)
        for hijo in hijos:
            if isinstance(hijo, tuple):
                hijo_idx = agregar_nodo(hijo)
                grafo.edge(idx, hijo_idx)
            else:
                hoja_idx = str(contador[0])
                contador[0] += 1
                grafo.node(hoja_idx, label=str(hijo))
                grafo.edge(idx, hoja_idx)
        return idx

    agregar_nodo(nodo)
    carpeta = "arboles"
    os.makedirs(carpeta, exist_ok=True)
    numero = 1
    while os.path.exists(f"{carpeta}/arbol_{numero}.png"):
        numero += 1
    ruta_salida = os.path.join(carpeta, f"arbol_{numero}")
    grafo.render(ruta_salida, cleanup=True)
    return ruta_salida + ".png"

def mostrar_imagen(path):
    ventana = tk.Toplevel()
    ventana.title("Árbol de Sintaxis Gráfico")
    imagen = Image.open(path)
    ancho, alto = imagen.size
    MAX_ANCHO, MAX_ALTO = 1000, 800
    if ancho > MAX_ANCHO or alto > MAX_ALTO:
        escala = min(MAX_ANCHO / ancho, MAX_ALTO / alto)
        imagen = imagen.resize((int(ancho * escala), int(alto * escala)), Image.Resampling.LANCZOS)
    foto = ImageTk.PhotoImage(imagen)
    etiqueta = tk.Label(ventana, image=foto)
    etiqueta.image = foto
    etiqueta.pack()

def mostrar_reglas_optimizacion():
    ventana = tk.Toplevel()
    ventana.title("⚙️ Reglas de Optimización Aplicadas")
    ventana.geometry("500x400")
    area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
    if reglas_optimizacion_usadas:
        for regla in reglas_optimizacion_usadas:
            area.insert(tk.END, regla + "\n")
    else:
        area.insert(tk.END, "(ninguna)\n")
    area.config(state=tk.DISABLED)
    area.pack(expand=True, fill="both")


def mostrar_resultado(texto):
    ventana = tk.Toplevel()
    ventana.title("Resultado del análisis")
    ventana.geometry("650x550")
    area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
    area.insert(tk.END, texto)
    area.config(state=tk.DISABLED)
    area.pack(expand=True, fill="both")

import subprocess

def abrir_codigo_assembler():
    carpeta = "ensamblador"
    if not os.path.exists(carpeta):
        messagebox.showinfo("Sin archivos", "No se ha generado ningún archivo .asm aún.")
        return

    archivos = [a for a in os.listdir(carpeta) if a.endswith(".asm")]
    if not archivos:
        messagebox.showinfo("Sin archivos", "No hay archivos .asm para mostrar.")
        return

    archivos.sort()
    ruta = os.path.join(carpeta, archivos[-1])
    try:
        os.startfile(ruta)  # Solo funciona en Windows
    except:
        try:
            subprocess.Popen(["notepad", ruta])  # Alternativa
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")

def generar_codigo_assembler(codigo_intermedio):
    import re
    carpeta = "ensamblador"
    os.makedirs(carpeta, exist_ok=True)
    numero = 1
    while os.path.exists(f"{carpeta}/codigo_{numero}.asm"):
        numero += 1
    ruta_salida = os.path.join(carpeta, f"codigo_{numero}.asm")

    data_section = set()
    instrucciones = []

    for linea in codigo_intermedio:
        linea = linea.strip()

        # Etiqueta (ej. L1:)
        if re.match(r'^[A-Za-z_]\w*:$', linea):
            instrucciones.append(linea)
            continue

        # Condicional tipo: IF x > y GOTO L1
        match = re.match(r'IF (\w+)\s*([<>=!]+)\s*(\w+)\s*GOTO\s+(\w+)', linea)
        if match:
            op1, operador, op2, etiqueta = match.groups()
            data_section.update([op1, op2])
            instrucciones.append(f"mov eax, [{op1}]")
            instrucciones.append(f"cmp eax, [{op2}]")
            salto = {
                "==": "je", "!=": "jne", ">": "jg",
                "<": "jl", ">=": "jge", "<=": "jle"
            }.get(operador)
            if salto:
                instrucciones.append(f"{salto} {etiqueta}")
            continue

        # GOTO simple
        match = re.match(r'GOTO\s+(\w+)', linea)
        if match:
            instrucciones.append(f"jmp {match.group(1)}")
            continue

        # Asignación constante: x = 3
        match = re.match(r'(\w+)\s*=\s*(\d+)', linea)
        if match:
            var, val = match.groups()
            data_section.add(var)
            instrucciones.append(f"mov dword [{var}], {val}")
            continue

        # Asignación directa: x = y
        match = re.match(r'(\w+)\s*=\s*(\w+)', linea)
        if match and not re.search(r'[\+\-\*/]', linea):
            dest, src = match.groups()
            data_section.update([dest, src])
            instrucciones.append(f"mov eax, [{src}]")
            instrucciones.append(f"mov [{dest}], eax")
            continue

        # Operaciones aritméticas: x = y + z
        match = re.match(r'(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(\w+)', linea)
        if match:
            dest, op1, operador, op2 = match.groups()
            data_section.update([dest, op1, op2])
            instrucciones.append(f"mov eax, [{op1}]")
            op_map = {"+": "add", "-": "sub", "*": "imul", "/": "idiv"}
            if operador == "/":
                instrucciones.append("mov edx, 0")  # limpiar para división
                instrucciones.append(f"mov ebx, [{op2}]")
                instrucciones.append("idiv ebx")
            else:
                instrucciones.append(f"{op_map[operador]} eax, [{op2}]")
            instrucciones.append(f"mov [{dest}], eax")
            continue

        # Desconocido
        instrucciones.append(f"; No reconocido: {linea}")

    with open(ruta_salida, "w") as f:
        f.write("section .data\n")
        for var in sorted(data_section):
            f.write(f"    {var} dd 0\n")

        f.write("\nsection .text\n")
        f.write("global _start\n")
        f.write("_start:\n")
        for inst in instrucciones:
            f.write(f"    {inst}\n")

        f.write("    ; Fin del programa\n")
        f.write("    mov eax, 1\n")
        f.write("    int 0x80\n")

    return ruta_salida





def mostrar_tabla_simbolos():
    ventana = tk.Toplevel()
    ventana.title("📚 Tabla de Símbolos")
    ventana.geometry("500x400")
    area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
    if tabla_simbolos:
        for simbolo, info in tabla_simbolos.items():
            usada = info.get('usada', False)
            linea = f"{simbolo}: tipo={info['tipo']}, tamaño={info['tamaño']} bytes, usada={usada}\n"
            area.insert(tk.END, linea)
    else:
        area.insert(tk.END, "(vacía)\n")
    area.config(state=tk.DISABLED)
    area.pack(expand=True, fill="both")

def mostrar_reglas_gramaticales():
    ventana = tk.Toplevel()
    ventana.title("📖 Reglas Gramaticales Usadas")
    ventana.geometry("500x400")
    area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
    if reglas_gramaticales:
        for regla in sorted(set(reglas_gramaticales)):
            area.insert(tk.END, regla + "\n")
    else:
        area.insert(tk.END, "(ninguna)\n")
    area.config(state=tk.DISABLED)
    area.pack(expand=True, fill="both")

def analizar_entrada(codigo):
    try:
        lexer.input(codigo)
        from analizador_sintactico import temporales
        temporales['contador'] = 1
        codigo_intermedio.clear()
        reglas_gramaticales.clear()
        tabla_simbolos.clear()
        resultado = parser.parse(codigo)

        output = "\n📌 Árbol Sintáctico:\n"
        if isinstance(resultado, tuple) and resultado[0] == 'INICIO':
            for i, expr in enumerate(resultado[1]):
                output += f"\n[Expresión {i+1}]\n"
                output += imprimir_arbol(expr)
        else:
            output += imprimir_arbol(resultado)

        output += "\n📚 Tabla de Símbolos:\n"
        if tabla_simbolos:
            for simbolo, info in tabla_simbolos.items():
                usada = info.get('usada', False)
                output += f"{simbolo}: tipo={info['tipo']}, tamaño={info['tamaño']} bytes, usada={usada}\n"
        else:
            output += "(vacía)\n"

        output += "\n📖 Reglas Gramaticales Usadas:\n"
        for regla in set(reglas_gramaticales):
            output += f"{regla}\n"

        codigo_opt = optimizar_codigo()

        output += "\n🧾 Código Intermedio:\n"
        for linea in codigo_intermedio:
            output += linea + "\n"

        output += "\n🛠️ Código Intermedio Optimizado:\n"
        for linea in codigo_opt:
            output += linea + "\n"

        output += "\n⚙️ Código Assembler:\n"
        codigo_asm = generar_codigo_assembler(codigo_opt)
        output += codigo_asm

        # Mostrar mensaje con ruta del archivo .asm
        import os
        ultima_ruta = ""
        for raiz, _, archivos in os.walk("ensamblador"):
            archivos_asm = [a for a in archivos if a.endswith(".asm")]
            if archivos_asm:
                ultima_ruta = os.path.join(raiz, sorted(archivos_asm)[-1])
                break

        if ultima_ruta:
            messagebox.showinfo("Archivo ASM generado", f"El código assembler fue guardado en:\n{ultima_ruta}")

        mostrar_resultado(output)
        ruta_imagen = generar_arbol_grafico(resultado)
        mostrar_imagen(ruta_imagen)
        mostrar_tabla_simbolos()
        mostrar_reglas_gramaticales()
        mostrar_reglas_optimizacion()
        
    except Exception as e:
        messagebox.showerror("Error de análisis", str(e))

def solicitar_codigo():
    ventana = tk.Toplevel()
    ventana.title("Entrada de código")

    etiqueta = tk.Label(ventana, text="Introduce el código a analizar (soporta varias líneas):")
    etiqueta.pack(pady=5)

    entrada = tk.Text(ventana, height=10, width=60, font=("Courier", 11))
    entrada.pack(padx=10, pady=5)

    def analizar_y_cerrar():
        codigo = entrada.get("1.0", tk.END).strip()
        if codigo:
            analizar_entrada(codigo)
        else:
            messagebox.showinfo("Información", "No se ingresó ningún código.")
        ventana.destroy()

    boton = tk.Button(ventana, text="Analizar", command=analizar_y_cerrar)
    boton.pack(pady=10)

def mostrar_ultimo_codigo_asm():
    carpeta = "ensamblador"
    if not os.path.exists(carpeta):
        messagebox.showinfo("Sin archivos", "No se ha generado ningún archivo .asm aún.")
        return

    archivos = [a for a in os.listdir(carpeta) if a.endswith(".asm")]
    if not archivos:
        messagebox.showinfo("Sin archivos", "No hay archivos .asm para mostrar.")
        return

    archivos.sort()
    ruta = os.path.join(carpeta, archivos[-1])
    try:
        with open(ruta, "r") as f:
            contenido = f.read()

        ventana = tk.Toplevel()
        ventana.title(f"Código Assembler: {archivos[-1]}")
        ventana.geometry("600x500")
        area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
        area.insert(tk.END, contenido)
        area.config(state=tk.DISABLED)
        area.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")

def mostrar_menu_principal():
    ventana = tk.Toplevel()
    ventana.title("Menú Principal")
    ventana.geometry("300x250")

    btn_analizar = tk.Button(ventana, text="🔍 Analizar Código", command=solicitar_codigo)
    btn_analizar.pack(pady=10)

    btn_abrir_asm = tk.Button(ventana, text="⚙️ Ver Código Assembler (Notepad)", command=abrir_codigo_assembler)
    btn_abrir_asm.pack(pady=10)

    btn_ver_asm_ventana = tk.Button(ventana, text="📄 Ver Código Assembler en ventana", command=mostrar_ultimo_codigo_asm)
    btn_ver_asm_ventana.pack(pady=10)

root = tk.Tk()
root.withdraw()
mostrar_menu_principal()
root.mainloop()
