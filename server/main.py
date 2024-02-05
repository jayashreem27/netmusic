import socket as sock

HOST = "127.0.0.1"
PORT = 8999

with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()

    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            print(addr, ":", data.decode('utf-8'))
            conn.sendall(data)
