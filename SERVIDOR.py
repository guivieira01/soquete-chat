import socket
import threading

host = '127.0.0.1'
porta = 5000
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)
soquete.listen()

clientes_conectados = []

def processar(conexao, cliente):
    global clientes_conectados
    try:
        dados_cliente = conexao.recv(1024).decode('utf-8')
        nome_cliente, porta_cliente = dados_cliente.split(":")
        clientes_conectados.append((nome_cliente, cliente[0], porta_cliente))
        print(f"Cliente {nome_cliente} conectado")

        while True:
            mensagem = conexao.recv(1024).decode('utf-8')
            if mensagem == "1":
                lista_clientes = ";".join(
                    [f"{c[0]} - {c[1]}:{c[2]}" for c in clientes_conectados 
                     if c[1] != cliente[0] or c[2] != porta_cliente]
                )
                conexao.send(lista_clientes.encode('utf-8'))

            elif mensagem:
                for c in clientes_conectados:
                    if c[1] != cliente[0] or c[2] != porta_cliente:
                        try:
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.connect((c[1], int(c[2])))
                                s.send(f"{nome_cliente}: {mensagem}".encode('utf-8'))
                        except Exception as e:
                            print(f"Erro ao enviar mensagem para {c[0]}: {e}")

    except Exception as e:
        print(f"Erro ao tratar cliente: {e}")

    finally:
        clientes_conectados = [c for c in clientes_conectados 
                               if c[1] != cliente[0] or c[2] != porta_cliente]
        conexao.close()

print("Servidor aguardando conexões...")

while True:
    conexao, cliente = soquete.accept()
    print(f"Conectado por {cliente[0]}:{cliente[1]}")
    threading.Thread(target=processar, args=(conexao, cliente)).start()
