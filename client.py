import socket
import pyaudio
import ssl
import threading
import queue
import time

HOSTNAME = "netmusic"
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
            if main_message == "quit":
                print("exit client thread")
                break
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


def validate_client_nums(nums, limit):
    for num in nums:
        if int(num) - 1 not in range(limit):
            return False
    else:
        return True


def main():
    # Define an SSL context and verify hostname
    context = ssl.create_default_context()
    context.load_verify_locations("./server.crt")

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

            server_filenames = client_socket.recv(PACKET_SIZE).decode()
            playlist_op = client_socket.recv(PACKET_SIZE).decode()
            filenames = server_filenames.split(",")

            # Print files and accept num
            print("Welcome to the NetMusic Server!")
            print("Below is a list of filenames available.")
            for i in range(len(filenames)):
                fname = filenames[i][:-4].replace('_', ' ')
                print(f"    {i+1}:      {fname}")

            correct = False
            playlist_wanted = " "
            while not correct:
                playlist_wanted = input(playlist_op)
                if playlist_wanted.lower() == "yes" or playlist_wanted.lower() == "no":
                    correct = True
                else:
                    print("Please enter yes/no")

            client_socket.send(playlist_wanted.encode())
            song_index = client_socket.recv(PACKET_SIZE).decode()
            if playlist_wanted == "no":
                correct = False
                while not correct:
                    num = int(input("\n " + song_index))
                    if num == 0:
                        print("Exiting...")
                        exit(0)
                    elif num-1 < len(filenames) and num > 0:
                        correct = True
                    else:
                        print("Incorrect option!")
                client_socket.send(str(num-1).encode())

                # Was the response correct
                server_filenames = client_socket.recv(PACKET_SIZE).decode()
                if server_filenames.startswith("Invalid"):
                    print("Server rejected our connection")
                    break
                else:
                    print("Server accepted!")

                # Start audio worker thread
                comm_queue = queue.Queue()
                audio_worker = threading.Thread(
                    target=playback_thread,
                    args=(comm_queue, client_socket, audio, stream)
                )
                audio_worker.start()
                fname = filenames[num-1][:-4].replace('_', ' ')
                print(f"\n\nPlaying {fname} (press ctrl^c to pause)... ")

                # main control thread
                while True:
                    try:
                        time.sleep(0.1)
                    except KeyboardInterrupt:
                        comm_queue.put("pause")
                        try:
                            inp = input(
                                "\nPaused. Enter p to play, s to stop: ")
                            if inp == "p":
                                comm_queue.put("play")
                                print("\nPlaying... ")
                            else:
                                comm_queue.put("stop")
                                audio_worker.join()
                                break
                        except KeyboardInterrupt:
                            comm_queue.put("stop")
                            audio_worker.join()
                            break
                comm_queue.put("stop")
                audio_worker.join()
                print(client_socket.recv(PACKET_SIZE).decode())
                client_socket.send("ack".encode())
                stream.start_stream()
            else:
                correct = False
                num = []
                while not correct:
                    num = input("\n " + song_index).split(",")
                    if num == 0:
                        print("Exiting...")
                        exit(0)
                    elif validate_client_nums(num, len(filenames)):
                        correct = True
                    else:
                        print("Incorrect numbers!")
                intgnums = [str(int(x) - 1) for x in num]
                client_socket.send(",".join(intgnums).encode())

                res = client_socket.recv(PACKET_SIZE).decode()
                if res.startswith("Invalid"):
                    print("Invalid codes!")
                    break
                else:
                    print("Accepted")

                print(client_socket.recv(PACKET_SIZE).decode())

                # Start audio worker thread
                comm_queue = queue.Queue()
                audio_worker = threading.Thread(
                    target=playback_thread,
                    args=(comm_queue, client_socket, audio, stream)
                )

                # main control thread
                run = True
                i = 0
                while run:
                    audio_worker.start()
                    print(f"\n\nPlaying {
                          filenames[int(num[i])-1]} (press ctrl^c to pause)... ")
                    while True:
                        try:
                            time.sleep(0.1)
                        except KeyboardInterrupt:
                            comm_queue.put("pause")
                            try:
                                inp = input(
                                    "\nPaused. Enter p to play, s to stop: ")
                                if inp == "p":
                                    comm_queue.put("play")
                                    print("\nPlaying... ")
                                else:
                                    comm_queue.put("stop")
                                    audio_worker.join()
                                    break
                            except KeyboardInterrupt:
                                comm_queue.put("stop")
                                audio_worker.join()
                                break
                    stream.start_stream()
                    i += 1
                    val = client_socket.recv(PACKET_SIZE).decode()
                    if "Song" in val:
                        client_socket.send("ack".encode())
                    else:
                        run = False

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


if __name__ == "__main__":
    main()
