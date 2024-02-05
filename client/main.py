import socket as sock

HOST = "127.0.0.1"
PORT = 8999

with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        user_data = input("-> ")
        s.sendall(user_data.encode('utf-8'))
        data = s.recv(1024).decode('utf-8')

        print(f"Received data {data}")
