import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AppInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Resgate")
        self.root.geometry("400x500")
        self.root.configure(bg='#f0f0f0')
        
        # Variáveis
        self.saldo = 0  # Saldo inicial
        self.historico = []
        
        self.criar_widgets()
        
    def criar_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Label do saldo (0MRN)
        self.label_saldo = tk.Label(
            main_frame,
            text=f"R$ {self.saldo:.2f}",
            font=('Arial', 48, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        self.label_saldo.pack(pady=20)
        
        # Botão Adicionar Dinheiro
        btn_adicionar = tk.Button(
            main_frame,
            text="Adicionar Dinheiro",
            font=('Arial', 14),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            command=self.adicionar_dinheiro,
            relief='flat',
            cursor='hand2'
        )
        btn_adicionar.pack(pady=10)
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=20)
        
        # Label Histórico
        label_historico = tk.Label(
            main_frame,
            text="Histórico de Resgate",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        label_historico.pack(pady=10)
        
        # Frame para lista de histórico (com scroll)
        historico_frame = tk.Frame(main_frame, bg='#f0f0f0')
        historico_frame.pack(fill='both', expand=True)
        
        # Canvas e Scrollbar
        canvas = tk.Canvas(historico_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(historico_frame, orient='vertical', command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Adicionar histórico inicial (exemplo)
        self.adicionar_historico(
            "João Guilmente",
            100.00,
            "Pix",
            "13:59"
        )
        
    def adicionar_dinheiro(self):
        # Simula adição de dinheiro
        valor = 50.00
        self.saldo += valor
        self.label_saldo.config(text=f"R$ {self.saldo:.2f}")
        
        # Adiciona ao histórico
        agora = datetime.now()
        hora = agora.strftime("%H:%M")
        self.adicionar_historico(
            "Sistema",
            valor,
            "Depósito",
            hora
        )
        
        messagebox.showinfo("Sucesso", f"R$ {valor:.2f} adicionado com sucesso!")
    
    def adicionar_historico(self, nome, valor, metodo, hora):
        # Adiciona ao histórico
        texto = f"{nome} resgatou R$ {valor:.2f} via {metodo} às {hora}"
        
        # Frame para cada item do histórico
        item_frame = tk.Frame(
            self.scrollable_frame,
            bg='white',
            relief='solid',
            bd=1
        )
        item_frame.pack(fill='x', padx=5, pady=5)
        
        # Label do item
        label_item = tk.Label(
            item_frame,
            text=texto,
            font=('Arial', 10),
            bg='white',
            fg='#34495e',
            wraplength=330,
            justify='left'
        )
        label_item.pack(padx=10, pady=8)
        
        # Atualiza scroll
        self.scrollable_frame.update_idletasks()
        
        # Scroll para o final
        canvas = self.scrollable_frame.master
        canvas.yview_moveto(1.0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppInterface(root)
    root.mainloop()