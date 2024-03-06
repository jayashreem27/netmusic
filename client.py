import socket
import pyaudio
import ssl

HOSTNAME = "localhost"
HOST = "127.0.0.1"
PORT = 5544
PACKET_SIZE = 1024


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
    print("Audio Initialization ended")

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
            print("Below is a list of filenames available.")
            for i in range(len(filenames)):
                print(f"{i+1}, {filenames[i]}")

            correct = False
            while not correct:
                num = int(input("\nType the file number:"))
                if num-1 < len(filenames):
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

        # Start recv cycle
        data = " "
        while data:
            try:
                data = client_socket.recv(PACKET_SIZE)
                stream.write(data)
            except Exception as e:
                print(e)
                break
            except KeyboardInterrupt:
                print("Keyboard interrupt")
                break


if __name__ == "__main__":
    main()
