import struct

import numpy as np
import pyaudio
import threading
from utils import *
import time
from collections import Counter


class Recv:
    def __init__(self, start_freq=19500):
        self.start_freq = start_freq
        self.freq_range = 500
        self.sampling_rate = 44100
        self.p = pyaudio.PyAudio()
        self.bytes_per_transmit = 1


        # TODO: use stream to send back the data
        self.CHUNK = 2048 * 2
        self.FORMAT = pyaudio.paInt32
        self.CHANNELS = 1
        self.RATE = 44100
        self.pause = False
        # stream object
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )
        self.streamSend = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
        )


    def read_audio_stream(self):
        data = self.stream.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK) + 'i', data)
        return data_int

    def listen(self):
        char_counter = Counter()
        start_time = time.time()
        word = ''
        try:
            while True:
                # data = self.read_audio_stream()
                # recv_freq_range = self.freq_range / 2
                # wave_to_bits(data, self.start_freq, recv_freq_range, self.bytes_per_transmit)
                current_time = time.time()
                if current_time - start_time >= 1:  # Every second
                    # Find the most common character
                    most_common_char, _ = char_counter.most_common(1)[0] if char_counter else ('', 0)
                    # print(f"Most common character in the last second: {most_common_char}")
                    word += most_common_char
                    print(f"Accumulated word: {word}")
                    char_counter.clear()  # Reset for the next second
                    start_time = current_time

                data = self.read_audio_stream()
                recv_freq_range = self.freq_range / 2
                list, letter = wave_to_bits(data, self.start_freq, recv_freq_range, self.bytes_per_transmit)

                # send back the data
                data_list = string_to_binary(letter)
                send_freq_range = self.freq_range / 2
                play_data(data_list, self.start_freq, send_freq_range, self.bytes_per_transmit, self.streamSend)

                if letter:
                    char_counter[letter] += 1

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.streamSend.stop_stream()
            self.streamSend.close()
            self.p.terminate()

def main():
    recv = Recv()
    recv.listen()


if __name__ == "__main__":
    main()

# import utils as u
# import time
# from collections import Counter

# def main():
#     p = u.pyaudio.PyAudio()
#     start_freq = 19800
#     freq_range = 200
#     bytes_per_transmit = 1

#     stream = p.open(
#         format=u.pyaudio.paInt32,
#         channels=1,
#         rate=44100,
#         input=True,
#         output=True,
#         frames_per_buffer=2048 * 2,
#     )

#     char_counter = Counter()
#     start_time = time.time()
#     word = ''

#     try:
#         while True:
#             current_time = time.time()
#             if current_time - start_time >= 1:  # Every second
#                 # Find the most common character
#                 most_common_char, _ = char_counter.most_common(1)[0] if char_counter else ('', 0)
#                 print(f"Most common character in the last second: {most_common_char}")
#                 word += most_common_char
#                 print(f"Accumulated word: {word}")
#                 char_counter.clear()  # Reset for the next second
#                 start_time = current_time

#             data, success = u.receive_data(stream, start_freq, freq_range, bytes_per_transmit)
#             if success:
#                 char_counter[data] += 1

#     except KeyboardInterrupt:
#         print("Stopping...")
#     finally:
#         stream.stop_stream()
#         stream.close()
#         p.terminate()
# if __name__ == "__main__":
#     main()