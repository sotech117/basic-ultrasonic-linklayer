import struct

import numpy as np
import pyaudio

from utils import *
import time
from collections import Counter


class Recv:
    def __init__(self, start_freq=5000):
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

    def read_audio_stream(self):
        data = self.stream.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK) + 'i', data)
        return data_int

    def print_data(self, data):
        print(data)

    def safe_check_byte(self, bytes_seen):
        safe_byte = []

        if len(bytes_seen) > 0:
            for col in range(len(bytes_seen[0])):
                count1s = 0
                count0s = 0
                for row in range(len(bytes_seen)):
                    bit = bytes_seen[row][col]
                    if bit == '1':
                        count1s += 1
                    else:
                        count0s += 1
                if count1s > count0s:
                    safe_byte.append('1')
                else:
                    safe_byte.append('0')

        return safe_byte

    def listen(self):
        char_counter = Counter()
        start_time = time.time()
        word = ''
        try:
            while True:
                current_time = time.time()
                if current_time - start_time >= 1.5:  # Every second
                    # Find the most common character
                    most_common_char, _ = char_counter.most_common(1)[0] if char_counter else ('', 0)
                    # print(f"Most common character in the last second: {most_common_char}")
                    word += most_common_char
                    print(f"Accumulated word: {word}")
                    char_counter.clear()  # Reset for the next second
                    start_time = current_time

                data = self.read_audio_stream()
                
                recv_freq_range = self.freq_range / 2
                bits = wave_to_bits(data, self.start_freq, recv_freq_range, self.bytes_per_transmit)
                letter = receive_string(bits[:-2])
                if letter:
                    char_counter[letter] += 1

        except KeyboardInterrupt:
            print("Stopping...")

def main():
    recv = Recv()
    recv.listen()


if __name__ == "__main__":
    main()
