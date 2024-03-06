import socket
import os
import wave
import ssl
import threading

HOST = "127.0.0.1"
PORT = 5544
PACKET_SIZE = 1024
SONGS_DIR = "./resource/"


def client_thread(conn, address, ssl_context):
    # upgrade connection to SSL
    with ssl_context.wrap_socket(conn, server_side=True) as secure_conn:
        print("[", address, "] connected")

        # parse the files available and send
        files = os.listdir(SONGS_DIR)
        files_data = ",".join(files)
        secure_conn.send(files_data.encode())
        try:
            # receive client response containing file name
            filename = secure_conn.recv(PACKET_SIZE).decode()
            for file in files:
                if filename in file:
                    secure_conn.send("Accepted".encode())
                    break
            else:
                secure_conn.send("Rejected".encode())
                secure_conn.close()
                return None

            # open wave file to play
            song = SONGS_DIR + filename
            waveform = wave.open(song, 'rb')

            print("Opened file", song)
            # start transmission loop
            data = " "
            while data:
                # send the next chunk
                data = waveform.readframes(PACKET_SIZE)
                secure_conn.send(data)
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            secure_conn.close()


if __name__ == "__main__":
    # define the SSL socket using the keyfiles
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="./rootCA.pem", keyfile="./rootCA.key")

    # create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    # always listen
    while True:
        conn, address = server_socket.accept()
        threading.Thread(target=client_thread, args=(
            conn, address, context)).start()
