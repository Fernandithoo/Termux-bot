# termux_teacher_bot.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, User, Chat
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import subprocess # Mantenido por si se usará más adelante, aunque no se usa en este código final
import json
import os

# --- 1. Configuración de Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# --- 2. Configuración Esencial del Bot ---
# ¡IMPORTANTE! Reemplaza esto con el token que te dio BotFather.
TOKEN = "7888884418:AAGSk56nOMOL-iKeVj-zF3fdvkBGeMK6ixE" # <--- ¡PON TU TOKEN AQUÍ!

# ¡IMPORTANT E! Reemplaza esto con tu ID de usuario de Telegram (es un número largo).
ADMIN_USER_ID = 7932344067 # <--- ¡PON TU ID DE USUARIO DE TELEGRAM AQUÍ!

# Tu nombre de usuario de Telegram (ej. @tu_usuario).
ADMIN_USERNAME = "@LUIISSS123" # <--- ¡PON TU @USERNAME DE TELEGRAM AQUÍ!
# termux_teacher_bot.py (Continuación)

# --- 3. Archivo para Guardar Datos Persistentes ---
DATA_FILE = 'bot_data.json'

# --- 4. Contenido del Bot ---
BAD_WORDS = ['groseria1', 'groseria2', 'malo', 'idiota', 'estúpido', 'mierda', 'puto', 'verga', 'cabron', 'joder']

TERMUX_COMMANDS = {
    "ls": "El comando `ls` (list) te muestra los archivos y directorios en tu ubicación actual de Termux. Es como ver el contenido de una carpeta. \nEjemplo: `ls -l` (para ver detalles).",
    "cd": "El comando `cd` (change directory) te permite moverte entre directorios. \nEjemplo: `cd storage/shared` (para ir a tu almacenamiento compartido) o `cd ..` (para subir un nivel).",
    "pwd": "El comando `pwd` (print working directory) te dice en qué directorio de Termux te encuentras actualmente. ¡Útil para no perderse!",
    "pkg": "El comando `pkg` es el gestor de paquetes de Termux, similar a `apt` en Debian. Lo usas para instalar, actualizar o eliminar software. \nEjemplo: `pkg install python` (para instalar Python).",
    "nano": "El comando `nano` es un editor de texto simple y fácil de usar directamente en la terminal de Termux. Es perfecto para escribir tus scripts. \nEjemplo: `nano mi_script.py`.",
    "python": "El comando `python` se usa para ejecutar scripts de Python. \nEjemplo: `python mi_programa.py`.",
    "pip": "El comando `pip` es el gestor de paquetes de Python. Lo usas para instalar librerías de Python. \nEjemplo: `pip install requests`.",
    "cat": "El comando `cat` (concatenate) se usa para mostrar el contenido de uno o varios archivos directamente en la terminal.",
    "rm": "El comando `rm` (remove) se utiliza para eliminar archivos y directorios. ¡Úsalo con cuidado, ya que no hay papelera de reciclaje en la terminal! \nEjemplo: `rm archivo.txt`.",
    "mkdir": "El comando `mkdir` (make directory) crea un nuevo directorio (carpeta). \nEjemplo: `mkdir mis_proyectos`.",
    "mv": "El comando `mv` (move) se usa para mover o renombrar archivos y directorios. \nEjemplo: `mv archivo_viejo.txt archivo_nuevo.txt` o `mv archivo.txt /ruta/a/otro/directorio`.",
    "cp": "El comando `cp` (copy) copia archivos y directorios. \nEjemplo: `cp original.txt copia.txt`.",
    "top": "El comando `top` muestra los procesos en ejecución y su uso de recursos del sistema en tiempo real. Para salir, presiona `q`.",
    "df": "El comando `df` (disk free) muestra el espacio libre en disco en tu sistema de archivos.",
    "du": "El comando `du` (disk usage) estima el espacio en disco usado por archivos y directorios. \nEjemplo: `du -h mi_carpeta` (para ver en formato legible)."
}

