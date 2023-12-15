import numpy as np
import pyaudio
import threading
from utils import *
import struct
import time
from collections import Counter
"""
:param data: A list of peak frequencies.
return: A string of characters.
"""


def receive_string(data, start_freq=19000, freq_step=250):
    binary = ['0'] * 8

    for item in data:
        freqPosition = (item - start_freq) // freq_step
        if 0 <= freqPosition < 8: binary[freqPosition] = '1'

    binary_string = ''.join(binary)
    try:
        return chr(int(binary_string, 2))
    except ValueError:
        return "Error: Invalid binary data"


class LinkLayer:
    def __init__(self, start_freq=18000):
        self.start_freq = start_freq
        self.freq_range = 2000
        self.sampling_rate = 44100
        self.p = pyaudio.PyAudio()
        self.isReceiving = False
        self.isEstablished = False
        self.bytes_per_transmit = 1
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)
        self.streamListen = self.p.open(format=pyaudio.paFloat32, channels=1, rate=44100, input=True)
        self.CHUNK = 2048 * 2

    def transmit_string(self, data):
        data_list = string_to_binary(data)
        send_freq_range = self.freq_range / 2
        play_data(data_list, self.start_freq, send_freq_range, self.bytes_per_transmit, self.stream)

    def send_data(self):
        while True:
            if not self.isReceiving:
                user_input = input("Enter data to send: ")
                if user_input == "exit" or user_input == "q":
                    self.stream.stop_stream()
                    self.stream.close()
                    break
                self.transmit_string(user_input)
                if not self.listen(user_input): self.transmit_string(user_input)
            else:
                print("Currently receiving data, please wait...")

    def read_audio_stream(self):
        data = self.streamListen.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK) + 'i', data)
        return data_int
    

    def listen(self, data):
        char_counter = Counter()
        start_time = time.time()
        word = ''
        current_time = time.time()
        if current_time - start_time >= 1:  # Every second
            # Find the most common character
            most_common_char, _ = char_counter.most_common(1)[0] if char_counter else ('', 0)
            # print(f"Most common character in the last second: {most_common_char}")
            word += most_common_char
            print(f"Accumulated word: {word}")
            char_counter.clear()  # Reset for the next second
            start_time = current_time

        # wait half a second
        time.sleep(.5)
        audio_data = self.read_audio_stream()
        recv_freq_range = self.freq_range / 2
        list, letter = wave_to_bits(audio_data, self.start_freq, recv_freq_range, self.bytes_per_transmit)

        if letter == data: return True
        return False

def main():
    link_layer = LinkLayer()

    # Create a thread for sending data
    send_thread = threading.Thread(target=link_layer.send_data)

    # Start the threads
    send_thread.start()


if __name__ == "__main__":
    main()
