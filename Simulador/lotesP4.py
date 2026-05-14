import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random

BG = "#0f0f1a"
PANEL = "#14142b"
CYAN = "#00f5ff"
ROJO = "#ff003c"
VERDE = "#00ff9f"

# PROCESO
class Proceso:
    def __init__(self, idp):
        self.id = idp
        self.op1 = random.randint(1,50)
        self.op2 = random.randint(1,50)
        self.op = random.choice(["+","-","*","/","%"])
        self.tme = random.randint(7,18)

        self.t_rest = self.tme
        self.t_serv = 0
        self.t_bloq = 0

        self.llegada = None
        self.final = None
        self.retorno = None
        self.respuesta = None
        self.espera = 0
        self.atendido = False

    def calcular(self):
        try:
            if self.op == "+": return self.op1 + self.op2
            if self.op == "-": return self.op1 - self.op2
            if self.op == "*": return self.op1 * self.op2
            if self.op == "/": return round(self.op1/self.op2,2)
            if self.op == "%": return self.op1 % self.op2
        except:
            return "ERROR"

# SIMULADOR
class Simulador:

    def __init__(self, root):
        self.root = root
        self.root.title("FCFS")
        self.root.geometry("1350x720")
        self.root.configure(bg=BG)

        self.reloj = 0
        self.pausado = False
        self.error = False

        self.nuevos = []
        self.listos = []
        self.bloq = []
        self.term = []
        self.ejec = None

        self.crear_ui()
        self.pedir_N()

        self.root.bind("i", self.interrumpir)
        self.root.bind("e", self.error_proceso)
        self.root.bind("p", self.pausa)
        self.root.bind("c", self.continuar)

# PEDIR N
    def pedir_N(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Procesos")
        ventana.geometry("300x150")
        ventana.configure(bg=PANEL)

        tk.Label(ventana, text="¿Cuántos procesos?",
                 bg=PANEL, fg=CYAN).pack(pady=10)

        entry = tk.Entry(ventana)
        entry.pack()

        def confirmar():
            try:
                n = int(entry.get())
                if n <= 0: raise ValueError

                for i in range(n):
                    self.nuevos.append(Proceso(i+1))

                ventana.destroy()
                self.ciclo()

            except:
                messagebox.showerror("Error","Número inválido")

        tk.Button(ventana,text="Confirmar",bg=CYAN,command=confirmar).pack(pady=10)

        self.root.wait_window(ventana)

# UI 
    def crear_ui(self):

        fuente = ("Consolas", 14, "bold")

        # IZQ
        frame_izq = tk.Frame(self.root, bg=PANEL)
        frame_izq.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(frame_izq,text="ESTADOS",bg=PANEL,fg=CYAN,font=fuente).pack()

        self.label_nuevos = tk.Label(frame_izq,bg=PANEL,fg=CYAN)
        self.label_nuevos.pack()

        self.text_listos = tk.Text(frame_izq,bg=BG,fg=CYAN,height=20)
        self.text_listos.pack()

        # CENTRO
        frame_centro = tk.Frame(self.root,bg=PANEL)
        frame_centro.pack(side="left",expand=True,fill="both",padx=10,pady=10)

        self.label_proceso = tk.Label(frame_centro,bg=PANEL,fg=VERDE)
        self.label_proceso.pack(pady=10)

        self.label_tiempos = tk.Label(frame_centro,bg=PANEL,fg=VERDE)
        self.label_tiempos.pack()

        self.progress = ttk.Progressbar(frame_centro,length=400)
        self.progress.pack(pady=10)

        self.label_bloq = tk.Label(frame_centro,bg=PANEL,fg=ROJO)
        self.label_bloq.pack(pady=10)

        # DERECHA
        frame_der = tk.Frame(self.root,bg=PANEL)
        frame_der.pack(side="right",fill="y",padx=10,pady=10)

        self.text_terminados = tk.Text(frame_der,bg=BG,fg=ROJO)
        self.text_terminados.pack()

        self.label_reloj = tk.Label(frame_der,bg=PANEL,fg=VERDE,font=fuente)
        self.label_reloj.pack()

# CICLO FCFS
    def ciclo(self):

        if self.pausado:
            self.root.after(500,self.ciclo)
            return

        self.reloj += 1

        # admitir max 3
        while len(self.listos)+len(self.bloq)+(1 if self.ejec else 0) < 3 and self.nuevos:
            p = self.nuevos.pop(0)
            p.llegada = self.reloj
            self.listos.append(p)

        # bloqueados
        for p in self.bloq[:]:
            p.t_bloq += 1
            if p.t_bloq == 10:
                self.bloq.remove(p)
                self.listos.append(p)

        # ejecución
        if not self.ejec and self.listos:
            self.ejec = self.listos.pop(0)
            if not self.ejec.atendido:
                self.ejec.respuesta = self.reloj - self.ejec.llegada
                self.ejec.atendido = True

        if self.ejec:

            if self.error:
                self.ejec.final = self.reloj
                self.term.append((self.ejec,"ERROR"))
                self.ejec = None
                self.error = False

            else:
                self.ejec.t_rest -= 1
                self.ejec.t_serv += 1

                if self.ejec.t_rest == 0:
                    self.ejec.final = self.reloj
                    res = self.ejec.calcular()
                    self.term.append((self.ejec,res))
                    self.ejec = None

        self.actualizar()

        if not self.nuevos and not self.listos and not self.bloq and not self.ejec:
            self.final()
            return

        self.root.after(1000,self.ciclo)

# ACTUALIZAR UI
    def actualizar(self):

        self.label_nuevos.config(text=f"Nuevos: {len(self.nuevos)}")

        self.text_listos.delete("1.0",tk.END)
        for p in self.listos:
            self.text_listos.insert(tk.END,f"ID:{p.id} TME:{p.tme} TR:{p.t_rest}\n")

        if self.ejec:
            p = self.ejec
            self.label_proceso.config(text=f"ID:{p.id} {p.op1}{p.op}{p.op2}")
            self.label_tiempos.config(text=f"Trans:{p.t_serv} Rest:{p.t_rest}")
            self.progress["value"] = (p.t_serv/p.tme)*100

        texto = ""
        for p in self.bloq:
            texto += f"ID:{p.id} TB:{p.t_bloq}\n"
        self.label_bloq.config(text=texto)

        self.label_reloj.config(text=f"Reloj: {self.reloj}")

        self.text_terminados.delete("1.0",tk.END)
        for p,res in self.term:
            self.text_terminados.insert(tk.END,f"ID:{p.id} = {res}\n")

# FINAL
    def final(self):
        self.text_terminados.insert(tk.END,"\n--- TIEMPOS ---\n")
        for p,res in self.term:
            p.retorno = p.final - p.llegada
            p.espera = p.retorno - p.t_serv

            self.text_terminados.insert(
                tk.END,
                f"ID:{p.id} L:{p.llegada} F:{p.final} R:{p.retorno} "
                f"Resp:{p.respuesta} Esp:{p.espera} Serv:{p.t_serv}\n"
            )

# TECLAS
    def interrumpir(self,event):
        if self.ejec:
            self.ejec.t_bloq = 0
            self.bloq.append(self.ejec)
            self.ejec = None

    def error_proceso(self,event):
        self.error = True

    def pausa(self,event):
        self.pausado = True

    def continuar(self,event):
        self.pausado = False

# MAIN
if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador(root)
    root.mainloop()