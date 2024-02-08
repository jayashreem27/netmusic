import socket
import threading
import asyncio

IP = "127.0.0.1"
PORT = 5566
SIZE = 1024
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(SIZE).decode(FORMAT)
            if not msg:
                break
            print(msg)
        except ConnectionResetError:
            print("[ERROR] Connection reset by peer.")
            break


async def send_messages(client_socket):
    while True:
        user_input = input("Enter your message (type '!DISCONNECT' to exit): ")
        client_socket.send(user_input.encode(FORMAT))
        if user_input == DISCONNECT_MESSAGE:
            break


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(send_messages(client))
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt. Disconnecting...")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        client.close()


if __name__ == "__main__":
    main()
