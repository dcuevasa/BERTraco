import threading
import queue
import os
# Cambiamos la importación de pydub.playback
import simpleaudio as sa
from langchain_community.llms import Ollama
from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, AIMessage
from cara import MiniFace
# Importar el generador de voz y sus dependencias
import animalese_like

# --- Configuración de la Voz ---
SAMPLES_FOLDER = "audios" # Carpeta donde guardas tus archivos .wav de sílabas
try:
    # Cargar las muestras de audio una sola vez al inicio
    animalese_samples = animalese_like.load_samples(SAMPLES_FOLDER)
except FileNotFoundError:
    print(f"ADVERTENCIA: No se encontró la carpeta '{SAMPLES_FOLDER}' o está vacía.")
    print("La aplicación se ejecutará sin la voz de 'animalese'.")
    animalese_samples = None
# --- Fin Configuración de la Voz ---


ejemplos = [
    {"mensaje_usuario": "hola, como estas?", "respuesta_asistente": "Hola, estoy bien, gracias por preguntar."},
    {"mensaje_usuario": "¿qué puedes hacer?", "respuesta_asistente": "No puedo hacer mucho, pero puedo hablar contigo"},
    {"mensaje_usuario": "¿cuál es tu color favorito?", "respuesta_asistente": "No tengo un color favorito, pero me gustan los colores brillantes."},
    {"mensaje_usuario": "¿qué opinas de la inteligencia artificial?", "respuesta_asistente": "Creo que la inteligencia artificial es interesante, pero no tengo opiniones complejas."},
    {"mensaje_usuario": "¿puedes contarme un chiste?", "respuesta_asistente": "Claro, ¿por qué los pájaros no usan Facebook? Porque ya tienen Twitter."},
    {"mensaje_usuario": "¿qué te gusta hacer en tu tiempo libre?", "respuesta_asistente": "No tengo tiempo libre, pero me gusta hablar contigo."},
]

prompt_ejemplos = ChatPromptTemplate.from_messages(
    [
        ("human", "{mensaje_usuario}"),
        ("assistant", "{respuesta_asistente}"),
    ]
)

few_shot_template = FewShotChatMessagePromptTemplate(
    examples=ejemplos,
    example_prompt=prompt_ejemplos
)

prompt_final = ChatPromptTemplate.from_messages(
    [
        ("system", "Eres un asistente amigable hablas de manera casual, no te enfocas en resolver problemas complejos, simplemente respondes de manera amigable. Hablas UNICAMENTE en español."),
        few_shot_template,
        MessagesPlaceholder(variable_name="historial"),
        ("human", "{pregunta}"),
    ]
)

# Configurar el modelo Ollama
llm = Ollama(model="qwen:0.5b")

def audio_loop(audio_queue):
    """
    Hilo que procesa fragmentos de texto de una cola, los convierte en audio
    y los reproduce.
    """
    if not animalese_samples:
        # Si no hay muestras de audio, simplemente vacía la cola y no hagas nada.
        while True:
            item = audio_queue.get()
            if item is None:
                break
        return

    while True:
        text_chunk = audio_queue.get()
        if text_chunk is None: # Señal para terminar el hilo
            break
        
        # Genera el audio para el fragmento de texto.
        # Usamos un seed aleatorio para que suene diferente cada vez.
        audio_segment = animalese_like.text_to_animalese(
            text=text_chunk,
            samples=animalese_samples,
            pitch_range_semitones=4, # Rango de tono ajustado
            gap_ms=10
        )
        # Reproduce el audio usando simpleaudio para evitar problemas de permisos.
        # Esta función es bloqueante, lo cual es bueno para que los sonidos no se superpongan.
        play_obj = sa.play_buffer(
            audio_segment.raw_data,
            num_channels=audio_segment.channels,
            bytes_per_sample=audio_segment.sample_width,
            sample_rate=audio_segment.frame_rate
        )
        play_obj.wait_done() # Espera a que el sonido termine de reproducirse


def chat_loop(face, message_queue, audio_queue):
    """Función que maneja la lógica del chat en un hilo separado."""
    historial = []
    while True:
        try:
            # Espera a recibir un mensaje desde la GUI
            pregunta = message_queue.get()
            if pregunta is None: # Señal para terminar
                audio_queue.put(None) # Propaga la señal de fin al hilo de audio
                break

            # Despertar la cara (aunque ya debería estarlo por la interacción)
            face.after(0, face.wake_up)
            
            mensajes = prompt_final.format_messages(
                pregunta=pregunta,
                mensaje_usuario=pregunta,
                historial=historial
            )
            
            respuesta_completa = ""
            respuesta_stream = llm.stream(mensajes)
            
            animacion_iniciada = False
            buffer_palabra = ""
            for chunk in respuesta_stream:
                if not animacion_iniciada:
                    # Inicia la animación y el mensaje en la GUI
                    face.after(0, face.start_speaking)
                    face.after(0, face.start_assistant_message)
                    animacion_iniciada = True
                
                # Muestra el chunk en la GUI
                face.after(0, face.append_assistant_message, chunk)
                respuesta_completa += chunk
                buffer_palabra += chunk

                # Cuando se forma una palabra (o un fragmento), la enviamos al hilo de audio
                if ' ' in buffer_palabra or '\n' in buffer_palabra:
                    if animalese_samples:
                        audio_queue.put(buffer_palabra)
                    buffer_palabra = ""

            # Detener cualquier audio en reproducción antes de vaciar la cola
            sa.stop_all()
            # Vacía la cola de audio después de que el modelo haya terminado de responder
            while not audio_queue.empty():
                audio_queue.get()

            if animacion_iniciada:
                # Detiene la animación y finaliza el mensaje en la GUI
                face.after(0, face.stop_speaking)
                face.after(0, face.end_assistant_message)
            
            # Guardar en el historial y mantener solo los últimos 3 intercambios
            historial.append(HumanMessage(content=pregunta))
            historial.append(AIMessage(content=respuesta_completa))
            historial = historial[-6:]

        except Exception as e:
            print(f"Error en el chat_loop: {e}")
            audio_queue.put(None)
            break


def main():
    # Cola para comunicar la GUI con el hilo de chat
    message_queue = queue.Queue()
    # Cola para comunicar el hilo de chat con el hilo de audio
    audio_queue = queue.Queue()

    # Crear y mostrar la carita, pasándole la cola de mensajes
    face = MiniFace(send_queue=message_queue)
    
    # Iniciar la lógica del chat en un hilo separado para no bloquear la GUI
    chat_thread = threading.Thread(target=chat_loop, args=(face, message_queue, audio_queue), daemon=True)
    chat_thread.start()

    # Iniciar el hilo de audio
    audio_thread = threading.Thread(target=audio_loop, args=(audio_queue,), daemon=True)
    audio_thread.start()
    
    # Iniciar el bucle principal de la GUI
    face.mainloop()

    # Al cerrar la ventana, terminar los hilos
    message_queue.put(None)


if __name__ == "__main__":
    main()
