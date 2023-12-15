import numpy as np
import pyaudio
import threading
from utils import *

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


def play_frequencies_separately(freq_map, duration=1.0, samplingRate=44100):
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
"""
:param data: A string of characters.
:return: A list of binary strings.
"""


def string_to_binary(data):
    data_list = []
    for char in data:
        binary_representation = format(ord(char), 'b').zfill(8)
        data_list.append(binary_representation)
    return data_list


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


def receive_string(data, start_freq=18000, freq_step=250):
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
    def __init__(self, start_freq=19500):
        self.start_freq = start_freq
        self.freq_range = 500
        self.sampling_rate = 44100
        self.p = pyaudio.PyAudio()
        self.isReceiving = False
        self.isEstablished = False
        self.bytes_per_transmit = 1
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)

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
