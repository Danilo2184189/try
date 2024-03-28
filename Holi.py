import tkinter as tk
from datetime import timedelta, datetime

class ContadorApp:
    def __init__(self, master):
        self.master = master
        master.title("Motivación Millonaria")
        master.configure(bg='#000000')

        self.customFont = "Poppins"

        self.valores_iniciales = {'trabajo': timedelta(minutes=90), 'descanso': timedelta(minutes=30)}
        
        self.inicio_frame = tk.Frame(master, bg='#000000')
        self.inicio_frame.pack(expand=True, fill='both')

        self.main_frame = tk.Frame(master, bg='#000000')
        self.boton_inicio = tk.Button(self.inicio_frame, text="Supera tus límites cada día.", command=self.iniciar_contadores, font=(self.customFont, 32), bg='#007bff', fg='white')
        self.boton_inicio.pack(pady=20)

        self.estado = "pausa"
        self.resetear_contadores()

        self.titulo_label = tk.Label(self.main_frame, text="Lo único imposible es aquello que no intentas", font=(self.customFont, 16), bg='#000000', fg='#f8f9fa')
        self.titulo_label.pack(pady=(10,0))

        self.label = tk.Label(self.main_frame, text="El éxito llega para aquellos que \n están demasiado ocupados buscándolo.\n- Henry David Thoreau", font=(self.customFont, 24), bg='#000000', fg='#f8f9fa')
        self.label.pack(pady=20)

        self.boton_trabajo = tk.Button(self.main_frame, text="Un paso más cerca del Exito", command=self.iniciar_trabajo, font=(self.customFont, 14), bg='#6c757d', fg='white')
        self.boton_trabajo.pack(side=tk.LEFT, padx=10, pady=20, expand=True)

        self.boton_descanso = tk.Button(self.main_frame, text="Recuperar Fuerzas", command=self.iniciar_descanso, font=(self.customFont, 14), bg='#17a2b8', fg='white')
        self.boton_descanso.pack(side=tk.LEFT, padx=10, pady=20, expand=True)
        
        self.boton_reinicio = tk.Button(self.main_frame, text="Reiniciar Contadores", command=self.resetear_contadores, font=(self.customFont, 14), bg='#dc3545', fg='white')
        self.boton_reinicio.pack(side=tk.LEFT, padx=10, pady=20, expand=True)

    def iniciar_contadores(self):
        self.inicio_frame.pack_forget()
        self.main_frame.pack(expand=True, fill='both')
        self.actualizar_tiempo()

    def actualizar_tiempo(self):
        ahora = datetime.now()
        if self.estado != "pausa":
            diferencia = ahora - self.ultimo_clic
            self.ultimo_clic = ahora

            if self.estado == "trabajo":
                self.tiempo_trabajo -= diferencia
                if self.tiempo_trabajo.total_seconds() <= 0:
                    self.estado = "descanso"
                    self.tiempo_trabajo = self.valores_iniciales['trabajo']
                    self.iniciar_descanso()
            elif self.estado == "descanso":
                self.tiempo_descanso -= diferencia
                if self.tiempo_descanso.total_seconds() <= 0:
                    self.estado = "trabajo"
                    self.tiempo_descanso = self.valores_iniciales['descanso']
                    self.iniciar_trabajo()

        self.label.config(text=self.formato_tiempo())
        self.master.after(1000, self.actualizar_tiempo)

    def formato_tiempo(self):
        if self.estado == "trabajo":
            tiempo = self.tiempo_trabajo
        elif self.estado == "descanso":
            tiempo = self.tiempo_descanso
        else:
            return "El éxito llega para aquellos que \n están demasiado ocupados buscándolo.\n- Henry David Thoreau"
        
        horas, rem = divmod(tiempo.total_seconds(), 3600)
        minutos, segundos = divmod(rem, 60)
        return '{:02}:{:02}:{:02}'.format(int(horas), int(minutos), int(segundos))

    def resetear_contadores(self):
        self.tiempo_trabajo = self.valores_iniciales['trabajo']
        self.tiempo_descanso = self.valores_iniciales['descanso']
        self.ultimo_clic = datetime.now()
        if self.estado != 'pausa':
            self.estado = 'pausa'
            self.label.config(text="¡Prepárate para ser millonario!")

    def iniciar_trabajo(self):
        if self.estado != "trabajo":
            self.estado = "trabajo"
            self.ultimo_clic = datetime.now()
            self.actualizar_tiempo()

    def iniciar_descanso(self):
        if self.estado != "descanso":
            self.estado = "descanso"
            self.ultimo_clic = datetime.now()
            self.actualizar_tiempo()

root = tk.Tk()
app = ContadorApp(root)
root.mainloop()
