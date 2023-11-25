---
layout: post
title:  Programación con chatgpt y la representación Gráfica de Datos Textuales con Python
date: 2023-07-21 11:23:00
description: Una prueba a la capacidad de ChatGPT para entender y aplicar indicaciones en la generación de código
tags: chatgpt automatizacion python programacion
categories: General
thumbnail: assets/img/img_2.jpg
giscus_comments: true
---
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Dependencies](https://img.shields.io/badge/Dependencies-Networkx%2C%20Asciinet%2C%20PySimpleGUI-brightgreen)
![Powered by ChatGPT](https://img.shields.io/badge/Powered%20by-ChatGPT-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)
![Project Status](https://img.shields.io/badge/Project%20Status-Completed-brightgreen)


Durante una presentación reciente utilizando Marp, me encontré con desafíos al intentar crear gráficos con Mermaid. Opté por explicar los conceptos con gráficos ASCII utilizando asciiflow, pero esta solución mostró ser ineficiente para representaciones simples y rápidas. Con el objetivo de abordar esta problemática, con los prompts correctos ChatGPT  fue capaz  de desarrollar una solución en Python utilizando las bibliotecas networkx, asciinet y PySimpleGUI.

```python

import networkx as nx
import pyperclip
from asciinet import graph_to_ascii
import PySimpleGUI as sg

# Función para generar el grafo y arte ASCII
def generar_grafo_y_ascii(texto_largo, relaciones):
    # Dividir el texto en palabras y ordenarlas
    lista_datos = texto_largo.split()

    # Convertir la cadena de texto en una lista de conexiones numeradas
    conexiones_numero = [tuple(map(int, rel.split("-"))) for rel in relaciones.split(",")]

    # Crear un grafo
    G = nx.Graph()

    # Agregar las conexiones basadas en los índices a partir de la lista de datos
    for u, v in conexiones_numero:
        G.add_edge(lista_datos[u - 1], lista_datos[v - 1])

    # Obtener el arte ASCII del grafo utilizando la función graph_to_ascii
    ascii_art = graph_to_ascii(G)

    # Diccionario de reemplazos
    reemplazos = {
        "─": "─",
        "┌": "┌",
        "└": "└",
        "┐": "┐",
        "┘": "┘"
    }

    # Aplicar los reemplazos utilizando un bucle
    for original, nuevo in reemplazos.items():
        ascii_art = ascii_art.replace(original, nuevo)

    return ascii_art

# Definir la interfaz gráfica
layout = [
    [sg.Text("Ingrese los nodos separado por espacios y las relaciones en \n guiones de posiciones separadas por comas.", justification="center")],     
    [sg.Text("Texto: ", size=(12, 1)), sg.InputText(key="texto_largo")],
    [sg.Text("Relaciones:", size=(12, 1)), sg.InputText(key="relaciones")],
    [sg.Button("Generar Grafo ASCII")],
    [sg.Multiline("", size=(60, 20), key="output", disabled=True, autoscroll=True)],
    [sg.Button("Copiar al Portapapeles"), sg.Button("Salir")]
]

# Crear la ventana
window = sg.Window("Generador de Grafo ASCII", layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Salir":
        break
    elif event == "Generar Grafo ASCII":
        texto_largo = values["texto_largo"]
        relaciones = values["relaciones"]

        try:
            ascii_art = generar_grafo_y_ascii(texto_largo, relaciones)
            window["output"].update(ascii_art)
        except Exception as e:
            sg.popup_error(f"Error: {e}")

    elif event == "Copiar al Portapapeles":
        output_text = window["output"].get()
        pyperclip.copy(output_text)

window.close()



```
**Cómo Utilizar la Herramienta:**

1. Ingresa los nodos separados por espacios, por ejemplo: "Titulo Subtitulo_A Subtitulo_B Derivado_1."
2. Define las relaciones utilizando el formato "posición-nodo" separadas por comas, por ejemplo: "1-2, 1-3, 2-4."
3. Haz clic en "Generar Grafo ASCII."

El arte ASCII generado se mostrará en el campo de salida de la interfaz y puede ser copiado al portapapeles para su uso inmediato.

**Ejemplo:**

**Texto Ingresado:**
```
Título Subtitulo_A Subtitulo_B Derivado_1 D_2
```

**Relaciones Ingresadas:**
```
1-2, 1-3, 3-4, 3-5 
```

**Resultado del Grafo ASCII:**
```
      Título
       │
┌──────┴──────┐
│               │
Subtitulo_A  Subtitulo_B
                │
         ┌─────┴─────┐
         │           │
   Derivado_1       D_2
```

**Conclusiones:**

Este proyecto destaca la eficacia de ChatGPT al traducir indicaciones específicas en soluciones de código prácticas. La herramienta desarrollada, con base en bibliotecas como networkx y PySimpleGUI en Python, resuelve de manera efectiva la representación gráfica de datos basada en texto.

La capacidad de ChatGPT para entender y aplicar indicaciones precisas ha agilizado la generación de código, ofreciendo una solución puntual. Esta colaboración directa entre la inteligencia artificial y la acción práctica subraya la utilidad de esta tecnología para abordar desafíos específicos de manera rápida y directa.
