import socket

HOST, PORT = 'localhost', 1337
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while data := conn.recv(1024):
                conn.sendall(data.swapcase())