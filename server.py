import socket
import threading
import time

IP = "127.0.0.1"
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        try:
            msg = conn.recv(SIZE).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                print(f"[{addr}] Disconnected")
            else:
                # Send current time to the client
                current_time = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime())
                conn.send(current_time.encode(FORMAT))
        except ConnectionResetError:
            print(f"[{addr}] Connection reset by peer")
            break

    conn.close()


def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


if __name__ == "__main__":
    main()
