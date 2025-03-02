import requests
import json
import os
# Libreria para el speaker
import pyttsx3
# Modelo gratuito de palabras para el speaker
import vosk
# Libreria para escuchar microfono
import pyaudio
# Libreria para reconocer audio a texto  --- PARECE SER QUE NO SE USA
# import speech_recognition as sr
# Libreria para copiar en el portapapeles
import pyperclip
# Libreria para busquedas en google
from googlesearch import search
# Manipulacion de controles (Botones, raton ,etc)
import pyautogui
# Formateo de textos
import unicodedata
# Manipulacion de ventanas (Encuentra las ventanas y crea instancia)
import pygetwindow as gw
# Busqueda de textos por parametros
import re
# Manipulacion de nivel audio
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import comtypes
# Manipulacion de Brave Navegador
import webbrowser
# Libreria para sacar URL del primer video YT en base a una palabra
import yt_dlp
# Libreria para ejecutar peticiones hacia un navegador web
from bs4 import BeautifulSoup

# TODO Se conecta a la ventana creada de la lib. pygetwindow para manipularla  -------------------
import win32gui
import win32con
import win32api
import time
from pynput.keyboard import Controller

# URL del servidor de Ollama y el nombre del modelo
modelo = "mistral"  # Cambia esto por el nombre de tu modelo
url = "http://127.0.0.1:11434/api/chat"  # Cambia esto si es necesario

# Modelos de Voz
# model = vosk.Model(r"E:/vosk-model-es-0.42")  # Modelo pesado
model = vosk.Model(r"./vosk-model-small-es-0.42")  # Modelo lite

# FUNCIONES
def formatea_respuestas(texto):
    # Normaliza la cadena a forma "NFD" y elimina los caracteres de acento
    texto_sin_acentos = unicodedata.normalize('NFD', texto)
    # se regresa la cadena en mayusculas y sin espacios
    return ''.join(c for c in texto_sin_acentos if unicodedata.category(c) != 'Mn').strip().upper()

def speak(dialog):
    # Inicializar el motor de texto a voz
    engine = pyttsx3.init()

    # Configurar algunas propiedades (opcional)
    rate = engine.getProperty('rate')  # Tasa de velocidad del habla
    engine.setProperty('rate', rate - 20)  # Hacer que la voz hable más lento

    # Voces
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Cambiar a la voz femenina

    volume = engine.getProperty('volume')  # Volumen de la voz
    engine.setProperty('volume', 1)  # Volumen máximo (0.0 a 1.0)

    # Hacer que el motor lea el texto
    engine.say(dialog)

    # Esperar hasta que termine de hablar
    engine.runAndWait()

def buscar_y_copiar_enlace(palabra):
    # Realizar la búsqueda en Google
    query = palabra + " site:wikipedia.org"  # Esto limita la búsqueda a Wikipedia
    resultados = search(query, num_results=10)  # Obtener los primeros 10 resultados

    # Iterar sobre los resultados y encontrar el primer enlace a Wikipedia
    for url in resultados:
        if "es.wikipedia.org" in url:  # Verificar que el enlace es de Wikipedia
            # Copiar el enlace al portapapeles (No se ocupa)
            pyperclip.copy(url)

            # Obtener la página de Wikipedia
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)

            # Verificar si la página existe
            if response.status_code != 200:
                print("No se encontró información en Wikipedia.")
                return None

            # Analizar el HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar el primer párrafo de la página
            parrafos = soup.find_all("p")
            for parrafo in parrafos:
                texto = parrafo.get_text().strip()
                if texto:
                    print(f"\nInformación de Wikipedia sobre '{palabra}':\n")
                    speak(texto)
                    print(texto)
                    return  # Solo imprime el primer párrafo encontrado
    print("No se encontró un enlace de Wikipedia.")
    return None

