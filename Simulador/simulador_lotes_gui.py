import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random

BG = "#0f0f1a"
PANEL = "#14142b"
CYAN = "#00f5ff"
ROJO = "#ff003c"
VERDE = "#00ff9f"

# ===============================
# PROCESO
# ===============================
class Proceso:
    def __init__(self, id_prog):
        self.id_prog = id_prog
        self.op1 = random.randint(1, 50)
        self.op2 = random.randint(1, 50)
        self.operador = random.choice(["+", "-", "*", "/", "%"])
        self.tme = random.randint(7, 18)

        self.t_restante = self.tme
        self.t_transcurrido = 0
        self.resultado = None

    def calcular(self):
        try:
            if self.operador == "+": return self.op1 + self.op2
            if self.operador == "-": return self.op1 - self.op2
            if self.operador == "*": return self.op1 * self.op2
            if self.operador == "/": return self.op1 / self.op2
            if self.operador == "%": return self.op1 % self.op2
        except:
            return "ERROR"

# ===============================
# SIMULADOR
# ===============================
class Simulador:

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Lotes")
        self.root.geometry("1200x700")
        self.root.configure(bg=BG)

        self.procesos = []
        self.lotes = []
        self.lote_actual = []

        self.reloj = 0
        self.proceso_actual = None
        self.pausado = False
        self.error = False

        self.crear_ui()
        self.pedir_N()

        self.root.bind("i", self.interrumpir)
        self.root.bind("e", self.error_proceso)
        self.root.bind("p", self.pausar)
        self.root.bind("c", self.continuar)

    # ===============================
    # GENERAR PROCESOS
    # ===============================
    def pedir_N(self):
        respuesta = simpledialog.askstring("Procesos", "¿Cuántos procesos?")

        if respuesta is None:
            self.root.destroy()
            return

        try:
            n = int(respuesta)
            if n <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Ingrese un número válido")
            self.pedir_N()
            return

        self.procesos = [Proceso(i+1) for i in range(n)]
        self.lotes = [self.procesos[i:i+3] for i in range(0, len(self.procesos), 3)]
        self.ejecutar_lote(0)

    # ===============================
    # UI (3 COLUMNAS)
    # ===============================
    def crear_ui(self):

        contenedor = tk.Frame(self.root, bg=BG)
        contenedor.pack(fill="both", expand=True)

        # IZQUIERDA → ESPERA
        frame_izq = tk.Frame(contenedor, bg=PANEL, width=300)
        frame_izq.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(frame_izq, text="EN ESPERA", fg=CYAN, bg=PANEL,
                 font=("Consolas", 12, "bold")).pack()

        self.text_espera = tk.Text(frame_izq, bg=BG, fg=CYAN)
        self.text_espera.pack(fill="both", expand=True)

        # CENTRO → EJECUCIÓN
        frame_centro = tk.Frame(contenedor, bg=PANEL)
        frame_centro.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.label_lotes = tk.Label(frame_centro, fg=ROJO, bg=PANEL,
                                   font=("Consolas", 12, "bold"))
        self.label_lotes.pack()

        self.label_ejecucion = tk.Label(frame_centro, fg=VERDE, bg=PANEL,
                                       font=("Consolas", 11))
        self.label_ejecucion.pack(pady=10)

        self.progress = ttk.Progressbar(frame_centro, length=400)
        self.progress.pack(pady=10)

        self.label_reloj = tk.Label(frame_centro, fg=VERDE, bg=PANEL,
                                   font=("Consolas", 12, "bold"))
        self.label_reloj.pack(pady=10)

        # DERECHA → TERMINADOS
        frame_der = tk.Frame(contenedor, bg=PANEL, width=350)
        frame_der.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(frame_der, text="TERMINADOS", fg=ROJO, bg=PANEL,
                 font=("Consolas", 12, "bold")).pack()

        self.text_terminados = tk.Text(frame_der, bg=BG, fg=ROJO)
        self.text_terminados.pack(fill="both", expand=True)

    # ===============================
    # EJECUCIÓN
    # ===============================
    def ejecutar_lote(self, index):
        if index >= len(self.lotes):
            self.label_ejecucion.config(text="*** TERMINADO ***")
            return

        self.lote_actual = self.lotes[index]
        self.label_lotes.config(text=f"Lotes pendientes: {len(self.lotes)-index-1}")
        self.ejecutar_proceso(0, index)

    def ejecutar_proceso(self, i, lote_index):

        if i >= len(self.lote_actual):
            self.ejecutar_lote(lote_index+1)
            return

        self.proceso_actual = self.lote_actual.pop(i)
        self.actualizar_espera()
        self.ciclo(lote_index)

    def ciclo(self, lote_index):

        if self.pausado:
            self.root.after(500, self.ciclo, lote_index)
            return

        p = self.proceso_actual

        if self.error:
            self.text_terminados.insert(tk.END,
                f"ID:{p.id_prog} {p.op1}{p.operador}{p.op2} = ERROR\n")
            self.error = False
            self.ejecutar_proceso(0, lote_index)
            return

        if p.t_restante > 0:

            p.t_transcurrido += 1
            p.t_restante -= 1

            self.label_ejecucion.config(
                text=f"ID:{p.id_prog} | {p.op1}{p.operador}{p.op2}\n"
                     f"Transcurrido:{p.t_transcurrido}  Restante:{p.t_restante}"
            )

            self.progress["value"] = (p.t_transcurrido/p.tme)*100

            self.reloj += 1
            self.label_reloj.config(text=f"Reloj: {self.reloj}")

            self.root.after(1000, self.ciclo, lote_index)

        else:
            res = p.calcular()
            self.text_terminados.insert(tk.END,
                f"ID:{p.id_prog} {p.op1}{p.operador}{p.op2} = {res}\n")

            self.progress["value"] = 0
            self.ejecutar_proceso(0, lote_index)

    # ===============================
    # ESPERA LIMPIA
    # ===============================
    def actualizar_espera(self):

        self.text_espera.delete("1.0", tk.END)

        self.text_espera.insert(tk.END, "ID | TME | RESTANTE\n")
        self.text_espera.insert(tk.END, "-"*25 + "\n")

        for p in self.lote_actual:
            if p.t_restante > 0:
                self.text_espera.insert(
                    tk.END,
                    f"{p.id_prog}   | {p.tme}   | {p.t_restante}\n"
                )

    # ===============================
    # TECLAS
    # ===============================
    def interrumpir(self, event):
        if self.proceso_actual:
            self.lote_actual.append(self.proceso_actual)
            self.text_terminados.insert(tk.END,
                f"ID:{self.proceso_actual.id_prog} INTERRUMPIDO\n")
            self.ejecutar_proceso(0, self.lotes.index(self.lote_actual))

    def error_proceso(self, event):
        self.error = True

    def pausar(self, event):
        self.pausado = True

    def continuar(self, event):
        self.pausado = False

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador(root)
    root.mainloop()