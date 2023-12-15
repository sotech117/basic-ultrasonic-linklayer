import struct

import numpy as np
import pyaudio
import threading
from utils import *


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

    def read_audio_stream(self):
        data = self.stream.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK) + 'i', data)
        return data_int

    def listen(self):
        while True:
            data = self.read_audio_stream()
            recv_freq_range = self.freq_range / 2
            wave_to_bits(data, self.start_freq, recv_freq_range, self.bytes_per_transmit)


def main():
    recv = Recv()
    recv.listen()


if __name__ == "__main__":
    main()
