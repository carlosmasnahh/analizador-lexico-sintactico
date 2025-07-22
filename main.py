import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from analizador_lexico import lexer, tabla_simbolos
from analizador_sintactico import parser, reglas_gramaticales, codigo_intermedio
from PIL import Image, ImageTk
from graphviz import Digraph
import os

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

def mostrar_resultado(texto):
    ventana = tk.Toplevel()
    ventana.title("Resultado del análisis")
    ventana.geometry("650x550")
    area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Courier", 10))
    area.insert(tk.END, texto)
    area.config(state=tk.DISABLED)
    area.pack(expand=True, fill="both")

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

        output += "\n🧾 Código Intermedio:\n"
        for linea in codigo_intermedio:
            output += linea + "\n"

        mostrar_resultado(output)
        ruta_imagen = generar_arbol_grafico(resultado)
        mostrar_imagen(ruta_imagen)
        mostrar_tabla_simbolos()
        mostrar_reglas_gramaticales()

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

root = tk.Tk()
root.withdraw()
solicitar_codigo()
root.mainloop()
