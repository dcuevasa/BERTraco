import threading
import queue
from langchain_community.llms import Ollama
from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, AIMessage
from cara import MiniFace

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

def chat_loop(face, message_queue):
    """Función que maneja la lógica del chat en un hilo separado."""
    historial = []
    while True:
        try:
            # Espera a recibir un mensaje desde la GUI
            pregunta = message_queue.get()
            if pregunta is None: # Señal para terminar
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
            for chunk in respuesta_stream:
                if not animacion_iniciada:
                    # Inicia la animación y el mensaje en la GUI
                    face.after(0, face.start_speaking)
                    face.after(0, face.start_assistant_message)
                    animacion_iniciada = True
                
                # Muestra el chunk en la GUI
                face.after(0, face.append_assistant_message, chunk)
                respuesta_completa += chunk
            
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
            break


def main():
    # Cola para comunicar la GUI con el hilo de chat
    message_queue = queue.Queue()

    # Crear y mostrar la carita, pasándole la cola
    face = MiniFace(send_queue=message_queue)
    
    # Iniciar la lógica del chat en un hilo separado para no bloquear la GUI
    chat_thread = threading.Thread(target=chat_loop, args=(face, message_queue), daemon=True)
    chat_thread.start()
    
    # Iniciar el bucle principal de la GUI
    face.mainloop()

    # Al cerrar la ventana, terminar el hilo de chat
    message_queue.put(None)


if __name__ == "__main__":
    main()
