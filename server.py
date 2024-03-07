import socket
import os
import wave
import ssl
import threading

HOST = "0.0.0.0"
PORT = 5544
PACKET_SIZE = 1024
SONGS_DIR = "./resource/"


def client_thread(conn, address, ssl_context):
    # upgrade connection to SSL
    with ssl_context.wrap_socket(conn, server_side=True) as secure_conn:
        print(f"[{address}] connected")

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

            print(f"{address} opened file", song)
            # start transmission loop
            data = " "
            while data:
                # send the next chunk
                data = waveform.readframes(PACKET_SIZE)
                secure_conn.send(data)
                res = secure_conn.recv(PACKET_SIZE).decode()
                if res == "paus":
                    while True:
                        res = secure_conn.recv(PACKET_SIZE).decode()
                        if res == "play":
                            continue
                        else:
                            break
        except ssl.SSLEOFError:
            print(f"[{address}] disconnected")
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            secure_conn.close()


if __name__ == "__main__":
    try:
        # define the SSL socket using the keyfiles
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="./server.crt",
                                keyfile="./server.key")

        # create a socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        print(f"Serving on {(HOST, PORT)}")
        server_socket.listen()
    except Exception as e:
        print(e)

    # always listen for incoming connections
    while True:
        try:
            conn, address = server_socket.accept()
            threading.Thread(target=client_thread,
                             args=(conn, address, context)).start()
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            break