def obtener_info_wikipedia(termino):
    # Convertir el término a formato URL de Wikipedia
    termino_url = termino.replace(" ", "_")
    url = f"https://es.wikipedia.org/wiki/{termino_url}"

    # Obtener la página de Wikipedia
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    # Verificar si la página existe
    if response.status_code != 200:
        print("No se encontró información en Wikipedia.")
        return

    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar el primer párrafo de la página
    parrafos = soup.find_all("p")
    for parrafo in parrafos:
        texto = parrafo.get_text().strip()
        if texto:
            print(f"\nInformación de Wikipedia sobre '{termino}':\n")
            speak(texto)
            print(texto)
            return  # Solo imprime el primer párrafo encontrado

    print("No se encontró contenido relevante en Wikipedia.")

def wiki():
    res = requests.get("https://es.wikipedia.org/w/api.php?action=query&titles=Lenguaje_de_programación_Python&prop=revisions&rvprop=content&format=json")
    print(res.json())
    res = res.json()

    for item in res['pages']['title']:
        print(item['title'])

def escuchar():
    speak("Te escucho")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

    while True:
        text = ''
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result())
            # Acceder al texto reconocido
            text = res.get("text", "")

            if text != "" and text != " ":
                print(text)  # El resultado ya está en texto
                return text

def escucha_continua():
    recognizer = vosk.KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

    while True:
        text = ''
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result())
            # Acceder al texto reconocido
            text = res.get("text", "")

            if text != "" and text != " ":
                return text

def control_audio(porcentaje, control):
    # Obtiene el controlador de audio
    dispositivos = AudioUtilities.GetSpeakers()
    interface = dispositivos.Activate(
        comtypes.GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}"),
        comtypes.CLSCTX_ALL, None)

    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Obtiene el volumen actual
    volumen_actual = volume.GetMasterVolumeLevelScalar()  # Valor entre 0.0 y 1.0

    if control == "UP":
        # Calcula el nuevo volumen
        nuevo_volumen = max(0.0, volumen_actual + (porcentaje / 100))  # Asegura que no sea menor a 0
    elif control == "DOWN":
        # Calcula el nuevo volumen
        nuevo_volumen = max(0.0, volumen_actual - (porcentaje / 100))  # Asegura que no sea menor a 0

    # Establece el nuevo volumen
    try:
        volume.SetMasterVolumeLevelScalar(nuevo_volumen, None)
    except:
        print("Error al querer modificar el sonido")

    print(f"El nuevo volumen es: {nuevo_volumen * 100:.2f}%")

def reproducir_YT(palabra):
    print("REPRODUCIOENDO")
    ruta_brave = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Ajusta si es necesario
    webbrowser.register("brave", None, webbrowser.BackgroundBrowser(ruta_brave))

    video_url = ""
    consulta = f"ytsearch:{palabra}"  # Hace una búsqueda en YouTube

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(consulta, download=False)  # Obtiene los resultados sin descargar
        if 'entries' in info and len(info['entries']) > 0:
            video_url = info['entries'][0]['webpage_url']  # Devuelve la URL del primer video


    if video_url:
        webbrowser.get("brave").open(video_url)  # Abre en Brave
        print(f"Reproduciendo video: {video_url}")
    else:
        print("No se encontró ningún video.")

def IA(texto):
    data = {
        "model": "mistral:latest",  # Nombre correcto del modelo
        "messages": [{"role": "user", "content": f"{texto}"}]
    }
    print("Respuesta antes")
    response = requests.post(url, json=data)
    print("Respuesta despues")

    # Comprobar la respuesta
    if response.status_code == 200:
        # Dividir la respuesta en líneas
        response_lines = response.text.strip().splitlines()
        contents = []

        # Procesar cada línea
        for line in response_lines:
            try:
                json_line = json.loads(line)
                if 'message' in json_line:
                    contents.append(json_line['message']['content'])
            except json.JSONDecodeError as e:
                print(f"Error al decodificar la línea: {line}\nError: {e}")

        # Unir todos los contenidos en un solo string
        full_response = ''.join(contents)
        print(full_response)
        speak(full_response)
    else:
        print(f"Error: {response.status_code}")
        speak("IA: Algo no salio bien")


