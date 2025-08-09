import threading
import queue
import time
import os

# --- Módulo de Traducción ---
import argostranslate.package
import argostranslate.translate

# --- Configuración de la Traducción (Lógica Corregida) ---
def setup_translation():
    """
    Comprueba si los modelos de traducción están instalados.
    Si no lo están, los descarga e instala desde internet.
    """
    # Primero, comprueba si los idiomas y las traducciones ya existen
    installed_langs = argostranslate.translate.get_installed_languages()
    es = next((lang for lang in installed_langs if lang.code == "es"), None)
    en = next((lang for lang in installed_langs if lang.code == "en"), None)

    if es and en and es.get_translation(en) and en.get_translation(es):
        print("Modelos de traducción (es <-> en) ya están instalados.")
        return es.get_translation(en), en.get_translation(es)

    # Si no están, proceder a la descarga e instalación
    print("Modelos de traducción no encontrados. Descargando e instalando...")
    try:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        # Función para encontrar e instalar un paquete específico
        def find_and_install(from_code, to_code):
            package_to_install = next(
                (p for p in available_packages if p.from_code == from_code and p.to_code == to_code),
                None
            )
            if package_to_install is None:
                raise ValueError(f"No se encontró el paquete de traducción de {from_code} a {to_code}.")
            
            print(f"Instalando: {package_to_install.from_name} -> {package_to_install.to_name}")
            package_to_install.install()

        # Instalar los paquetes necesarios (si no están ya)
        if not (en and en.get_translation(es)):
            find_and_install("en", "es")
        if not (es and es.get_translation(en)):
            find_and_install("es", "en")

        # Recargar los idiomas y devolver los traductores
        installed_langs = argostranslate.translate.get_installed_languages()
        es = next(lang for lang in installed_langs if lang.code == "es")
        en = next(lang for lang in installed_langs if lang.code == "en")
        print("Modelos de traducción instalados y cargados correctamente.")
        return es.get_translation(en), en.get_translation(es)

    except Exception as e:
        print(f"Error crítico durante la configuración de la traducción: {e}")
        print("Asegúrate de tener una conexión a internet para descargar los modelos.")
        exit()

# Inicializar la traducción
es_to_en_translator, en_to_es_translator = setup_translation()

def translate_es_to_en(text):
    print(f"Traduciendo de español a inglés: {text}")
    return es_to_en_translator.translate(text)

def translate_en_to_es(text):
    print(f"Traduciendo de inglés a español: {text}")
    return en_to_es_translator.translate(text)
# --- Fin Módulo de Traducción ---


import simpleaudio as sa
from langchain_community.llms import Ollama
from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, AIMessage
from cara import MiniFace
import animalese_like

# --- Configuración de la Voz ---
SAMPLES_FOLDER = "audios"
try:
    animalese_samples = animalese_like.load_samples(SAMPLES_FOLDER)
except FileNotFoundError:
    print(f"ADVERTENCIA: No se encontró la carpeta '{SAMPLES_FOLDER}'. La aplicación se ejecutará sin voz.")
    animalese_samples = None
# --- Fin Configuración de la Voz ---

# --- Prompt en INGLÉS para el modelo ---
ejemplos_en = [
    {"mensaje_usuario": "hello, how are you?", "respuesta_asistente": "Hello, I'm fine, thanks for asking."},
    {"mensaje_usuario": "what can you do?", "respuesta_asistente": "I can't do much, but I can talk to you."},
    {"mensaje_usuario": "what is your favorite color?", "respuesta_asistente": "I don't have a favorite color, but I like bright colors."},
    {"mensaje_usuario": "can you tell me a joke?", "respuesta_asistente": "Sure, why don't scientists trust atoms? Because they make up everything!"},
]

prompt_ejemplos_en = ChatPromptTemplate.from_messages(
    [
        ("human", "{mensaje_usuario}"),
        ("assistant", "{respuesta_asistente}"),
    ]
)

few_shot_template_en = FewShotChatMessagePromptTemplate(
    examples=ejemplos_en,
    example_prompt=prompt_ejemplos_en
)

prompt_final_en = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a friendly assistant. You speak casually, you don't focus on solving complex problems, you just respond in a friendly way. You ONLY speak in English."),
        few_shot_template_en,
        MessagesPlaceholder(variable_name="historial"),
        ("human", "{pregunta}"),
    ]
)
# --- Fin Prompt en INGLÉS ---

# Configurar el modelo Ollama
llm = Ollama(model="qwen:0.5b")

def audio_loop(audio_queue):
    if not animalese_samples:
        while True:
            if audio_queue.get() is None: break
        return

    while True:
        text_chunk = audio_queue.get()
        if text_chunk is None: break
        
        audio_segment = animalese_like.text_to_animalese(
            text=text_chunk, samples=animalese_samples, pitch_range_semitones=4, gap_ms=10
        )
        play_obj = sa.play_buffer(
            audio_segment.raw_data, audio_segment.channels,
            audio_segment.sample_width, audio_segment.frame_rate
        )
        play_obj.wait_done()

def chat_loop(face, message_queue, audio_queue):
    historial_en = [] # El historial ahora debe estar en inglés
    while True:
        try:
            pregunta_es = message_queue.get()
            if pregunta_es is None:
                audio_queue.put(None)
                break

            face.after(0, face.wake_up)
            
            # 1. Traducir pregunta del usuario a inglés
            pregunta_en = translate_es_to_en(pregunta_es)
            
            mensajes = prompt_final_en.format_messages(
                pregunta=pregunta_en,
                mensaje_usuario=pregunta_en,
                historial=historial_en
            )
            
            # Recolectar la respuesta completa en inglés primero
            respuesta_en_completa = ""
            for chunk in llm.stream(mensajes):
                respuesta_en_completa += chunk
            
            # 2. Traducir la respuesta completa del LLM a español
            respuesta_es_completa = translate_en_to_es(respuesta_en_completa)

            # 3. Simular el "streaming" de la respuesta traducida
            face.after(0, face.start_speaking)
            face.after(0, face.start_assistant_message)
            
            palabras_es = respuesta_es_completa.split()
            for palabra in palabras_es:
                # Añadir la palabra (y un espacio) a la GUI
                face.after(0, face.append_assistant_message, f"{palabra} ")
                
                # Poner la palabra en la cola de audio para generar sonido
                if animalese_samples:
                    audio_queue.put(palabra)
                
                # Pequeña pausa para simular el ritmo de habla
                time.sleep(0.1) 
            
            sa.stop_all()
            while not audio_queue.empty(): audio_queue.get()

            face.after(0, face.stop_speaking)
            face.after(0, face.end_assistant_message)
            
            # Guardar en el historial (en inglés)
            historial_en.append(HumanMessage(content=pregunta_en))
            historial_en.append(AIMessage(content=respuesta_en_completa))
            historial_en = historial_en[-6:]

        except Exception as e:
            print(f"Error en el chat_loop: {e}")
            audio_queue.put(None)
            break

def main():
    message_queue = queue.Queue()
    audio_queue = queue.Queue()
    face = MiniFace(send_queue=message_queue)
    
    threading.Thread(target=chat_loop, args=(face, message_queue, audio_queue), daemon=True).start()
    threading.Thread(target=audio_loop, args=(audio_queue,), daemon=True).start()
    
    face.mainloop()
    message_queue.put(None)

if __name__ == "__main__":
    main()
