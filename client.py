import socket
from time import sleep

IP = "127.0.0.1"
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)

        while True:
            try:
                client.sendall("newpacket".encode(FORMAT))
                # Receive message from the server
                data = client.recv(SIZE).decode(FORMAT)
                if not data:
                    break

                # Receive and print current time
                print(f"[SERVER] {data}")
                sleep(0.5)

            except KeyboardInterrupt:
                print("\nDisconnecting...")
                client.send(DISCONNECT_MESSAGE.encode(FORMAT))
                break

    finally:
        client.close()


if __name__ == "__main__":
    main()
