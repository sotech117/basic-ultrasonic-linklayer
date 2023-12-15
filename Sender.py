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

class LinkLayer:
    def __init__(self, start_freq=5000):
        self.start_freq = start_freq
        self.freq_range = 500
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
            else:
                print("Currently receiving data, please wait...")

def main():
    link_layer = LinkLayer()

    # Create a thread for sending data
    send_thread = threading.Thread(target=link_layer.send_data)

    # Start the threads
    send_thread.start()


if __name__ == "__main__":
    main()
