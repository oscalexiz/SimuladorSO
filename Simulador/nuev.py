import tkinter as tk
from tkinter import ttk, simpledialog
import random

# ─── PALETA ─────────────────────────────────────────────────────────────────
BG     = "#0a0a12"
PANEL  = "#0f0f1e"
BORDER = "#1a1a3a"
CYAN   = "#00e5ff"
ROJO   = "#ff003c"
VERDE  = "#00ff88"
AMARILLO = "#ffcc00"
MORADO = "#bb86fc"
BLANCO = "#ff00a2"

MAX_MEM = 5
T_BLOQUEADO = 9
QUANTUM_MS = 100
id_counter = 0

# ─── CLASE PROCESO ───────────────────────────────────────────────────────────
class Proceso:
    def __init__(self, reloj_actual):
        global id_counter
        id_counter += 1
        self.pid = id_counter
        self.op1 = random.randint(1, 50)
        self.op2 = random.randint(1, 50)
        self.operador = random.choice(["+", "-", "*", "/", "%"])
        self.tme = random.randint(7, 18)

        self.t_llegada = reloj_actual
        self.t_fin = None
        self.t_retorno = None
        self.t_espera = 0
        self.t_servicio = 0
        self.t_restante = self.tme
        self.t_respuesta = None

        self.estado = "nuevo"
        self.resultado = None
        self.t_bloqueado_rest = 0
        self.t_bloqueado_total = 0

    def calcular(self):
        try:
            if self.operador == "+": return self.op1 + self.op2
            if self.operador == "-": return self.op1 - self.op2
            if self.operador == "*": return self.op1 * self.op2
            if self.operador == "/":
                if self.op2 == 0: return "ERROR"
                return round(self.op1 / self.op2, 2)
            if self.operador == "%":
                if self.op2 == 0: return "ERROR"
                return self.op1 % self.op2
        except:
            return "error"

    def operacion_str(self):
        return f"{self.op1} {self.operador} {self.op2}"

# ─── SIMULADOR ───────────────────────────────────────────────────────────────
class Simulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador FCFS")
        self.root.geometry("900x600")
        self.root.configure(bg=BG)

        self.cola_nuevos = []
        self.cola_listos = []
        self.cola_bloqueados = []
        self.terminados = []
        self.en_ejecucion = None

        self.reloj = 0
        self.reloj_ms = 0
        self.pausado = False
        self.corriendo = False

        self.crear_ui()
        self.bind_keys()
        self.pedir_iniciales()

    def crear_ui(self):
        self.lbl_estado = tk.Label(self.root, text="[ INICIANDO ]",
                                   fg=AMARILLO, bg=BG)
        self.lbl_estado.pack()

        self.lbl_reloj = tk.Label(self.root,
            text="RELOJ: 0 (0 ms)",
            fg=AMARILLO, bg=BG,
            font=("Courier New", 18, "bold"))
        self.lbl_reloj.pack()

        self.text = tk.Text(self.root, bg=PANEL, fg=BLANCO)
        self.text.pack(fill="both", expand=True)

    def bind_keys(self):
        self.root.bind("<e>", self.tecla_E)
        self.root.bind("<w>", self.tecla_W)
        self.root.bind("<p>", self.tecla_P)
        self.root.bind("<c>", self.tecla_C)
        self.root.bind("<n>", self.tecla_N)

    def pedir_iniciales(self):
        n = simpledialog.askinteger("Inicio", "Procesos iniciales:", minvalue=1, maxvalue=10)
        for _ in range(n):
            self.cola_nuevos.append(Proceso(self.reloj))
        self.admitir_procesos()
        self.corriendo = True
        self.tick()

    def admitir_procesos(self):
        en_mem = len(self.cola_listos) + len(self.cola_bloqueados) + (1 if self.en_ejecucion else 0)
        while self.cola_nuevos and en_mem < MAX_MEM:
            p = self.cola_nuevos.pop(0)
            p.estado = "listo"
            self.cola_listos.append(p)
            en_mem += 1

    def tick(self):
        if not self.corriendo:
            return

        if self.pausado:
            self.root.after(QUANTUM_MS, self.tick)
            return

        self.reloj += 1
        self.reloj_ms += QUANTUM_MS

        # bloqueados
        for p in list(self.cola_bloqueados):
            p.t_bloqueado_rest -= 1
            p.t_bloqueado_total += 1
            if p.t_bloqueado_rest <= 0:
                p.estado = "listo"
                self.cola_bloqueados.remove(p)
                self.cola_listos.append(p)

        # espera
        for p in self.cola_listos:
            p.t_espera += 1

        # despacho
        if self.en_ejecucion is None and self.cola_listos:
            self.en_ejecucion = self.cola_listos.pop(0)
            self.en_ejecucion.estado = "ejecutando"

        # ejecución
        if self.en_ejecucion:
            p = self.en_ejecucion
            p.t_servicio += 1
            p.t_restante -= 1

            if p.t_restante <= 0:
                p.resultado = p.calcular()
                p.t_fin = self.reloj
                p.t_retorno = p.t_fin - p.t_llegada
                p.estado = "terminado"
                self.terminados.append(p)
                self.en_ejecucion = None

        self.admitir_procesos()
        self.actualizar_ui()

        # 🔴 VERIFICAR FIN
        todo_hecho = (
            not self.cola_nuevos and
            not self.cola_listos and
            not self.cola_bloqueados and
            self.en_ejecucion is None
        )

        if todo_hecho:
            self.corriendo = False
            self.lbl_estado.config(text="[ SIMULACIÓN TERMINADA ]", fg=ROJO)
            self.lbl_reloj.config(fg=ROJO)  # ← CAMBIA A ROJO
            return

        self.root.after(QUANTUM_MS, self.tick)

    def actualizar_ui(self):
        self.lbl_reloj.config(text=f"RELOJ: {self.reloj} ({self.reloj_ms} ms)")

        texto = "\nLISTOS:\n"
        for p in self.cola_listos:
            texto += f"P{p.pid} Rest:{p.t_restante}\n"

        texto += "\nEJECUCIÓN:\n"
        if self.en_ejecucion:
            p = self.en_ejecucion
            texto += f"P{p.pid} {p.operacion_str()}\n"
        else:
            texto += "CPU libre\n"

        texto += "\nBLOQUEADOS:\n"
        for p in self.cola_bloqueados:
            texto += f"P{p.pid} {p.t_bloqueado_total}\n"

        texto += "\nTERMINADOS:\n"
        for p in self.terminados:
            texto += f"P{p.pid} = {p.resultado}\n"

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, texto)

    # ─── TECLAS ──────────────────────────────────────────────────────────────
    def tecla_E(self, e):
        if self.en_ejecucion:
            p = self.en_ejecucion
            p.estado = "bloqueado"
            p.t_bloqueado_rest = T_BLOQUEADO
            self.cola_bloqueados.append(p)
            self.en_ejecucion = None

    def tecla_W(self, e):
        if self.en_ejecucion:
            p = self.en_ejecucion
            p.resultado = "ERROR"
            p.estado = "terminado"
            self.terminados.append(p)
            self.en_ejecucion = None

    def tecla_P(self, e):
        self.pausado = True

    def tecla_C(self, e):
        self.pausado = False

    def tecla_N(self, e):
        self.cola_nuevos.append(Proceso(self.reloj))

# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador(root)
    root.mainloop()