import tkinter as tk
from tkinter import scrolledtext
import random
import time

class MiniFace(tk.Tk):
    def __init__(self, send_queue):
        super().__init__()
        self.send_queue = send_queue
        # --- Constantes de Configuración de la Cara ---
        self.CANVAS_WIDTH = 200
        self.CANVAS_HEIGHT = 200

        # Geometría de los Ojos
        self.EYE1_COORDS = (45, 50, 85, 80)
        self.EYE2_COORDS = (115, 50, 155, 80)
        self.PUPIL1_COORDS = (58, 58, 72, 72)
        self.PUPIL2_COORDS = (128, 58, 142, 72)

        # Geometría de la Boca
        self.MOUTH_Y = 130
        self.MOUTH_X1 = 70
        self.MOUTH_X2 = 130
        self.MOUTH_OPEN_HEIGHT = 145
        
        # Geometría de la Lengua
        self.TONGUE_COORDS = (85, 135, 115, 170)

        # Parámetros de Animación
        self.ANIMATION_INTERVAL_MS = 500
        self.IDLE_DELAY_MIN_S = 1.5
        self.IDLE_DELAY_MAX_S = 5.0
        self.SLEEP_TIMEOUT_S = 10.0 # Tiempo de inactividad para dormir
        # --- Fin de Constantes ---

        self.title("Asistente Simple")
        self.canvas = tk.Canvas(self, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg="white")
        self.canvas.pack()

        # --- Widgets de Chat ---
        self.chat_display = scrolledtext.ScrolledText(self, state='disabled', height=8, width=50, wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=5, fill="both", expand=True)

        input_frame = tk.Frame(self)
        input_frame.pack(padx=10, pady=5, fill="x")

        self.input_entry = tk.Entry(input_frame, width=40)
        self.input_entry.pack(side=tk.LEFT, fill="x", expand=True)
        self.input_entry.bind("<Return>", self.send_message)

        send_button = tk.Button(input_frame, text="Enviar", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        # --- Fin Widgets de Chat ---

        # Ojos
        self.eye1 = self.canvas.create_oval(*self.EYE1_COORDS, fill="white", outline="black", width=2)
        self.eye2 = self.canvas.create_oval(*self.EYE2_COORDS, fill="white", outline="black", width=2)
        self.pupil1 = self.canvas.create_oval(*self.PUPIL1_COORDS, fill="black")
        self.pupil2 = self.canvas.create_oval(*self.PUPIL2_COORDS, fill="black")

        # Boca (línea simple cuando está cerrada)
        self.mouth = self.canvas.create_line(self.MOUTH_X1, self.MOUTH_Y, self.MOUTH_X2, self.MOUTH_Y, width=3)
        
        # Lengua (oculta inicialmente)
        self.tongue = self.canvas.create_oval(*self.TONGUE_COORDS, fill="pink", outline="red", state='hidden')

        self.speaking = False
        self.sleeping = False # Nuevo estado para dormir
        self.z_particles = [] # Para almacenar las Zs
        self.last_activity_time = time.time()
        self.idle_delay = self.IDLE_DELAY_MIN_S

        self.animation_loop()

    def send_message(self, event=None):
        """Envía el mensaje del Entry a la cola de procesamiento."""
        msg = self.input_entry.get()
        if msg.strip():
            self.send_queue.put(msg)
            self.display_message("Tú", msg)
            self.input_entry.delete(0, tk.END)

    def display_message(self, sender, message):
        """Muestra un mensaje en el widget de chat."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def start_assistant_message(self):
        """Prepara el display para un nuevo mensaje del asistente."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "Asistente: ")
        self.chat_display.config(state='disabled')

    def append_assistant_message(self, chunk):
        """Añade un fragmento del mensaje del asistente al display."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, chunk)
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def end_assistant_message(self):
        """Finaliza el mensaje del asistente con un salto de línea."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def wake_up(self):
        """Despierta la cara si está durmiendo."""
        if self.sleeping:
            self.stop_sleeping()
        self.last_activity_time = time.time()

    def start_speaking(self):
        self.wake_up()
        self.speaking = True

    def stop_speaking(self):
        self.speaking = False
        self.last_activity_time = time.time()
        # Restaurar boca y ojos a estado neutral
        self.canvas.delete(self.mouth)
        self.mouth = self.canvas.create_line(self.MOUTH_X1, self.MOUTH_Y, self.MOUTH_X2, self.MOUTH_Y, width=3)
        self.reset_eyes()

    def start_sleeping(self):
        """Inicia la animación de dormir."""
        if self.speaking:
            self.stop_speaking()
        
        self.speaking = False
        self.sleeping = True
        
        # Cerrar los ojos (como en blink)
        eye1_closed_coords = (self.EYE1_COORDS[0], self.EYE1_COORDS[1] + 15, self.EYE1_COORDS[2], self.EYE1_COORDS[1] + 15)
        eye2_closed_coords = (self.EYE2_COORDS[0], self.EYE2_COORDS[1] + 15, self.EYE2_COORDS[2], self.EYE2_COORDS[1] + 15)
        self.canvas.coords(self.eye1, *eye1_closed_coords)
        self.canvas.coords(self.eye2, *eye2_closed_coords)
        self.canvas.itemconfig(self.pupil1, state='hidden')
        self.canvas.itemconfig(self.pupil2, state='hidden')

    def stop_sleeping(self):
        """Detiene la animación de dormir."""
        self.sleeping = False
        for z in self.z_particles:
            self.canvas.delete(z)
        self.z_particles = []
        self.reset_eyes()

    def animate_mouth(self):
        # Variaciones al hablar
        open_width_offset = random.randint(-5, 5)
        
        # Cambia entre línea y óvalo para abrir/cerrar
        if self.canvas.type(self.mouth) == 'line':
            self.canvas.delete(self.mouth)
            self.mouth = self.canvas.create_oval(
                self.MOUTH_X1 + open_width_offset, self.MOUTH_Y, 
                self.MOUTH_X2 - open_width_offset, self.MOUTH_OPEN_HEIGHT, 
                fill="black"
            )
            # Mover pupilas un poco al hablar
            self.canvas.move(self.pupil1, 0, random.randint(-1, 1))
            self.canvas.move(self.pupil2, 0, random.randint(-1, 1))
        else:
            self.canvas.delete(self.mouth)
            self.mouth = self.canvas.create_line(self.MOUTH_X1, self.MOUTH_Y, self.MOUTH_X2, self.MOUTH_Y, width=3)
            self.reset_eyes() # Vuelve a centrar los ojos al cerrar la boca

    def animate_sleep(self):
        """Anima las Zs mientras duerme."""
        # Crear una nueva Z de vez en cuando
        if random.random() < 0.1:
            z_id = self.canvas.create_text(self.CANVAS_WIDTH - 30, self.MOUTH_Y - 20, text="Z", font=("Arial", 12))
            self.z_particles.append(z_id)

        # Mover y eliminar las Zs que se van
        particles_to_remove = []
        for z in self.z_particles:
            self.canvas.move(z, -1, -2)
            x, y = self.canvas.coords(z)
            if y < 0: # Si la Z sale por arriba
                particles_to_remove.append(z)
        
        for z in particles_to_remove:
            self.canvas.delete(z)
            self.z_particles.remove(z)

    def animation_loop(self):
        if self.speaking:
            self.last_activity_time = time.time()
            self.animate_mouth()
        elif self.sleeping:
            self.animate_sleep()
        elif time.time() - self.last_activity_time > self.SLEEP_TIMEOUT_S:
            self.start_sleeping()
        # Modificación clave: Añadir 'and not self.sleeping' a la condición.
        elif time.time() - self.last_activity_time > self.idle_delay and not self.sleeping:
            self.run_random_idle_animation()
            self.idle_delay = random.uniform(self.IDLE_DELAY_MIN_S, self.IDLE_DELAY_MAX_S)

        self.after(self.ANIMATION_INTERVAL_MS, self.animation_loop)

    def run_random_idle_animation(self):
        animations = [self.blink, self.look_around, self.long_blink, self.stick_tongue, self.concentrate]
        # Ponderación: hacer que pestañear sea más común
        weights = [0.55, 0.2, 0.05, 0.05, 0.15]
        chosen_animation = random.choices(animations, weights)[0]
        chosen_animation()

    def reset_eyes(self):
        # Solo resetea los ojos si la cara no está durmiendo.
        if self.sleeping:
            return

        self.canvas.coords(self.eye1, *self.EYE1_COORDS)
        self.canvas.coords(self.eye2, *self.EYE2_COORDS)
        self.canvas.coords(self.pupil1, *self.PUPIL1_COORDS)
        self.canvas.coords(self.pupil2, *self.PUPIL2_COORDS)
        self.canvas.itemconfig(self.eye1, fill="white")
        self.canvas.itemconfig(self.eye2, fill="white")
        self.canvas.itemconfig(self.pupil1, state='normal')
        self.canvas.itemconfig(self.pupil2, state='normal')

    def blink(self, duration=50):
        # Coordenadas para ojos cerrados (línea horizontal)
        eye1_closed_coords = (self.EYE1_COORDS[0], self.EYE1_COORDS[1] + 15, self.EYE1_COORDS[2], self.EYE1_COORDS[1] + 15)
        eye2_closed_coords = (self.EYE2_COORDS[0], self.EYE2_COORDS[1] + 15, self.EYE2_COORDS[2], self.EYE2_COORDS[1] + 15)
        
        self.canvas.coords(self.eye1, *eye1_closed_coords)
        self.canvas.coords(self.eye2, *eye2_closed_coords)
        self.canvas.itemconfig(self.pupil1, state='hidden')
        self.canvas.itemconfig(self.pupil2, state='hidden')
        self.after(duration, self.reset_eyes)

    def long_blink(self):
        self.blink(duration=random.randint(1000, 2500))

    def look_around(self):
        dx = random.randint(-10, 10)
        dy = random.randint(-5, 5)
        self.canvas.move(self.pupil1, dx, dy)
        self.canvas.move(self.pupil2, dx, dy)
        self.after(random.randint(700, 1500), self.reset_eyes)

    def stick_tongue(self):
        # Abrir la boca un poco
        self.canvas.delete(self.mouth)
        self.mouth = self.canvas.create_oval(
            self.MOUTH_X1, self.MOUTH_Y, 
            self.MOUTH_X2, self.MOUTH_Y + 10, # Apertura pequeña
            fill="black"
        )
        
        def hide_tongue_and_close_mouth():
            self.canvas.itemconfig(self.tongue, state='hidden')
            self.canvas.delete(self.mouth)
            self.mouth = self.canvas.create_line(self.MOUTH_X1, self.MOUTH_Y, self.MOUTH_X2, self.MOUTH_Y, width=3)

        self.canvas.itemconfig(self.tongue, state='normal')
        self.canvas.lift(self.tongue) # <-- Mueve la lengua al frente
        self.after(random.randint(1000, 2000), hide_tongue_and_close_mouth)

    def concentrate(self):
        # Coordenadas para ojos entrecerrados
        eye1_concentrate_coords = (self.EYE1_COORDS[0], self.EYE1_COORDS[1] + 5, self.EYE1_COORDS[2], self.EYE1_COORDS[3] - 5)
        eye2_concentrate_coords = (self.EYE2_COORDS[0], self.EYE2_COORDS[1] + 5, self.EYE2_COORDS[2], self.EYE2_COORDS[3] - 5)

        self.canvas.coords(self.eye1, *eye1_concentrate_coords)
        self.canvas.coords(self.eye2, *eye2_concentrate_coords)
        self.after(random.randint(1000, 2500), self.reset_eyes)

# Ejemplo de uso
if __name__ == '__main__':
    # Esta parte es solo para pruebas directas del archivo cara.py
    # y no se usará cuando se ejecute desde berraco.py
    import queue
    test_queue = queue.Queue()
    face = MiniFace(send_queue=test_queue)

    def toggle_speaking():
        if face.speaking:
            face.stop_speaking()
            print("Dejó de hablar.")
        else:
            face.start_speaking()
            print("Empezó a hablar.")
    
    def toggle_sleep():
        if face.sleeping:
            face.stop_sleeping()
            print("Se despertó.")
        else:
            face.start_sleeping()
            print("Se durmió.")

    # Añade un botón para probar
    button = tk.Button(face, text="Hablar/Callar", command=toggle_speaking)
    button.pack()

    sleep_button = tk.Button(face, text="Dormir/Despertar", command=toggle_sleep)
    sleep_button.pack()

    face.mainloop()
