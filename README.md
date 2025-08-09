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

A continuación se detallan los pasos para instalar y ejecutar BERTraco tanto en Windows como en Linux.

### Windows

**1. Instalar Ollama**

Necesitas tener Ollama instalado para ejecutar el modelo de lenguaje local.
*   Ve a la página oficial de Ollama: [ollama.com](https://ollama.com/).
*   Descarga el instalador para Windows y sigue las instrucciones.

**2. Descargar el Modelo de Lenguaje (LLM)**

El proyecto está configurado para usar `qwen:0.5b`, un modelo pequeño y eficiente. Una vez instalado Ollama, abre el Símbolo del sistema (Command Prompt) o PowerShell y ejecuta:
```bash
ollama pull qwen:0.5b
```
*Nota: Puedes experimentar con otros modelos pequeños cambiando el nombre del modelo en la línea `llm = Ollama(model="qwen:0.5b")` del archivo [`BERTraco.py`](d:\David\Trabajos\Entregas\Proyectos\BERTraco\BERTraco.py).*

**3. Instalar Python**

Si no tienes Python, descárgalo desde [python.org](https://www.python.org/). Se recomienda la versión 3.8 o superior. Asegúrate de marcar la casilla "Add Python to PATH" durante la instalación. `Tkinter` generalmente viene incluido.

**4. Configurar el Proyecto**

*   **Clona el Repositorio:** Abre una terminal (cmd o PowerShell) y ejecuta:
    ```bash
    git clone https://github.com/tu-usuario/BERTraco.git
    cd BERTraco
    ```
    *(Reemplaza la URL por la del repositorio real).*

*   **Crea un Entorno Virtual (Recomendado):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

*   **Instala las Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

**5. Ejecutar la Aplicación**

Asegúrate de que el servicio de Ollama se esté ejecutando en segundo plano. Luego, en la misma terminal con el entorno virtual activado, inicia la aplicación:
```bash
python BERTraco.py
```

### Linux

**1. Instalar Ollama**

*   **Instalación:** Abre una terminal y ejecuta el siguiente comando:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
*   **Página oficial:** Para más información, visita [ollama.com](https://ollama.com/).

**2. Descargar el Modelo de Lenguaje (LLM)**

Una vez instalado Ollama, descarga el modelo con este comando en tu terminal:
```bash
ollama pull qwen:0.5b
```
*Nota: Puedes experimentar con otros modelos pequeños cambiando el nombre del modelo en la línea `llm = Ollama(model="qwen:0.5b")` del archivo [`BERTraco.py`](d:\David\Trabajos\Entregas\Proyectos\BERTraco\BERTraco.py).*

**3. Dependencias del Sistema**

El proyecto requiere `tkinter`. Si no está instalado, puedes instalarlo en sistemas basados en Debian/Ubuntu con:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**4. Configurar el Proyecto**

*   **Clona el Repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/BERTraco.git
    cd BERTraco
    ```
    *(Reemplaza la URL por la del repositorio real).*

*   **Crea un Entorno Virtual (Recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

*   **Instala las Dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

**4. Ejecuta la Aplicación**

Asegúrate de que el servicio de Ollama se esté ejecutando en segundo plano. Luego, inicia la aplicación:

```bash
python3 BERTraco.py
```

¡Y listo! La ventana de BERTraco aparecerá y podrás empezar a chatear con tu nuevo compañero de IA.