PYTHON_LESSONS = [
    {
        "title": "Lección 1: ¡Hola Mundo! y Variables",
        "content": "La primera lección de Python siempre es el 'Hola Mundo'. Aprenderemos a imprimir texto en la consola y a guardar información en variables.\n\n"
                   "**Imprimir texto:**\n"
                   "```python\nprint('¡Hola, Python!')\n```\n\n"
                   "**Variables:** Son como cajas para guardar datos.\n"
                   "```python\nx = 10\nnombre = 'Alice'\n```"
    },
    {
        "title": "Lección 2: Tipos de Datos Básicos",
        "content": "Python maneja varios tipos de datos:\n"
                   "- **Enteros (`int`):** Números sin decimales (ej. `5`, `-3`).\n"
                   "- **Flotantes (`float`):** Números con decimales (ej. `3.14`, `-0.5`).\n"
                   "- **Cadenas de texto (`str`):** Texto entre comillas (ej. `'Hola'`, `\"Mundo\"`).\n"
                   "- **Booleanos (`bool`):** `True` o `False`."
    },
    {
        "title": "Lección 3: Operadores Aritméticos",
        "content": "Aprende a realizar operaciones matemáticas básicas:\n"
                   "- **Suma:** `+`\n"
                   "- **Resta:** `-`\n"
                   "- **Multiplicación:** `*`\n"
                   "- **División:** `/` (siempre devuelve un `float`)\n"
                   "- **División entera:** `//`\n"
                   "- **Módulo (residuo):** `%`\n"
                   "- **Potencia:** `**`"
    },
    {
        "title": "Lección 4: Cadenas de Texto (Strings)",
        "content": "Los strings son secuencias de caracteres. Puedes:\n"
                   "- **Concatenar:** `nombre + ' ' + apellido`\n"
                   "- **Multiplicar:** `'abc' * 3` (`'abcabcabc'`)\n"
                   "- **Acceder a caracteres:** `texto[0]`\n"
                   "- **Cortar (Slicing):** `texto[1:4]`\n"
                   "- **Métodos útiles:** `.upper()`, `.lower()`, `.strip()`, `.replace()`."
    },
    {
        "title": "Lección 5: Listas (Arrays)",
        "content": "Las **listas** son colecciones ordenadas y mutables de ítems. Pueden contener diferentes tipos de datos.\n\n"
                   "**Crear lista:** `mi_lista = [1, 'hola', True]`\n"
                   "**Acceder:** `mi_lista[0]`\n"
                   "**Añadir:** `mi_lista.append('nuevo')`\n"
                   "**Modificar:** `mi_lista[0] = 5`\n"
                   "**Eliminar:** `mi_lista.remove('hola')`"
    },
    {
        "title": "Lección 6: Tuplas",
        "content": "Las **tuplas** son colecciones ordenadas e **inmutables** (no se pueden cambiar una vez creadas). Son útiles para datos que no deben modificarse.\n\n"
                   "**Crear tupla:** `mi_tupla = (1, 'dos', 3)`\n"
                   "**Acceder:** `mi_tupla[0]`\n"
                   "**Desempaquetar:** `a, b, c = mi_tupla`"
    },
    {
        "title": "Lección 7: Diccionarios",
        "content": "Los **diccionarios** son colecciones no ordenadas de pares `clave: valor`. Las claves deben ser únicas e inmutables.\n\n"
                   "**Crear diccionario:** `persona = {'nombre': 'Ana', 'edad': 30}`\n"
                   "**Acceder:** `persona['nombre']`\n"
                   "**Añadir/Modificar:** `persona['ciudad'] = 'Madrid'`\n"
                   "**Eliminar:** `del persona['edad']`"
    },
    {
        "title": "Lección 8: Conjuntos (Sets)",
        "content": "Los **conjuntos** son colecciones no ordenadas de ítems únicos. Son útiles para eliminar duplicados y realizar operaciones matemáticas de conjuntos (unión, intersección).\n\n"
                   "**Crear conjunto:** `mi_set = {1, 2, 3, 2}` (resultado: `{1, 2, 3}`)\n"
                   "**Añadir:** `mi_set.add(4)`\n"
                   "**Eliminar:** `mi_set.remove(1)`"
    },
    {
        "title": "Lección 9: Condicionales (if/elif/else)",
        "content": "Permiten que tu programa tome decisiones. El código se ejecuta solo si una condición es `True`.\n\n"
                   "```python\nif edad >= 18:\n    print('Adulto')\nelif edad >= 13:\n    print('Adolescente')\nelse:\n    print('Niño')\n```"
    },
    {
        "title": "Lección 10: Bucles `for`",
        "content": "Iteran sobre una secuencia (lista, tupla, string, rango) un número determinado de veces.\n\n"
                    "```python\nfrutas = ['manzana', 'banana', 'cereza']\nfor fruta in frutas:\n    print(fruta)\n\nfor i in range(5):\n    print(i) # 0, 1, 2, 3, 4\n```"
    },
    {
        "title": "Lección 11: Bucles `while`",
        "content": "Repiten un bloque de código mientras una condición sea `True`.\n\n"
                   "```python\ncontador = 0\nwhile contador < 3:\n    print(contador)\n    contador += 1\n```"
    },
    {
        "title": "Lección 12: Funciones",
        "content": "Bloques de código reutilizables. Ayudan a organizar el código y evitar la repetición.\n\n"
                   "```python\ndef saludar(nombre):\n    return f'Hola, {nombre}!'\n\nmensaje = saludar('Carlos')\nprint(mensaje)\n```"
    },
    {
        "title": "Lección 13: Argumentos de Funciones",
        "content": "Las funciones pueden aceptar argumentos por posición, por palabra clave, y un número variable de argumentos (`*args`, `**kwargs`).\n\n"
                   "```python\ndef sumar(a, b):\n    return a + b\n\ndef mostrar_info(nombre, edad=30):\n    print(f'{nombre} tiene {edad} años.')\n```"
    },
    {
        "title": "Lección 14: Alcance de Variables (Scope)",
        "content": "El alcance define dónde una variable es accesible. Las variables pueden ser locales (dentro de una función) o globales (fuera de funciones)."
                   "```python\nglobal_var = 10\n\ndef my_func():\n    local_var = 5\n    print(global_var) # Accede a global\n\nmy_func()\n# print(local_var) # Error: local_var no accesible aquí\n```"
    },
    {
        "title": "Lección 15: Manejo de Errores (try/except)",
        "content": "Permite que tu programa maneje errores (excepciones) elegantemente sin detenerse.\n\n"
                   "```python\ntry:\n    resultado = 10 / 0\nexcept ZeroDivisionError:\n    print('No se puede dividir por cero.')\nexcept ValueError:\n    print('Error de valor.')\n```"
    },
    {
        "title": "Lección 16: Archivos (Lectura y Escritura)",
        "content": "Cómo abrir, leer y escribir en archivos. Siempre usa `with open(...)` para asegurar que el archivo se cierre correctamente.\n\n"
                   "```python\n# Escritura\nwith open('mi_archivo.txt', 'w') as f:\n    f.write('Hola mundo!')\n\n# Lectura\nwith open('mi_archivo.txt', 'r') as f:\n    contenido = f.read()\n    print(contenido)\n```"
    },
    {
        "title": "Lección 17: Módulos y Paquetes",
        "content": "Un **módulo** es un archivo `.py` que contiene código Python. Un **paquete** es un directorio con módulos y un archivo `__init__.py`.\n\n"
                   "**Importar:** `import math`, `from datetime import date`"
    },
    {
        "title": "Lección 18: Programación Orientada a Objetos (Clases y Objetos)",
        "content": "Python es un lenguaje orientado a objetos. Una **clase** es un 'plano' para crear **objetos**.\n\n"
                   "```python\nclass Perro:\n    def __init__(self, nombre):\n        self.nombre = nombre\n    def ladrar(self):\n        print(f'{self.nombre} dice Woof!')\n\nmi_perro = Perro('Fido')\nmi_perro.ladrar()\n```"
    },
    {
        "title": "Lección 19: Herencia",
        "content": "Permite que una clase (clase hija) herede atributos y métodos de otra clase (clase padre), promoviendo la reutilización de código.\n\n"
                   "```python\nclass Animal:\n    def __init__(self, especie):\n        self.especie = especie\n    def moverse(self):\n        pass\n\nclass Perro(Animal):\n    def __init__(self, nombre):\n        super().__init__('Canino')\n        self.nombre = nombre\n    def ladrar(self):\n        print('Woof!')\n```"
    },
    {
        "title": "Lección 20: Polimorfismo",
        "content": "Significa 'muchas formas'. En POO, se refiere a la capacidad de diferentes objetos de responder al mismo método de maneras diferentes. Es común verlo con la sobreescritura de métodos (method overriding)."
    }
]

