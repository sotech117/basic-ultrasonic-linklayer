import struct

import numpy as np
import pyaudio
import threading

import utils
from utils import *
import time
from collections import Counter


class Recv:
    def __init__(self, start_freq=18000):
        self.start_freq = start_freq
        self.freq_range = 2000
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
        prev_is_data_flag = '0'
        prev_is_new_byte_flag = '0'

        bytes_seen = []
        recv_buffer = []

        while True:
            data = self.read_audio_stream()
            recv_freq_range = self.freq_range / 2
            bits = wave_to_bits(data, self.start_freq, recv_freq_range, self.bytes_per_transmit)

            # handle the data flags
            is_data_flag = bits[-1]
            is_new_byte_flag = bits[-2]

            if prev_is_data_flag == '0' and is_data_flag == '1':
                prev_is_data_flag = is_data_flag
                # just started receiving data
                bytes_seen = []
                recv_buffer = []

            is_data_flag = bits[-1]
            if prev_is_data_flag == '0' and is_data_flag == '0':
                prev_is_data_flag = is_data_flag

                # just waiting for new data
                continue

            if prev_is_data_flag == '1' and is_data_flag == '0':
                prev_is_data_flag = is_data_flag

                # just finished the last byte of data, add it to buffer, then write buffer to terminal
                recv_buffer.append(self.safe_check_byte(bytes_seen))

                # FIXME: what to do with buffer?
                # for now print buffer as string
                buffer_as_string = ''.join([utils.receive_string(byte) for byte in recv_buffer])
                print("recv_buffer: ", buffer_as_string)

                # clear data structure & buffer
                continue

            # at this point, we know we are receiving data
            if prev_is_new_byte_flag == is_new_byte_flag:
                prev_is_new_byte_flag = is_new_byte_flag

                # we are still receiving the same byte, store it in the data structure
                byte = bits[:-2]
                bytes_seen.append(byte)
                continue
            else:
                prev_is_new_byte_flag = is_new_byte_flag

                # we are receiving a new byte, so we need to write the old byte to the recv buffer
                recv_buffer.append(self.safe_check_byte(bytes_seen))
                # clear the data structure
                bytes_seen = []

                # append the new byte to the data structure
                byte = bits[:-2]
                bytes_seen.append(byte)
                continue

def main():
    recv = Recv()
    recv.listen()


if __name__ == "__main__":
    main()
