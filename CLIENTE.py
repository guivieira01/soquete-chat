import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

class ClienteApp:
    def __init__(self, root):
        self.nome_cliente = simpledialog.askstring("Cliente Chat", "Digite seu nome:")
        if not self.nome_cliente:
            self.nome_cliente = "Cliente Desconhecido"

        self.root = root
        self.root.title(f"Cliente Chat ({self.nome_cliente})")

        self.mensagens_texto = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.mensagens_texto.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        self.mensagens_texto.config(state=tk.DISABLED)

        self.campo_mensagem = tk.Entry(root, width=40)
        self.campo_mensagem.grid(row=1, column=0, padx=10, pady=10)

        self.botao_enviar = tk.Button(root, text="Enviar", command=self.enviar_mensagem)
        self.botao_enviar.grid(row=1, column=1, padx=10, pady=10)

        self.lista_clientes = tk.Listbox(root, width=30, height=20)
        self.lista_clientes.grid(row=0, column=2, padx=10, pady=10)

        self.host_servidor = '127.0.0.1'
        self.porta_servidor = 5000
        self.soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soquete_servidor.connect((self.host_servidor, self.porta_servidor))

        self.porta_local = self.iniciar_escuta()

        self.soquete_servidor.send(f"{self.nome_cliente}:{self.porta_local}".encode('utf-8'))

        threading.Thread(target=self.escutar_mensagens, daemon=True).start()
        threading.Thread(target=self.atualizar_lista_clientes, daemon=True).start()

    def iniciar_escuta(self):
        self.soquete_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soquete_local.bind(('127.0.0.1', 0))
        self.soquete_local.listen(5)
        porta_local = self.soquete_local.getsockname()[1]

        def escutar():
            while True:
                conexao, endereco = self.soquete_local.accept()
                threading.Thread(target=self.tratar_conexao, args=(conexao,)).start()

        threading.Thread(target=escutar, daemon=True).start()
        return porta_local

    def tratar_conexao(self, conexao):
        while True:
            try:
                mensagem = conexao.recv(1024).decode('utf-8')
                if mensagem:
                    self.exibir_mensagem(mensagem)
                else:
                    break
            except:
                break
        conexao.close()

    def exibir_mensagem(self, mensagem):
        self.mensagens_texto.config(state=tk.NORMAL)
        self.mensagens_texto.insert(tk.END, mensagem + "\n")
        self.mensagens_texto.config(state=tk.DISABLED)

    def enviar_mensagem(self):
        mensagem = self.campo_mensagem.get()
        if mensagem:
            destino = self.lista_clientes.get(tk.ACTIVE)
            if destino == "Todos":
                for i in range(1, self.lista_clientes.size()):
                    self.enviar_para_cliente(self.lista_clientes.get(i), mensagem)
            elif destino:
                self.enviar_para_cliente(destino, mensagem)
            self.campo_mensagem.delete(0, tk.END)

    def enviar_para_cliente(self, destino, mensagem):
        try:
            nome_destino, destino_ip_porta = destino.split(" - ")
            destino_host, destino_porta = destino_ip_porta.split(":")
            soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soquete_cliente.connect((destino_host, int(destino_porta)))
            soquete_cliente.send(f"{self.nome_cliente}: {mensagem}".encode('utf-8'))
            soquete_cliente.close()
            self.exibir_mensagem(f"Você ({nome_destino}): {mensagem}")
        except Exception as e:
            self.exibir_mensagem(f"Erro ao enviar mensagem para {nome_destino}: {e}")

    def escutar_mensagens(self):
        while True:
            try:
                threading.Event().wait(1)
            except Exception as e:
                self.exibir_mensagem(f"Erro ao escutar mensagens: {e}")

    def atualizar_lista_clientes(self):
        while True:
            try:
                lista_clientes = self.listar_clientes()
                self.lista_clientes.delete(0, tk.END)
                self.lista_clientes.insert(tk.END, "Todos")
                for cliente in lista_clientes:
                    self.lista_clientes.insert(tk.END, cliente)
                threading.Event().wait(5)
            except Exception as e:
                self.exibir_mensagem(f"Erro ao atualizar lista de clientes: {e}")

    def listar_clientes(self):
        try:
            self.soquete_servidor.send("1".encode('utf-8'))
            resposta = self.soquete_servidor.recv(1024).decode('utf-8')
            return resposta.split(";") if resposta else []
        except Exception as e:
            self.exibir_mensagem(f"Erro ao listar clientes: {e}")
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteApp(root)
    root.mainloop()