# -------- COMANDOS --------
def buscaWikiPedia():
    res = "SABER MAS"
    respuestas_aceptadas = ["EH", "SABER MAS", "SI", "TI", "CI", "DI", "I", "Y", "PI", "SÍ"]

    while res in respuestas_aceptadas:
        speak("Que concepto barra palabra quieres investigar?")
        termino = escuchar()
        buscar_y_copiar_enlace(termino)
        speak("Quiere saber algo mas?")
        res = formatea_respuestas(escuchar())

def comandos_pausa_video(respuesta):
    if len(respuesta.split(" ")) == 1:
        pyautogui.press("space")
    elif len(respuesta.split(" ")) > 1:
        if respuesta.split(" ")[-1] == "YOUTUBE":
            respuesta = "- Youtube - "
        elif respuesta.split(" ")[-1] == "DISNEY":
            respuesta = "Disney"
        elif respuesta.split(" ")[-1] == "GOOGLE":
            respuesta = "Google"
        elif respuesta.split(" ")[-1] == "SPOTIFY":
            respuesta = "Spotify"
        try:
            # Encuentra la ventana por su título
            ventana = gw.getWindowsWithTitle(respuesta)[0]  # Obtiene la primera ventana que coincide

            ventana.activate()  # Activa la ventana
            # Presionamos espacio
            pyautogui.press("space")

        except IndexError:
            speak(f"No se encontró ninguna ventana con el título '{respuesta}'")

def comandos_nextPrev_video(respuesta):
    respNext = ["SIGUIENTE", "NEXT"]
    respPrev = ["ATRAS", "ANTERIOR"]

    if respuesta.split(" ")[0] in respNext:
        if respuesta.split(" ")[-1] == "YOUTUBE" or respuesta.split(" ")[-1] == "VIDEO":
            respuesta = "- Youtube - "
            control = ["shift", "n"]
        elif respuesta.split(" ")[-1] == "DISNEY":
            respuesta = "Disney"
            control = ["shift", "n"]
        elif respuesta.split(" ")[-1] == "GOOGLE":
            respuesta = "Google"
            control = ["shift", "n"]
        elif respuesta.split(" ")[-1] == "SPOTIFY":
            respuesta = "Spotify"
            control = ["shift", "n"]
        try:
            # Encuentra la ventana por su título
            ventana = gw.getWindowsWithTitle(respuesta)[0]  # Obtiene la primera ventana que coincide
            ventana.activate()  # Activa la ventana
            # Presionamos espacio
            pyautogui.hotkey(*control)

        except IndexError:
            speak(f"No se encontró ninguna ventana con el título '{respuesta}'")

    elif respuesta.split(" ")[0] in respPrev:
        if respuesta.split(" ")[-1] == "YOUTUBE" or respuesta.split(" ")[-1] == "VIDEO":
            respuesta = "Youtube"
        elif respuesta.split(" ")[-1] == "DISNEY":
            respuesta = "Disney"
        elif respuesta.split(" ")[-1] == "GOOGLE":
            respuesta = "Google"
        elif respuesta.split(" ")[-1] == "SPOTIFY":
            respuesta = "Spotify"
        try:
            # Encuentra la ventana por su título
            ventana = gw.getWindowsWithTitle(respuesta)[0]  # Obtiene la primera ventana que coincide
            ventana.activate()  # Activa la ventana
            # Presionamos espacio
            pyautogui.press("space")

        except IndexError:
            speak(f"No se encontró ninguna ventana con el título '{respuesta}'")

