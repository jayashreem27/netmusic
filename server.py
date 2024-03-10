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
    # Upgrade connection to SSL
    with ssl_context.wrap_socket(conn, server_side=True) as secure_conn:
        print(f"[{address}] connected")

        # Parse the files available and send
        files = os.listdir(SONGS_DIR)
        files_data = ",".join(files)
        secure_conn.send(files_data.encode())
        try:
            # Prompt user to create a playlist or select individual songs
            secure_conn.send("Create playlist? (yes/no): ".encode())
            playlist_choice = secure_conn.recv(PACKET_SIZE).decode()

            if playlist_choice.lower() == 'yes':
                # Receive selected song indexes for the playlist
                secure_conn.send("Enter song indexes for playlist (comma-separated): ".encode())
                song_indexes = secure_conn.recv(PACKET_SIZE).decode().split(',')
                songs_to_play = []

                # Validate indexe
                for index in song_indexes:
                    try:
                        song_index = int(index)
                        if 0 <= song_index < len(files):
                            songs_to_play.append(files[song_index])
                        else:
                            secure_conn.send(f"Invalid song index: {index}. Please enter a valid index.".encode())
                            return None
                    except ValueError:
                        secure_conn.send(f"Invalid song index: {index}. Please enter a valid index.".encode())
                        return None

                # Send confirmation to start playlist
                secure_conn.send("Starting playlist...".encode())

                # Play selected songs one by one
                for index, filename in enumerate(songs_to_play):
                    song_path = SONGS_DIR + filename

                    # Open wave file to play
                    waveform = wave.open(song_path, 'rb')
                    print(f"{address} opened file", song_path)

                    # Start transmission loop
                    data = " "
                    while data:
                        # Send the next chunk
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
                    waveform.close()

                    # Notify client that the song has finished
                    if index < len(songs_to_play) - 1:
                        next_song = songs_to_play[index + 1]
                        secure_conn.send(f"Song {filename} finished. Next song: {next_song}".encode())
                    else:
                        secure_conn.send("Playlist finished".encode())
            else:
                # Receive individual song index to play
                secure_conn.send("Enter song index to play: ".encode())
                song_index = int(secure_conn.recv(PACKET_SIZE).decode())

                # Validate song index
                if 0 <= song_index < len(files):
                    filename = files[song_index]

                    # Send confirmation to start playing the selected song
                    secure_conn.send(f"Playing song {filename}...".encode())

                    # Play the selected song
                    song_path = SONGS_DIR + filename
                    waveform = wave.open(song_path, 'rb')
                    print(f"{address} opened file", song_path)

                    data = " "
                    while data:
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
                    waveform.close()
                    secure_conn.send("Song finished".encode())
                else:
                    secure_conn.send("Invalid song index. Please enter a valid index.".encode())
        except ssl.SSLEOFError:
            print(f"[{address}] disconnected")
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            secure_conn.close()


if __name__ == "__main__":
    try:
        # Define the SSL socket using the keyfiles
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="./server.crt",
                                keyfile="./server.key")

        # Create a socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        print(f"Serving on {(HOST, PORT)}")
        server_socket.listen()
    except Exception as e:
        print(e)

    # Always listen for incoming connections
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
