import socket
import pyaudio
import ssl
import threading
import queue
import time

HOSTNAME = "localhost"
HOST = "127.0.0.1"
PORT = 5544
PACKET_SIZE = 1024


def playback_thread(queue, client_socket, audio, stream):
    # Start recv cycle
    data = " "
    main_message = ""
    while data:
        try:
            if not queue.empty():
                main_message = queue.get()
            else:
                main_message = ""
            data = client_socket.recv(PACKET_SIZE)
            stream.write(data)
            if main_message == "pause":
                client_socket.send("paus".encode())
                stream.stop_stream()
                while queue.empty():
                    time.sleep(0.01)
                main_message = queue.get()
                if main_message == "play":
                    client_socket.send("play".encode())
                    stream.start_stream()
                if main_message == "stop":
                    client_socket.send("stop".encode())
                    break
            else:
                client_socket.send("live".encode())
                time.sleep(0.001)
        except Exception as e:
            print(e)
            break
        except KeyboardInterrupt:
            break


def main():
    # Define an SSL context and verify hostname
    context = ssl.create_default_context()
    context.load_verify_locations("./rootCA.pem")

    # Start PyAudio for music playback
    print("You may see some audio initialization text below. This is normal.")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=48000,
                        output=True,
                        frames_per_buffer=PACKET_SIZE)
    print("Audio Initialization ended\n\n")

    # Main loop
    while True:
        try:
            # Create and connect socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket = context.wrap_socket(sock, server_hostname=HOSTNAME)
            client_socket.connect((HOST, PORT))

            res = client_socket.recv(PACKET_SIZE).decode()
            filenames = res.split(",")

            # Print files and accept num
            print("Welcome to the NetMusic Server!")
            print("Below is a list of filenames available.")
            for i in range(len(filenames)):
                print(f"    {i+1}:      {filenames[i]}")

            correct = False
            while not correct:
                num = int(input("\nType the file number, zero to exit: "))
                if num == 0:
                    print("Exiting...")
                    exit(0)
                elif num-1 < len(filenames) and num > 0:
                    correct = True
                else:
                    print("Incorrect option!")
            client_socket.send(filenames[num-1].encode())

            # Was the response correct
            res = client_socket.recv(PACKET_SIZE).decode()
            if res == "Rejected":
                print("Server rejected our connection")
                break
            else:
                print("Server accepted!")

        except Exception as e:
            print(e)
            # Close the client socket and audio stream
            client_socket.close()
            stream.stop_stream()
            stream.close()

            # Terminate PyAudio
            audio.terminate()

            print("Connection closed.")
            break
        except KeyboardInterrupt:
            print("User interrupted. Closing connection.")

            # Close the client socket and audio stream
            client_socket.close()
            stream.stop_stream()
            stream.close()

            # Terminate PyAudio
            audio.terminate()

            print("Connection closed.")
            break

        # Start audio worker thread
        comm_queue = queue.Queue()
        audio_worker = threading.Thread(
            target=playback_thread,
            args=(comm_queue, client_socket, audio, stream)
        )
        audio_worker.start()
        print("Playing... ")

        # main control thread
        while True:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                comm_queue.put("pause")
                try:
                    inp = input("Paused. Enter p to play, s to stop: ")
                    if inp == "p":
                        comm_queue.put("play")
                        print("Playing... ")
                    else:
                        comm_queue.put("stop")
                        audio_worker.join()
                        break
                except KeyboardInterrupt:
                    comm_queue.put("stop")
                    audio_worker.join()
                    break
        stream.start_stream()


if __name__ == "__main__":
    main()