def comandos_audio(respuesta):
    aumento = ["AUMENTA", "INCREMENTA", "INCREMENTO", "INCREMENTO", "SUBE", "INCREMENTAN"]
    decremento = ["DISMINUYE", "DISMINUYO", "DISMINUYEN", "BAJA", "BAJO"]
    porcentaje = ["PORCIENTO", "PORCENTAGE"]
    if respuesta.split(" ")[0] in aumento:
        print("Aumenta")
        if respuesta.split(" ")[-1] in porcentaje:
            if "1" in respuesta:
                print("Aumenta %1")
                control_audio(1, "UP")
            elif "CINCO" in respuesta:
                print("Aumenta %5")
                control_audio(5, "UP")
            elif "DIEZ" in respuesta:
                print("Aumenta %10")
                control_audio(10, "UP")
            elif "TREINTA" in respuesta:
                print("Aumenta %30")
                control_audio(30, "UP")
            elif "CINCUENTA" in respuesta:
                print("Aumenta %50")
                control_audio(50, "UP")
            elif "CIEN" in respuesta:
                print("Aumenta %100")
                control_audio(100, "UP")
    elif respuesta.split(" ")[0] in decremento:
        print("Decrementa")
        if respuesta.split(" ")[-1] in porcentaje:
            if "1" in respuesta:
                print("Aumenta %1")
                control_audio(1, "DOWN")
            elif "CINCO" in respuesta:
                print("Aumenta %5")
                control_audio(5, "DOWN")
            elif "DIEZ" in respuesta:
                print("Aumenta %10")
                control_audio(10, "DOWN")
            elif "TREINTA" in respuesta:
                print("Aumenta %30")
                control_audio(30, "DOWN")
            elif "CINCUENTA" in respuesta:
                print("Aumenta %50")
                control_audio(50, "DOWN")
            elif "CIEN" in respuesta:
                print("Aumenta %100")
                control_audio(100, "DOWN")

def comando_reproducir(palabra):
    if len(palabra.split(" ")) <= 1:
        speak("Que repordusco?")
        palabra = escuchar()
        reproducir_YT(palabra)
    else:
        reproducir_YT(palabra)

def comandoIA():
    res = "SABER MAS"
    respuestas_aceptadas = ["EH", "SABER MAS", "SI", "TI", "CI", "DI", "I", "Y", "PI", "SÍ"]

    while res in respuestas_aceptadas:
        speak("Dime?")
        pregunta = escuchar()
        IA(pregunta)
        speak("Desea saber algo mas?")
        res = formatea_respuestas(escuchar())


# speak("    Hola soy un robot tonto que te responde despues del Te escucho")
speak("    Activado")
speak("    Estare de fondo escuchandote si necesitas algo mas")
finalizarKelo = True
while finalizarKelo:
    opcion = formatea_respuestas(escucha_continua())
    print("?? "+opcion)
    res_comando_busqueda = ["BUSCAR", "BUSCA", "BUSQUEDA", "INVESTIGA"]
    res_comando_video = ["PAUSA", "DESPAUSA", "CONTINUA", "SIGUE", "PAUSAS", "DETEN", "PARA"]
    res_comando_nextOrPrevVideo = ["SIGUIENTE", "NEXT", "ATRAS", "ANTERIOR"]
    res_comando_audio = ["SONIDO", "AUDIO", "PORCIENTO"]
    res_comando_reproduceYT = ["REPRODUCE", "PON", "REPRODUCIO", "PRODUCE", "REPRODUCIR"]
    res_comando_IA = ["VIERNES"]

    if opcion in res_comando_busqueda:
        buscaWikiPedia()
    elif opcion.split(" ")[0] in res_comando_video:
        comandos_pausa_video(opcion)
    elif opcion.split(" ")[0] in res_comando_nextOrPrevVideo:
        comandos_nextPrev_video(opcion)
    elif opcion.split(" ")[-1] in res_comando_audio:
        comandos_audio(opcion)
    elif opcion.split(" ")[0] in res_comando_reproduceYT:
        comando_reproducir(opcion)
    elif opcion in res_comando_IA:
        comandoIA()


# ----------------------------------------------- COMANDOS ACTUALES -----------------------------------------------

# BUSQUEDA DESDE WIKIPEDIA: ["BUSCAR", "BUSCA", "BUSQUEDA", "INVESTIGA"]

# REPRODUCE VIDEOS EN YT: ["REPRODUCE", "PON", "REPRODUCIO", "PRODUCE", "REPRODUCIR"] + "NOMBRE DE LO QUE QUIERES REPRODUCIR"

# PASUSA VIDEO SI ESTYA:  OR ["PAUSA", "DESPAUSA", "CONTINUA", "SIGUE", "PAUSAS", "DETEN", "PARA"] + "QUE QUIERES PAUSAR"

# CONTROL AUDIO: [CUALQUIER SINONIMO DE AUMENTO O DECREMENTO] + [SINONIMOS DE SONIDO] + [PORCENTAJE]

