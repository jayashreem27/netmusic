import socket
import pyaudio
import wave
import os
from _thread import *
import ssl

def clientthread(conn, address):
    print("<", address, ">  connected ")
    try:
        # Retrieve the list of available resources
        resource = os.listdir("./resource")
        ss = "\n\n\n\n \t\t Media Player \n"
        for i in range(len(resource)):
            if i % 2 == 0:
                ss += "\n"
            resource[i] = resource[i][:-4]
            ss = ss + "\t" + resource[i] + "\t"
        conn.send(ss.encode())

        # Receive the selected resource from the client
        x = conn.recv(1024).decode()

        # Check if the selected resource exists
        for i in resource:
            if x.lower() == i.lower():
                print("Song found")
                conn.send("1".encode())
                x = i
                break
        else:
            conn.send("0".encode())
            raise ValueError("Selected resource not found")

        # Open the selected resource file
        x = "./resource/" + x + ".wav"
        print(x)

        # Error handling for file operations
        try:
            wf = wave.open(x, 'rb')
        except Exception as file_error:
            print("Error opening audio file:", file_error)
            raise

        p = pyaudio.PyAudio()

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 48000

        # Open a PyAudio stream for audio playback
        try:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            output=True,
                            frames_per_buffer=CHUNK)
        except pyaudio.PyAudioError as audio_error:
            print("PyAudio error:", audio_error)
            raise

        # Stream the audio data to the client
        try:
            data = wf.readframes(CHUNK)
            while data:
                conn.send(data)
                data = wf.readframes(CHUNK)
        except Exception as send_error:
            print("Error sending data:", send_error)
            raise

        # Close the resources after streaming is complete
        finally:
            wf.close()
            stream.stop_stream()
            stream.close()
            p.terminate()
            conn.close()

    except socket.error as socket_error:
        print("Socket error:", socket_error)
        conn.close()
    except IOError as file_error:
        print("File error:", file_error)
        conn.close()
    except pyaudio.PyAudioError as audio_error:
        print("PyAudio error:", audio_error)
        conn.close()
    except Exception as e:
        print("Unexpected error:", e)
        conn.close()

# Create a regular socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set a timeout of 10 seconds for connection acceptance
server_socket.settimeout(10)

# Create an SSL context for the server
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

# Load server SSL certificate and private key
ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Set cipher suites for SSL/TLS
ssl_context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA:!DSS')

# Enable certificate verification and load CA certificates
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.load_verify_locations(cafile="ca.crt")

# Set SSL/TLS protocol versions
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

# Disable session ticket and renegotiation
ssl_context.options |= ssl.OP_NO_TICKET
ssl_context.options |= ssl.OP_NO_RENEGOTIATION

# Wrap the regular socket with SSL/TLS encryption
server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

server_socket.bind(("", 5544))
server_socket.listen(10)

while True:
    try:
        conn, address = server_socket.accept()
        start_new_thread(clientthread, (conn, address))
    except socket.timeout:
        print("Connection timed out. Retrying...")
