import socket
import threading
import wave
import pyaudio
import pickle
import struct

host_name = socket.gethostname()
host_ip = "127.0.0.1"
print(host_ip)
port = 9611


def audio_stream():
    server_socket = socket.socket()
    server_socket.bind((host_ip, (port-1)))

    server_socket.listen(5)
    CHUNK = 1024
    wf = wave.open("./tswift-hitsdiff.wav", 'rb')

    p = pyaudio.PyAudio()
    print('server listening at', (host_ip, (port-1)))

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=CHUNK)

    client_socket, addr = server_socket.accept()

    data = None
    while True:
        if client_socket:
            while True:

                data = wf.readframes(CHUNK)
                a = pickle.dumps(data)
                message = struct.pack("Q", len(a))+a
                client_socket.sendall(message)


t1 = threading.Thread(target=audio_stream, args=())
t1.start()
