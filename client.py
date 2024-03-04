import socket
import pyaudio
import ssl
import sys

context = ssl.create_default_context()
context.load_verify_locations('./rootCA.pem')
client_socket = context.wrap_socket(socket.socket(
    socket.AF_INET, socket.SOCK_STREAM), server_hostname="localhost")

client_socket.connect(("127.0.0.1", 5544))

p = pyaudio.PyAudio()

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 3
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

while True:
    try:
        res = client_socket.recv(1024).decode()
        print(res)
        print("\n")
        sys.stdout.flush()
        x = input("Enter The song to be Played : ")
        client_socket.send(x.encode())
        ch = int(client_socket.recv(1024).decode())
        if ch == 0:
            print("!!! Choose a legal song number !!!")
            continue
        if ch == 1:
            print(" Track !!  ", x, "  !! Playing")
            data = "1"
            while data != "":
                client_socket.send("keepalive".encode())
                data = client_socket.recv(1024)
                stream.write(data)
    except Exception as e:
        print(e)
        break
    except KeyboardInterrupt:
        client_socket.send("exit".encode('utf-8'))
        client_socket.close()
        break

stream.stop_stream()
stream.close()
p.terminate()