PYTHON_QUIZ_QUESTIONS = [
    {
        "question": "¿Qué función se usa para imprimir mensajes en la consola en Python?",
        "options": ["display()", "show()", "print()", "output()"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cuál de los siguientes es un tipo de dato entero (integer) en Python?",
        "options": ["3.14", "'hello'", "10", "True"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué operador se usa para la división entera en Python?",
        "options": ["/", "//", "%", "**"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cómo se define una cadena de texto (string) en Python?",
        "options": ["sin comillas", "con comillas simples o dobles", "con corchetes", "con paréntesis"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cuál es la forma correcta de crear una lista en Python?",
        "options": ["lista = (1, 2, 3)", "lista = {1, 2, 3}", "lista = [1, 2, 3]", "lista = <1, 2, 3>"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué significa que una tupla sea 'inmutable'?",
        "options": ["Que no se puede ordenar", "Que no se pueden añadir o eliminar elementos después de su creación", "Que solo contiene números", "Que sus elementos deben ser del mismo tipo"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué tipo de estructura de datos usa 'clave: valor'?",
        "options": ["Lista", "Tupla", "Conjunto", "Diccionario"],
        "correct_option_index": 3
    },
    {
        "question": "¿Qué palabra clave se usa para una condición 'si no' en Python?",
        "options": ["else if", "elseif", "elif", "otherwise"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué bucle se usa para iterar sobre una secuencia de elementos?",
        "options": ["while", "do-while", "loop", "for"],
        "correct_option_index": 3
    },
    {
        "question": "¿Qué se usa para definir un bloque de código reutilizable en Python?",
        "options": ["loop", "function", "module", "class"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué error ocurre al intentar dividir un número por cero?",
        "options": ["TypeError", "NameError", "ZeroDivisionError", "ValueError"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué modo de apertura de archivo usarías para escribir y sobrescribir un archivo existente?",
        "options": ["'r'", "'a'", "'w'", "'x'"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cómo se importa el módulo 'math' en Python?",
        "options": ["import math", "get math", "use math", "load math"],
        "correct_option_index": 0
    },
    {
        "question": "¿Qué es una 'clase' en Programación Orientada a Objetos?",
        "options": ["Una función especial", "Un tipo de dato inmutable", "Un plano para crear objetos", "Una variable global"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué concepto de POO permite que una clase hija herede de una clase padre?",
        "options": ["Polimorfismo", "Encapsulamiento", "Herencia", "Abstracción"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cuál es el operador para la multiplicación en Python?",
        "options": ["x", "*", "#", "$"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué valor devuelve `type(10)` en Python?",
        "options": ["<class 'float'>", "<class 'str'>", "<class 'int'>", "<class 'bool'>"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué hace el método `.append()` en una lista?",
        "options": ["Elimina el último elemento", "Añade un elemento al final", "Ordena la lista", "Invierte la lista"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cuál de estas no es una colección de datos en Python?",
        "options": ["Lista", "Diccionario", "Función", "Conjunto"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué hace el operador `%` (módulo) en Python?",
        "options": ["Calcula la potencia", "Devuelve el cociente de la división", "Devuelve el residuo de la división", "Devuelve el valor absoluto"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué palabra clave se utiliza para definir una función en Python?",
        "options": ["func", "define", "def", "function"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cuál es el propósito de `try` y `except` en Python?",
        "options": ["Definir clases y objetos", "Manejar errores", "Crear bucles", "Importar módulos"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué se utiliza para hacer comentarios de una sola línea en Python?",
        "options": ["//", "/* */", "#", "--"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cuál de las siguientes es una forma correcta de un comentario multilínea en Python?",
        "options": ["# Esto es un comentario", "'''Esto es un comentario'''", "// Esto es un comentario", ""],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué método se usa para eliminar el último elemento de una lista?",
        "options": ["remove()", "delete()", "pop()", "clear()"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué tipo de dato representa verdadero/falso?",
        "options": ["int", "float", "bool", "str"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué es una variable global?",
        "options": ["Una variable definida dentro de una función", "Una variable accesible en todo el programa", "Una variable que solo contiene texto", "Una variable que no puede cambiar su valor"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cuál es la sintaxis correcta para un bucle `while`?",
        "options": ["while (condicion):", "while condicion;", "while condicion do:", "while condicion {"],
        "correct_option_index": 0
    },
    {
        "question": "¿Qué operador se usa para la potencia en Python?",
        "options": ["^", "**", "pow()", "exp()"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué hace el método `.lower()` en un string?",
        "options": ["Convierte a mayúsculas", "Invierte el string", "Convierte a minúsculas", "Elimina espacios"],
        "correct_option_index": 2
    },
    {
        "question": "¿Qué significa `\n` en un string?",
        "options": ["Espacio", "Tabulación", "Nueva línea", "Retorno de carro"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cómo se convierte un número a string en Python?",
        "options": ["int_to_str()", "str()", "to_string()", "convert_str()"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué se usa para iterar un número específico de veces en un bucle `for`?",
        "options": ["range()", "loop()", "iterate()", "count()"],
        "correct_option_index": 0
    },
    {
        "question": "¿Cuál de los siguientes NO es un tipo de dato numérico en Python?",
        "options": ["int", "float", "complex", "char"],
        "correct_option_index": 3
    },
    {
        "question": "¿Qué método se usa para añadir un elemento a un conjunto (set)?",
        "options": ["append()", "add()", "insert()", "push()"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cuál es la salida de `print(5 == 5)`?",
        "options": ["False", "True", "5", "Error"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué operador se usa para comprobar igualdad en valor Y tipo?",
        "options": ["==", "=", "===", "!="],
        "correct_option_index": 0
    },
    {
        "question": "¿Qué hace el método `.strip()` en un string?",
        "options": ["Elimina espacios al principio y al final", "Convierte a mayúsculas", "Invierte el string", "Busca un substring"],
        "correct_option_index": 0
    },
    {
        "question": "¿Qué significa 'POO' en Python?",
        "options": ["Programación Orientada a Operaciones", "Programación Orientada a Objetos", "Procesos Orientados a Operaciones", "Puntos de Operación Oficiales"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cuál es el archivo especial que indica que un directorio es un paquete Python?",
        "options": ["__main__.py", "__init__.py", "package.py", "module.py"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué palabra clave se usa para crear una instancia de una clase?",
        "options": ["new", "create", "instantiate", "Ninguna, se crea directamente con el nombre de la clase"],
        "correct_option_index": 3
    },
    {
        "question": "¿Qué método especial se usa para inicializar un objeto de una clase?",
        "options": ["start()", "init()", "__init__()", "create()"],
        "correct_option_index": 2
    },
    {
        "question": "¿Cuál es el propósito del `self` en los métodos de una clase?",
        "options": ["Se refiere al nombre de la clase", "Se refiere a la instancia actual del objeto", "Es una palabra clave reservada para herencia", "Define una variable global"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué hace el operador `in`?",
        "options": ["Suma dos números", "Verifica si un elemento está en una secuencia", "Comprueba si dos valores son iguales", "Multiplica dos números"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué estructura se usa para almacenar elementos desordenados y sin duplicados?",
        "options": ["Lista", "Tupla", "Diccionario", "Conjunto (Set)"],
        "correct_option_index": 3
    },
    {
        "question": "¿Qué hace el método `.pop()` en una lista si no se le da un índice?",
        "options": ["Elimina el primer elemento", "Elimina el último elemento", "Elimina un elemento aleatorio", "No hace nada"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué se usa para leer una línea de un archivo?",
        "options": ["read()", "readline()", "readlines()", "get_line()"],
        "correct_option_index": 1
    },
    {
        "question": "¿Cuál es la extensión de un archivo de módulo Python?",
        "options": [".txt", ".py", ".exe", ".doc"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué es un 'objeto' en POO?",
        "options": ["Un tipo de variable", "Una instancia de una clase", "Una función", "Un módulo"],
        "correct_option_index": 1
    },
    {
        "question": "¿Qué palabra clave se usa para salir de un bucle?",
        "options": ["exit", "stop", "break", "continue"],
        "correct_option_index": 2
    }
]
# termux_teacher_bot.py (Continuación)

# --- 5. Funciones para la Gestión de Datos (Strikes y Bloqueos) ---
bot_data = {
    'strikes': {},  # {user_id (str): count}
    'blocked_users': [], # [user_id (int), user_id (int), ...]
    'quiz_state': {}, # {user_id: {'question_index': int, 'score': int}}
    'lesson_state': {} # {user_id: {'current_lesson_index': int}}
}

def load_data():
    """Carga los datos del bot desde el archivo JSON."""
    global bot_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                loaded_data = json.load(f)
                # Actualizar bot_data con los datos cargados, manteniendo los valores por defecto si no existen
                bot_data['strikes'] = loaded_data.get('strikes', {})
                bot_data['blocked_users'] = loaded_data.get('blocked_users', [])
                bot_data['quiz_state'] = loaded_data.get('quiz_state', {})
                bot_data['lesson_state'] = loaded_data.get('lesson_state', {})

            logger.info(f"Datos cargados desde {DATA_FILE}")
            # Asegurarse de que los user_id en blocked_users sean int
            bot_data['blocked_users'] = [int(uid) for uid in bot_data['blocked_users']]
            # Asegurarse de que las keys de strikes sean str
            bot_data['strikes'] = {str(k): v for k, v in bot_data['strikes'].items()}
            # Asegurarse de que las keys de quiz_state y lesson_state sean str
            bot_data['quiz_state'] = {str(k): v for k, v in bot_data['quiz_state'].items()}
            bot_data['lesson_state'] = {str(k): v for k, v in bot_data['lesson_state'].items()}

        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON desde {DATA_FILE}: {e}. Se inicializarán datos vacíos.")
            bot_data = {'strikes': {}, 'blocked_users': [], 'quiz_state': {}, 'lesson_state': {}}
    else:
        logger.info(f"Archivo de datos {DATA_FILE} no encontrado. Se creará uno nuevo.")

def save_data():
    """Guarda los datos del bot en el archivo JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(bot_data, f, indent=4)
    logger.info(f"Datos guardados en {DATA_FILE}")

def add_strike(user_id: int):
    """Añade un strike a un usuario."""
    user_id_str = str(user_id)
    bot_data['strikes'][user_id_str] = bot_data['strikes'].get(user_id_str, 0) + 1
    save_data()
    return bot_data['strikes'][user_id_str]

def clear_strikes(user_id: int):
    """Borra los strikes de un usuario."""
    user_id_str = str(user_id)
    if user_id_str in bot_data['strikes']:
        del bot_data['strikes'][user_id_str]
        save_data()

def block_user(user_id: int):
    """Bloquea a un usuario."""
    if user_id not in bot_data['blocked_users']:
        bot_data['blocked_users'].append(user_id)
        save_data()

def unblock_user(user_id: int):
    """Desbloquea a un usuario."""
    if user_id in bot_data['blocked_users']:
        bot_data['blocked_users'].remove(user_id)
        save_data()

def is_user_blocked(user_id: int) -> bool:
    """Verifica si un usuario está bloqueado."""
    return user_id in bot_data['blocked_users']

# Cargar datos al iniciar el bot
load_data()
# termux_teacher_bot.py (Continuación)

# --- 6. Funciones para Generar Teclados Inline ---

def get_main_menu_keyboard():
    """Crea y devuelve el teclado de botones inline para el menú principal."""
    keyboard = [
        [
            InlineKeyboardButton("📚 Lecciones de Python", callback_data="mostrar_lecciones"),
            InlineKeyboardButton("🧠 Quiz de Python", callback_data="ir_al_quiz"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Comandos Termux", callback_data="mostrar_comandos_termux"),
            InlineKeyboardButton("❓ Ayuda del Bot", callback_data="ayuda_bot"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_termux_commands_keyboard():
    """Crea y devuelve el teclado de botones inline con los comandos de Termux."""
    keyboard = []
    commands_list = sorted(list(TERMUX_COMMANDS.keys()))
    for i in range(0, len(commands_list), 2):
        row = []
        for cmd_name in commands_list[i:i+2]:
            row.append(InlineKeyboardButton(cmd_name, callback_data=f"termux_cmd_{cmd_name}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Menú Principal", callback_data="volver_main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu_keyboard():
    """Crea y devuelve el teclado de botones inline para el menú de administración."""
    keyboard = [
        [
            InlineKeyboardButton("🚫 Bloquear Usuario", callback_data="admin_block_user"),
            InlineKeyboardButton("✅ Desbloquear Usuario", callback_data="admin_unblock_user"),
        ],
        [
            InlineKeyboardButton("📊 Ver Strikes", callback_data="admin_view_strikes"),
            InlineKeyboardButton("🧹 Limpiar Strikes", callback_data="admin_clear_strikes"),
        ],
        [
            InlineKeyboardButton("📋 Listar Bloqueados", callback_data="admin_list_blocked"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- NUEVA FUNCIÓN ---
def get_lesson_navigation_keyboard(current_index: int):
    """Crea el teclado para navegar entre lecciones."""
    keyboard = []
    nav_row = []

    if current_index > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"lesson_prev_{current_index - 1}"))
    
    # Agrega el contador de lecciones
    nav_row.append(InlineKeyboardButton(f"{current_index + 1}/{len(PYTHON_LESSONS)}", callback_data="ignore"))

    if current_index < len(PYTHON_LESSONS) - 1:
        nav_row.append(InlineKeyboardButton("Siguiente ➡️", callback_data=f"lesson_next_{current_index + 1}"))
    
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("🏡 Menú Principal", callback_data="volver_main_menu")])
    return InlineKeyboardMarkup(keyboard)

# --- NUEVA FUNCIÓN ---
def get_quiz_options_keyboard(options: list, question_index: int):
    """Crea el teclado de botones inline con las opciones de una pregunta del quiz."""
    keyboard = []
    for i, option in enumerate(options):
        # 'quiz_ans_<index_pregunta>_<index_opcion_elegida>'
        keyboard.append([InlineKeyboardButton(option, callback_data=f"quiz_ans_{question_index}_{i}")])
    return InlineKeyboardMarkup(keyboard)
# termux_teacher_bot.py (Continuación)

# --- 7. Lógica de Moderación y Verificación de Usuarios ---

async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Verifica si el usuario está bloqueado.
    Si está bloqueado, envía un mensaje de aviso y retorna True.
    Retorna False si el usuario no está bloqueado.
    """
    user_id = update.effective_user.id
    if is_user_blocked(user_id):
        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"🚫 Has sido bloqueado por el administrador {ADMIN_USERNAME}. "
                "Si crees que es un error, contacta con él."
            )
        elif update.message:
            await update.message.reply_text(
                f"🚫 Has sido bloqueado por el administrador {ADMIN_USERNAME}. "
                "Si crees que es un error, contacta con él."
            )
        return True
    return False

async def handle_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja mensajes que contienen palabras prohibidas.
    Añade strikes al usuario y lo bloquea si acumula demasiados.
    """
    if await check_user_status(update, context): 
        return
    
    message_text = update.message.text.lower()
    user_id = update.effective_user.id
    user_mention = update.effective_user.mention_html()

    for bad_word in BAD_WORDS:
        if bad_word in message_text:
            strike_count = add_strike(user_id)
            if strike_count >= 3:
                block_user(user_id)
                await update.message.reply_html(
                    f"{user_mention}, ¡atención! Has usado una palabra prohibida de nuevo. "
                    f"Acumulas {strike_count} strikes. Has sido **BLOQUEADO** del bot. "
                    f"Contacta a {ADMIN_USERNAME} si crees que es un error."
                )
                logger.warning(f"Usuario {user_id} ({update.effective_user.full_name}) ha sido BLOQUEADO por usar palabras prohibidas.")
            else:
                await update.message.reply_html(
                    f"{user_mention}, ¡cuidado con el lenguaje! Esa palabra está prohibida. "
                    f"Acumulas {strike_count} strikes. Al llegar a 3 strikes, serás bloqueado."
                )
                logger.info(f"Usuario {user_id} ({update.effective_user.full_name}) recibió strike {strike_count} por palabra prohibida.")
            try:
                await update.message.delete()
            except Exception as e:
                logger.error(f"No se pudo borrar el mensaje del usuario {user_id}: {e}")
            return
# termux_teacher_bot.py (Continuación)

# --- 8. Handlers de Comandos Básicos de Usuario ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía el mensaje de bienvenida con el menú principal de botones inline."""
    if await check_user_status(update, context): return

    reply_markup = get_main_menu_keyboard()
    await update.message.reply_text(
        "¡Hola! Soy tu bot asistente para aprender Python y Termux. ¿Qué te gustaría hacer hoy?",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía el menú principal con botones inline cuando se usa /help."""
    if await check_user_status(update, context): return

    reply_markup = get_main_menu_keyboard()
    await update.message.reply_text(
        "Aquí tienes las opciones principales del bot:",
        reply_markup=reply_markup
    )
# termux_teacher_bot.py (Continuación)

# --- NUEVA SECCIÓN: Lógica para Lecciones de Python ---

async def show_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE, lesson_index: int) -> None:
    """Muestra una lección de Python específica."""
    user_id_str = str(update.effective_user.id)
    if not 0 <= lesson_index < len(PYTHON_LESSONS):
        await update.callback_query.edit_message_text(
            "Lo siento, esa lección no existe o no está disponible."
        )
        # Asegurarse de que el estado de la lección sea válido si se corrompe.
        bot_data['lesson_state'][user_id_str] = {'current_lesson_index': 0}
        save_data()
        return

    lesson = PYTHON_LESSONS[lesson_index]
    lesson_text = f"**{lesson['title']}**\n\n{lesson['content']}"
    
    reply_markup = get_lesson_navigation_keyboard(lesson_index)
    
    # Actualizar el estado de la lección del usuario
    bot_data['lesson_state'][user_id_str] = {'current_lesson_index': lesson_index}
    save_data()

    await update.callback_query.edit_message_text(
        text=lesson_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
# termux_teacher_bot.py (Continuación)

# --- NUEVA SECCIÓN: Lógica para el Quiz de Python ---

import random # Necesario para barajar las preguntas

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inicia un nuevo quiz de Python para el usuario."""
    user_id_str = str(update.effective_user.id)

    # Reiniciar el estado del quiz para el usuario
    bot_data['quiz_state'][user_id_str] = {
        'question_index': 0,
        'score': 0,
        'questions_order': random.sample(range(len(PYTHON_QUIZ_QUESTIONS)), len(PYTHON_QUIZ_QUESTIONS)) # Barajar las preguntas
    }
    save_data()
    
    await send_quiz_question(update, context, user_id_str)

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_str: str) -> None:
    """Envía la pregunta actual del quiz al usuario."""
    quiz_state = bot_data['quiz_state'].get(user_id_str)
    
    if not quiz_state or quiz_state['question_index'] >= len(PYTHON_QUIZ_QUESTIONS):
        await finish_quiz(update, context, user_id_str)
        return

    current_q_index_in_order = quiz_state['questions_order'][quiz_state['question_index']]
    question_data = PYTHON_QUIZ_QUESTIONS[current_q_index_in_order]
    
    question_text = f"**Pregunta {quiz_state['question_index'] + 1}/{len(PYTHON_QUIZ_QUESTIONS)}:**\n\n{question_data['question']}"
    reply_markup = get_quiz_options_keyboard(question_data['options'], current_q_index_in_order) # Usar el índice original para el callback

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=question_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        # Esto podría usarse si el quiz se iniciara con un comando, no solo con un botón
        await update.message.reply_text(
            text=question_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def check_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verifica la respuesta del usuario a una pregunta del quiz."""
    query = update.callback_query
    await query.answer()

    user_id_str = str(update.effective_user.id)
    quiz_state = bot_data['quiz_state'].get(user_id_str)

    if not quiz_state: # Si el quiz no está en curso
        await query.edit_message_text("El quiz no está en curso. Pulsa '🧠 Quiz de Python' para empezar uno nuevo.",
                                      reply_markup=get_main_menu_keyboard())
        return
    
    # query.data es como 'quiz_ans_<question_original_index>_<selected_option_index>'
    parts = query.data.split('_')
    original_q_index = int(parts[2])
    selected_option_index = int(parts[3])

    question_data = PYTHON_QUIZ_QUESTIONS[original_q_index]
    is_correct = (selected_option_index == question_data['correct_option_index'])

    if is_correct:
        quiz_state['score'] += 1
        feedback = "¡Correcto! ✅"
    else:
        correct_answer_text = question_data['options'][question_data['correct_option_index']]
        feedback = f"Incorrecto. ❌ La respuesta correcta era: **{correct_answer_text}**"

    # Avanzar a la siguiente pregunta
    quiz_state['question_index'] += 1
    save_data() # Guardar el estado actualizado

    # Mostrar retroalimentación y la siguiente pregunta o finalizar el quiz
    if quiz_state['question_index'] < len(PYTHON_QUIZ_QUESTIONS):
        await query.edit_message_text(text=f"{feedback}\n\nCargando siguiente pregunta...")
        await send_quiz_question(update, context, user_id_str)
    else:
        await finish_quiz(update, context, user_id_str)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_str: str) -> None:
    """Finaliza el quiz y muestra la puntuación del usuario."""
    quiz_state = bot_data['quiz_state'].pop(user_id_str, None) # Eliminar el estado del quiz
    save_data()

    if quiz_state:
        total_questions = len(PYTHON_QUIZ_QUESTIONS)
        score = quiz_state['score']
        result_message = f"¡Quiz terminado! 🎉\n\nHas respondido correctamente a **{score} de {total_questions}** preguntas.\n\n"
        if score == total_questions:
            result_message += "¡Felicidades! ¡Eres un experto en Python! 🥳"
        elif score >= total_questions / 2:
            result_message += "¡Buen trabajo! Sigue practicando para mejorar. 💪"
        else:
            result_message += "No te preocupes, ¡sigue estudiando las lecciones! Siempre hay algo nuevo que aprender. 😊"
    else:
        result_message = "El quiz ha finalizado o no estaba en curso."

    await update.callback_query.edit_message_text(
        text=result_message,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard() # Volver al menú principal
    )
# termux_teacher_bot.py (Continuación)

# --- 10. Handler Principal para Botones Inline (MODIFICADO) ---

async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja las pulsaciones de los botones inline.
    Procesa las diferentes 'callback_data' para dirigir la acción del bot.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_id_str = str(user_id) # Para acceder a bot_data

    if await check_user_status(update, context): 
        return

    # --- Lógica para botones de USUARIO NORMAL ---
    if query.data == "mostrar_lecciones":
        # Iniciar desde la primera lección o la última vista
        current_lesson_index = bot_data['lesson_state'].get(user_id_str, {}).get('current_lesson_index', 0)
        await show_lesson(update, context, current_lesson_index)
    
    # --- NUEVOS HANDLERS PARA NAVEGACIÓN DE LECCIONES ---
    elif query.data.startswith("lesson_prev_"):
        lesson_index = int(query.data.split('_')[-1])
        await show_lesson(update, context, lesson_index)

    elif query.data.startswith("lesson_next_"):
        lesson_index = int(query.data.split('_')[-1])
        await show_lesson(update, context, lesson_index)
        
    elif query.data == "ir_al_quiz":
        await start_quiz(update, context) # Inicia el quiz

    # --- NUEVO HANDLER PARA RESPUESTAS DEL QUIZ ---
    elif query.data.startswith("quiz_ans_"):
        await check_quiz_answer(update, context)

    elif query.data == "mostrar_comandos_termux":
        await query.edit_message_text(text="Aquí tienes una lista de comandos de Termux. Toca uno para ver su descripción:",
                                      reply_markup=get_termux_commands_keyboard())

    elif query.data.startswith("termux_cmd_"):
        cmd_name = query.data.replace("termux_cmd_", "")
        description = TERMUX_COMMANDS.get(cmd_name, "Lo siento, no encontré una descripción para ese comando.")
        await query.edit_message_text(text=f"**Comando: `{cmd_name}`**\n\n{description}", 
                                      parse_mode='Markdown', reply_markup=get_termux_commands_keyboard())
    
    elif query.data == "ayuda_bot":
        await query.edit_message_text(text="**Ayuda del Bot:**\n"
                                          "Este bot te ayuda a aprender Python y comandos de Termux.\n\n"
                                          "📚 **Lecciones de Python:** Accede a tutoriales y explicaciones.\n"
                                          "🧠 **Quiz de Python:** Pon a prueba tus conocimientos.\n"
                                          "👨‍💻 **Comandos Termux:** Aprende sobre comandos útiles para tu terminal.\n\n"
                                          "Si tienes dudas o encuentras un error, contacta con el administrador: "
                                          f"{ADMIN_USERNAME}", parse_mode='Markdown', reply_markup=get_main_menu_keyboard())

    elif query.data == "volver_main_menu":
        await query.edit_message_text(text="Volviendo al menú principal...", 
                                      reply_markup=get_main_menu_keyboard())
        # Limpiar el estado del quiz si el usuario vuelve al menú principal durante un quiz
        if user_id_str in bot_data['quiz_state']:
            del bot_data['quiz_state'][user_id_str]
            save_data()


    # --- Lógica para BOTONES DE ADMINISTRACIÓN (solo si el usuario es ADMIN_USER_ID) ---
    elif user_id == ADMIN_USER_ID:
        if query.data == "admin_block_user":
            await query.edit_message_text(
                "Para bloquear un usuario, envía `/block <user_id>`. "
                "Ejemplo: `/block 123456789`",
                parse_mode='Markdown',
                reply_markup=get_admin_menu_keyboard()
            )
        elif query.data == "admin_unblock_user":
            await query.edit_message_text(
                "Para desbloquear un usuario, envía `/unblock <user_id>`. "
                "Ejemplo: `/unblock 123456789`",
                parse_mode='Markdown',
                reply_markup=get_admin_menu_keyboard()
            )
        elif query.data == "admin_view_strikes":
            await query.edit_message_text(
                "Para ver los strikes de un usuario, envía `/strikes <user_id>`. "
                "Ejemplo: `/strikes 123456789`",
                parse_mode='Markdown',
                reply_markup=get_admin_menu_keyboard()
            )
        elif query.data == "admin_clear_strikes":
            await query.edit_message_text(
                "Para limpiar los strikes de un usuario, envía `/strikes <user_id> clear`. "
                "Ejemplo: `/strikes 123456789 clear`",
                parse_mode='Markdown',
                reply_markup=get_admin_menu_keyboard()
            )
        elif query.data == "admin_list_blocked":
            await query.edit_message_text(
                "Para listar todos los usuarios bloqueados, envía `/listblocked`.",
                parse_mode='Markdown',
                reply_markup=get_admin_menu_keyboard()
            )
        else:
            await query.edit_message_text("Acción de administración no reconocida.",
                                          reply_markup=get_admin_menu_keyboard())
    else:
        await query.edit_message_text("Acción no reconocida o no autorizada.")
# termux_teacher_bot.py (Continuación)

# --- 11. Handlers de Comandos de Administración (Solo para el Admin) ---

async def admin_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el menú de opciones de administración."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ No tienes permisos para usar este comando.")
        return
    
    reply_markup = get_admin_menu_keyboard()
    await update.message.reply_text(
        "Bienvenido, administrador. Selecciona una opción:",
        reply_markup=reply_markup
    )

async def admin_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando de administrador para bloquear un usuario."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ No tienes permisos para usar este comando.")
        return

    if len(context.args) == 1:
        try:
            target_user_id = int(context.args[0])
            block_user(target_user_id)
            clear_strikes(target_user_id)
            await update.message.reply_text(f"Usuario {target_user_id} ha sido bloqueado y sus strikes borrados.")
            logger.info(f"Admin {ADMIN_USER_ID} bloqueó al usuario {target_user_id}.")
        except ValueError:
            await update.message.reply_text("Uso: /block <user_id>")
    else:
        await update.message.reply_text("Uso: /block <user_id>")

async def admin_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando de administrador para desbloquear un usuario."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ No tienes permisos para usar este comando.")
        return

    if len(context.args) == 1:
        try:
            target_user_id = int(context.args[0])
            unblock_user(target_user_id)
            await update.message.reply_text(f"Usuario {target_user_id} ha sido desbloqueado.")
            logger.info(f"Admin {ADMIN_USER_ID} desbloqueó al usuario {target_user_id}.")
        except ValueError:
            await update.message.reply_text("Uso: /unblock <user_id>")
    else:
        await update.message.reply_text("Uso: /unblock <user_id>")

async def admin_strikes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando de administrador para ver o limpiar strikes de un usuario."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ No tienes permisos para usar este comando.")
        return

    if len(context.args) == 1:
        try:
            target_user_id = int(context.args[0])
            user_id_str = str(target_user_id)
            strikes = bot_data['strikes'].get(user_id_str, 0)
            await update.message.reply_text(f"El usuario {target_user_id} tiene {strikes} strikes.")
        except ValueError:
            await update.message.reply_text("Uso: /strikes <user_id>")
    elif len(context.args) == 2 and context.args[1].lower() == "clear":
        try:
            target_user_id = int(context.args[0])
            clear_strikes(target_user_id)
            await update.message.reply_text(f"Los strikes del usuario {target_user_id} han sido limpiados.")
            logger.info(f"Admin {ADMIN_USER_ID} limpió strikes del usuario {target_user_id}.")
        except ValueError:
            await update.message.reply_text("Uso: /strikes <user_id> clear")
    else:
        await update.message.reply_text("Uso: /strikes <user_id> [clear]")

async def admin_list_blocked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando de administrador para listar usuarios bloqueados."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔️ No tienes permisos para usar este comando.")
        return
    
    if not bot_data['blocked_users']:
        await update.message.reply_text("No hay usuarios bloqueados actualmente.")
        return

    blocked_list_str = "Usuarios bloqueados:\n"
    for user_id in bot_data['blocked_users']:
        blocked_list_str += f"- `{user_id}`\n"
    
    await update.message.reply_text(blocked_list_str, parse_mode='Markdown')
    logger.info(f"Admin {ADMIN_USER_ID} solicitó la lista de usuarios bloqueados.")

# --- 12. Función Principal para Configurar y Ejecutar el Bot ---

def main() -> None:
    """Configura y ejecuta el bot de Telegram."""
    application = Application.builder().token(TOKEN).build()

    # --- 13. Registro de Handlers ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CallbackQueryHandler(handle_button_press))

    # Asegurarse de que `handle_bad_words` se ejecute primero para la moderación
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bad_words), group=0)

    # Handlers para comandos de administración
    application.add_handler(CommandHandler("admin_user", admin_user_menu))
    application.add_handler(CommandHandler("block", admin_block))
    application.add_handler(CommandHandler("unblock", admin_unblock))
    application.add_handler(CommandHandler("strikes", admin_strikes))
    application.add_handler(CommandHandler("listblocked", admin_list_blocked))

    # --- 14. Inicio del Bot ---
    logger.info("Bot iniciado. Esperando actualizaciones...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# --- 15. Punto de Entrada del Script ---
if __name__ == "__main__":
    main()
