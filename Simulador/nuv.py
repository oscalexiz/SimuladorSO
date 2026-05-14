import tkinter as tk
from tkinter import ttk, simpledialog
import random

# ─── COLORES ─────────────────────────────────────────────────
BG = "#0b0b1a"
PANEL = "#111133"
CYAN = "#00e5ff"
VERDE = "#00ff88"
ROJO = "#ff2255"
AMARILLO = "#ffcc00"
BLANCO = "#e0e0ff"

MAX_MEM = 5
T_BLOQUEADO = 9
QUANTUM_MS = 100
id_counter = 0

# ─── PROCESO ─────────────────────────────────────────────────
class Proceso:
    def __init__(self, reloj):
        global id_counter
        id_counter += 1
        self.pid = id_counter
        self.tme = random.randint(7, 18)
        self.t_restante = self.tme
        self.estado = "nuevo"
        self.resultado = None
        self.t_bloq_rest = 0
        self.t_bloq_total = 0

# ─── SIMULADOR ───────────────────────────────────────────────
class Simulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador FCFS")
        self.root.geometry("1200x700")
        self.root.configure(bg=BG)

        self.cola_nuevos = []
        self.cola_listos = []
        self.cola_bloq = []
        self.terminados = []
        self.cpu = None

        self.reloj = 0
        self.reloj_ms = 0
        self.corriendo = True

        self.crear_ui()
        self.iniciar()

    # ─── UI ──────────────────────────────────────────────────
    def crear_ui(self):

        # reloj arriba
        self.lbl_reloj = tk.Label(self.root,
            text="RELOJ: 0",
            fg=VERDE, bg=BG,
            font=("Consolas", 22, "bold"))
        self.lbl_reloj.pack(pady=10)

        contenedor = tk.Frame(self.root, bg=BG)
        contenedor.pack(fill="both", expand=True)

        # columnas
        self.col1 = tk.Frame(contenedor, bg=BG)
        self.col2 = tk.Frame(contenedor, bg=BG)
        self.col3 = tk.Frame(contenedor, bg=BG)

        self.col1.pack(side="left", expand=True, fill="both", padx=5)
        self.col2.pack(side="left", expand=True, fill="both", padx=5)
        self.col3.pack(side="left", expand=True, fill="both", padx=5)

        # paneles
        self.box_nuevos = self.crear_box(self.col1, "NUEVOS", CYAN)
        self.box_listos = self.crear_box(self.col1, "LISTOS", CYAN)

        self.box_cpu = self.crear_box(self.col2, "EJECUCIÓN", VERDE)

        self.box_bloq = self.crear_box(self.col3, "BLOQUEADOS", AMARILLO)
        self.box_term = self.crear_box(self.col3, "TERMINADOS", ROJO)

    def crear_box(self, parent, titulo, color):
        frame = tk.Frame(parent, bg=PANEL, bd=2, relief="solid")
        frame.pack(fill="both", expand=True, pady=5)

        tk.Label(frame, text=titulo, fg=color, bg=PANEL,
                 font=("Consolas", 11, "bold")).pack()

        text = tk.Text(frame, bg=PANEL, fg=color, height=10, bd=0)
        text.pack(fill="both", expand=True)

        return text

    # ─── INICIO ──────────────────────────────────────────────
    def iniciar(self):
        for _ in range(5):
            self.cola_nuevos.append(Proceso(self.reloj))
        self.admitir()
        self.tick()

    def admitir(self):
        while self.cola_nuevos and len(self.cola_listos) < MAX_MEM:
            p = self.cola_nuevos.pop(0)
            p.estado = "listo"
            self.cola_listos.append(p)

    # ─── TICK ────────────────────────────────────────────────
    def tick(self):

        if not self.corriendo:
            return

        self.reloj += 1
        self.reloj_ms += QUANTUM_MS

        # CPU
        if self.cpu is None and self.cola_listos:
            self.cpu = self.cola_listos.pop(0)

        if self.cpu:
            self.cpu.t_restante -= 1
            if self.cpu.t_restante <= 0:
                self.cpu.estado = "terminado"
                self.cpu.resultado = "OK"
                self.terminados.append(self.cpu)
                self.cpu = None

        self.actualizar_ui()

        # fin
        if not self.cola_listos and not self.cola_nuevos and not self.cpu:
            self.lbl_reloj.config(fg=ROJO)
            self.corriendo = False
            return

        self.root.after(QUANTUM_MS, self.tick)

    # ─── UI UPDATE ───────────────────────────────────────────
    def actualizar_ui(self):

        self.lbl_reloj.config(text=f"RELOJ: {self.reloj}")

        # nuevos
        self.escribir(self.box_nuevos,
            f"Procesos nuevos: {len(self.cola_nuevos)}")

        # listos
        texto = ""
        for p in self.cola_listos:
            texto += f"P{p.pid} TR:{p.t_restante}\n"
        self.escribir(self.box_listos, texto)

        # cpu
        if self.cpu:
            texto = f"P{self.cpu.pid}\nRestante: {self.cpu.t_restante}"
        else:
            texto = "CPU libre"
        self.escribir(self.box_cpu, texto)

        # bloqueados
        texto = ""
        for p in self.cola_bloq:
            texto += f"P{p.pid}\n"
        self.escribir(self.box_bloq, texto)

        # terminados
        texto = ""
        for p in self.terminados:
            texto += f"P{p.pid} OK\n"
        self.escribir(self.box_term, texto)

    def escribir(self, widget, texto):
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, texto)


# ─── MAIN ───────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador(root)
    root.mainloop()