import numpy as np
import pyaudio
import threading
from utils import *
import struct
import time
from collections import Counter

"""
Play a single frequency.

:param freq: Frequency in Hz.
:param amplitude: Amplitude of the frequency (0.0 to 1.0).
:param duration: Duration of the sound in seconds.
:param samplingRate: Sampling rate in Hz.
"""


def play_frequency(freq, amplitude, duration=1.0, samplingRate=44100, p=None):
    # Generate sample for the given frequency as a float32 array
    samples = (amplitude * np.sin(2 * np.pi * np.arange(samplingRate * duration) * freq / samplingRate)).astype(
        np.float32).tobytes()

    # Open stream
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=samplingRate,
                    output=True)

    stream.write(samples)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # p.terminate()


"""
Use threads to play multiple frequencies simultaneously.

:param freq_map: A dictionary with frequency (Hz) as keys and amplitude (0.0 to 1.0) as values.
:param duration: Duration of the sound in seconds.
:param samplingRate: Sampling rate in Hz.
"""


def play_frequencies_separately(freq_map, duration=1, samplingRate=44100):
    p = pyaudio.PyAudio()

    threads = []
    for freq, amplitude in freq_map.items():
        thread = threading.Thread(target=play_frequency, args=(freq, amplitude, duration, samplingRate, p))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    p.terminate()


# hello in binary
# data = "01101000 01100101 01101100 01101100 01101111"

# convert string to binary representation

# transmit string
"""
:param data: A string of characters.
"""


def transmit_string(data):
    data_list = string_to_binary(data)

    for i in range(len(data_list)):
        freq_map = {}
        start_freq = 18000
        for j in range(len(data_list[i])):
            if data_list[i][j] == "0":
                freq_map[start_freq + j * 250] = 0.0

            if data_list[i][j] == "1":
                freq_map[start_freq + j * 250] = 1.0

        # print(freq_map)
        play_frequencies_separately(freq_map, duration=1000)


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


# Example usage
# data for the letter h
# # 01101000
# data = [18250, 18500, 19000]
# decoded_string = receive_string(data)
# print(decoded_string)


# transmit_string("h")


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
