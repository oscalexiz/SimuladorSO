import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# ===============================
# COLORES CYBERPUNK
# ===============================

BG = "#0f0f1a"
PANEL = "#14142b"
CYAN = "#00f5ff"
ROJO = "#ff003c"
VERDE = "#00ff9f"

# ===============================
# CLASE PROCESO
# ===============================

class Proceso:
    def __init__(self, nombre, operador, op1, op2, tme, id_prog):
        self.nombre = nombre
        self.operador = operador
        self.op1 = op1
        self.op2 = op2
        self.tme = tme
        self.id_prog = id_prog
        self.resultado = None
        self.error = False

    def calcular(self):
        try:
            if self.operador == "+": return self.op1 + self.op2
            if self.operador == "-": return self.op1 - self.op2
            if self.operador == "*": return self.op1 * self.op2
            if self.operador == "/": return self.op1 / self.op2
            if self.operador == "%": return self.op1 % self.op2
            if self.operador == "^": return self.op1 ** self.op2
        except:
            return "Error"

# ===============================
# SIMULADOR
# ===============================

class Simulador:

    def __init__(self, root):
        self.root = root
        self.root.title("Proceso")
        self.root.geometry("1350x720")
        self.root.configure(bg=BG)

        self.N = None
        self.procesos = []
        self.lotes = []
        self.terminados = []
        self.reloj_global = 0

        self.proceso_actual = None
        self.error_forzado = False

        self.crear_ui()
        self.pedir_N()

        self.root.bind("i", self.interrumpir)
        self.root.bind("e", self.forzar_error)

    # ===============================
    # PEDIR N
    # ===============================

    def pedir_N(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Cantidad de Procesos")
        ventana.geometry("300x150")
        ventana.configure(bg=PANEL)

        tk.Label(ventana, text="¿Cuántos procesos desea capturar?",
                 bg=PANEL, fg=CYAN).pack(pady=10)

        entry = tk.Entry(ventana)
        entry.pack(pady=5)

        def confirmar():
            try:
                valor = int(entry.get())
                if valor > 0:
                    self.N = valor
                    self.label_contador.config(text=f"0 / {self.N}")
                    ventana.destroy()
                else:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Ingrese número mayor a 0")

        tk.Button(ventana, text="Confirmar", bg=CYAN,
                  command=confirmar).pack(pady=10)

        self.root.wait_window(ventana)

    # ===============================
    # INTERFAZ
    # ===============================

    def crear_ui(self):

        fuente_titulo = ("Consolas", 14, "bold")

        frame_izq = tk.Frame(self.root, bg=PANEL)
        frame_izq.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(frame_izq, text="CAPTURA", bg=PANEL, fg=CYAN, font=fuente_titulo).pack(pady=10)

        labels = ["Nombre", "Operando 1", "Operador (+ - * / % ^)",
                  "Operando 2", "TME", "ID"]

        self.entries = []

        for texto in labels:
            tk.Label(frame_izq, text=texto, bg=PANEL, fg=CYAN).pack()
            entry = tk.Entry(frame_izq, bg=BG, fg=CYAN)
            entry.pack(pady=5)
            self.entries.append(entry)

        tk.Button(frame_izq, text="AGREGAR", bg=CYAN,
                  command=self.agregar_proceso).pack(pady=10)

        self.btn_ejecutar = tk.Button(frame_izq, text="EJECUTAR", bg=ROJO,
                                      command=self.iniciar)
        self.btn_ejecutar.pack(pady=10)

        self.label_contador = tk.Label(frame_izq, text="0 / 0",
                                       bg=PANEL, fg=VERDE)
        self.label_contador.pack(pady=10)

        # CENTRO
        frame_centro = tk.Frame(self.root, bg=PANEL)
        frame_centro.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.label_pendientes = tk.Label(frame_centro, text="Lotes Pendientes: 0",
                                         bg=PANEL, fg=ROJO, font=fuente_titulo)
        self.label_pendientes.pack(pady=10)

        self.label_proceso = tk.Label(frame_centro, text="", bg=PANEL, fg=VERDE)
        self.label_proceso.pack(pady=10)

        self.label_tiempos = tk.Label(frame_centro, text="", bg=PANEL, fg=VERDE)
        self.label_tiempos.pack()

        self.progress = ttk.Progressbar(frame_centro, length=400)
        self.progress.pack(pady=10)

        # 🔥 NUEVO: INFO DEL LOTE ACTUAL
        self.label_lote_info = tk.Label(frame_centro, text="", bg=PANEL, fg=CYAN, justify="left")
        self.label_lote_info.pack(pady=10)

        # DERECHO
        frame_der = tk.Frame(self.root, bg=PANEL)
        frame_der.pack(side="right", fill="y", padx=10, pady=10)

        self.text_terminados = tk.Text(frame_der, height=25, bg=BG, fg=ROJO)
        self.text_terminados.pack()

        self.label_reloj = tk.Label(frame_der, text="Reloj Global: 0",
                                    bg=PANEL, fg=VERDE, font=fuente_titulo)
        self.label_reloj.pack(pady=20)

    # ===============================
    # AGREGAR
    # ===============================

    def agregar_proceso(self):

        if len(self.procesos) >= self.N:
            messagebox.showinfo("Límite", "Ya capturó todos los procesos")
            return

        try:
            nombre = self.entries[0].get()
            op1 = float(self.entries[1].get())
            operador = self.entries[2].get()
            op2 = float(self.entries[3].get())
            tme = int(self.entries[4].get())
            id_prog = self.entries[5].get()

            if operador not in ["+", "-", "*", "/", "%", "^"]:
                raise ValueError

            for p in self.procesos:
                if p.id_prog == id_prog:
                    raise ValueError

        except:
            messagebox.showerror("Error", "Datos inválidos o ID repetido")
            return

        self.procesos.append(Proceso(nombre, operador, op1, op2, tme, id_prog))
        self.label_contador.config(text=f"{len(self.procesos)} / {self.N}")

        for e in self.entries:
            e.delete(0, tk.END)

    # ===============================
    # EJECUCIÓN
    # ===============================

    def iniciar(self):
        if len(self.procesos) != self.N:
            messagebox.showerror("Error", "Debe capturar todos los procesos")
            return

        self.lotes = [self.procesos[i:i+4] for i in range(0, len(self.procesos), 4)]
        self.ejecutar_lote(0, 0)

    def ejecutar_lote(self, i_lote, i_proc):

        if i_lote >= len(self.lotes):
            self.text_terminados.insert(tk.END, "\n*** TODOS LOS PROCESOS FINALIZADOS ***\n")
            return

        lote = self.lotes[i_lote]

        # 🔥 actualizar lotes pendientes
        pendientes = len(self.lotes) - i_lote - 1
        self.label_pendientes.config(text=f"Lotes Pendientes: {pendientes}")

        if i_proc >= len(lote):
            self.ejecutar_lote(i_lote+1, 0)
            return

        self.proceso_actual = lote[i_proc]
        self.ejecutar_proceso(i_lote, i_proc, 0)

    def ejecutar_proceso(self, i_lote, i_proc, tiempo):

        proceso = self.proceso_actual

        if self.error_forzado:
            proceso.resultado = "Error"
            self.text_terminados.insert(tk.END, f"ID:{proceso.id_prog} ERROR\n")
            self.error_forzado = False
            self.ejecutar_lote(i_lote, i_proc+1)
            return

        if tiempo < proceso.tme:

            self.label_proceso.config(
                text=f"{proceso.nombre} | ID:{proceso.id_prog}\n"
                     f"{proceso.op1} {proceso.operador} {proceso.op2}"
            )

            self.label_tiempos.config(
                text=f"Transcurrido:{tiempo+1}  Restante:{proceso.tme-(tiempo+1)}"
            )

            # 🔥 INFO DETALLADA DEL LOTE
            self.label_lote_info.config(
                text=f"=== LOTE {i_lote+1} ===\n"
                     f"Nombre: {proceso.nombre}\n"
                     f"ID: {proceso.id_prog}\n"
                     f"Operación: {proceso.op1} {proceso.operador} {proceso.op2}\n"
                     f"Transcurrido: {tiempo+1}\n"
                     f"Restante: {proceso.tme-(tiempo+1)}"
            )

            self.progress["value"] = (tiempo+1) / proceso.tme * 100

            self.label_reloj.config(text=f"Reloj Global: {self.reloj_global}")
            self.reloj_global += 1

            self.root.after(1000, self.ejecutar_proceso,
                            i_lote, i_proc, tiempo+1)

        else:
            proceso.resultado = proceso.calcular()
            self.text_terminados.insert(
                tk.END,
                f"ID:{proceso.id_prog} Resultado:{proceso.resultado}\n"
            )
            self.progress["value"] = 0
            self.ejecutar_lote(i_lote, i_proc+1)

    # ===============================
    # INTERRUPCIONES
    # ===============================

    def interrumpir(self, event):
        if self.proceso_actual:
            self.lotes.append([self.proceso_actual])
            self.text_terminados.insert(tk.END, f"ID:{self.proceso_actual.id_prog} INTERRUMPIDO\n")

    def forzar_error(self, event):
        self.error_forzado = True


if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador(root)
    root.mainloop()