import socket
import pyaudio
import wave
import os
import threading
import ssl


def clientthread(insecure_conn, address, context):
    with context.wrap_socket(insecure_conn, server_side=True) as conn:
        print("<", address, ">  connected ")
        while True:
            try:
                resource = os.listdir("./resource")
                ss = "\n\n\n\n \t\t Media Player \n"
                for i in range(len(resource)):
                    if i % 2 == 0:
                        ss += "\n"
                    resource[i] = resource[i][:-4]
                    ss = ss+"\t"+resource[i]+"\t"
                conn.send(ss.encode())
                x = conn.recv(1024).decode()
                for i in resource:
                    if x.lower() == i.lower():
                        print("song found")
                        conn.send("1".encode())
                        x = i
                        break
                else:
                    conn.send("0".encode())
                    continue
                x = "./resource/"+x+".wav"
                print(x)
                wf = wave.open(x, 'rb')

                p = pyaudio.PyAudio()

                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 2
                RATE = 48000

                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                output=True,
                                frames_per_buffer=CHUNK)

                data = 1
                while data:
                    try:
                        message = conn.recv(1024).decode('utf-8')
                        if message == "exit":
                            stream.stop_stream()
                            p.terminate()
                            conn.close()
                            break
                        data = wf.readframes(CHUNK)
                        conn.send(data)
                    except Exception as e:
                        print(e)
                        break
                    except KeyboardInterrupt:
                        break
            except Exception as e:
                print(e)
                break
            except KeyboardInterrupt:
                break


# create a context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="./rootCA.pem", keyfile="./rootCA.key")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 5544))
server_socket.listen()
while True:
    conn, address = server_socket.accept()
    threading.Thread(target=clientthread, args=(
        conn, address, context)).start()
