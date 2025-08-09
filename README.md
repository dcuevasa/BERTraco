# BERTraco - Tu Compañero de IA Local

BERTraco es un asistente de escritorio simple y amigable diseñado para funcionar de manera eficiente en computadoras de bajos recursos. Utiliza un modelo de lenguaje pequeño que se ejecuta localmente a través de Ollama, lo que garantiza tu privacidad y un funcionamiento sin necesidad de una conexión a internet constante (después de la configuración inicial).

Su principal característica es una interfaz gráfica con una cara animada que reacciona a la conversación, creando una experiencia de usuario más interactiva y entretenida.



## Características

*   **100% Local:** El modelo de lenguaje se ejecuta en tu propia máquina. Tus conversaciones son privadas.
*   **Bajo Consumo de Recursos:** Optimizado para hardware antiguo o con especificaciones modestas.
*   **Interfaz Animada:** Una cara expresiva que parpadea, mira a su alrededor, "habla" mientras genera respuestas e incluso se duerme si no hay interacción.
*   **Chat Persistente:** Recuerda los últimos intercambios de la conversación actual para mantener el contexto.
*   **Fácil de Configurar:** Con unos pocos pasos, puedes tener tu propio asistente de IA personal.

## Requisitos

Este proyecto fue desarrollado y probado en **Lubuntu 20.04** con **Python 3.8.10**, pero debería ser compatible con la mayoría de las distribuciones de Linux modernas.

### 1. Ollama

Necesitas tener Ollama instalado para ejecutar el modelo de lenguaje local. Ollama es una herramienta que facilita la ejecución de LLMs de código abierto.

*   **Instalación en Linux:** Abre una terminal y ejecuta el siguiente comando:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
*   **Página oficial:** Para más información o instrucciones para otros sistemas operativos, visita [ollama.com](https://ollama.com/).

### 2. Modelo de Lenguaje (LLM)

El proyecto está configurado para usar `qwen:0.5b`, un modelo pequeño y eficiente. Una vez instalado Ollama, descarga el modelo con este comando en tu terminal:

```bash
ollama pull qwen:0.5b
```
*Nota: Puedes experimentar con otros modelos pequeños cambiando el nombre del modelo en la línea `llm = Ollama(model="qwen:0.5b")` del archivo `BERTraco.py`.*

### 3. Dependencias de Python

El proyecto requiere varias librerías de Python, las cuales están listadas en el archivo `requirements.txt`.

La librería `tkinter` también es necesaria, pero generalmente viene incluida con las instalaciones de Python en Linux. Si encuentras un error relacionado con `tkinter`, puedes instalarla en sistemas basados en Debian/Ubuntu con el siguiente comando:

```bash
sudo apt-get update
sudo apt-get install python3-tk
```

## Guía de Instalación

Sigue estos pasos para poner en marcha a BERTraco:

**1. Clona el Repositorio**

Abre tu terminal, navega al directorio donde quieras guardar el proyecto y clónalo.

```bash
git clone https://github.com/tu-usuario/BERTraco.git
cd BERTraco
```
*(Reemplaza `https://github.com/tu-usuario/BERTraco.git` con la URL real del repositorio).*

**2. Crea un Entorno Virtual (Recomendado)**

Es una buena práctica aislar las dependencias del proyecto.

```bash
# Asegúrate de estar usando la versión correcta de python
python3.8 -m venv venv
source venv/bin/activate
```
*Ahora verás `(venv)` al principio de tu línea de comandos.*

**3. Instala las Dependencias**

Instala todas las librerías de Python necesarias usando el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

**4. Ejecuta la Aplicación**

Asegúrate de que el servicio de Ollama se esté ejecutando en segundo plano. Luego, inicia la aplicación:

```bash
python3 BERTraco.py
```

¡Y listo! La ventana de BERTraco aparecerá y podrás empezar a chatear con tu nuevo compañero de IA.