# given the cmdline arg, turns the byte sequencies into a list of frequencies, and vice versa

# 1875 1924 +24, -25, range/2, 1, flipping new info 2 sending or not
import numpy as np
import pyaudio
import threading
from scipy.fftpack import fft


def wave_to_bits(wave, starting_freq, freq_range, bytes_per_transmit, chunk=4096, rate=44100):
    spectrum = fft(wave)
    spectrum = np.abs(spectrum)
    spectrum = spectrum / (np.linalg.norm(spectrum) + 1e-16)

    # FIXME: update to self values, given if ur a sender or receiver
    starting_freq = starting_freq
    end_freq = starting_freq + freq_range
    freq_to_index_ratio = (chunk - 1) / rate

    # only accept the scaled spectrum from our starting range to 20000 Hz
    starting_range_index = int(starting_freq * freq_to_index_ratio)
    ending_range_index = int(end_freq * freq_to_index_ratio)
    restricted_spectrum = spectrum[starting_range_index:ending_range_index + 1]

    # get the n indices of the max peaks of amplitude greater than .125, within our confined spectrum
    indices = np.argwhere(restricted_spectrum > .125)

    freqs = [int((indices[i] + starting_range_index) / freq_to_index_ratio) for i in range(len(indices))]

    # convert the frequencies to bits
    data = frequencies_to_bits(freqs, calculate_send_frequencies(starting_freq, freq_range, bytes_per_transmit))

    # TODO: remove
    byte = data[:8]
    to_return = ''
    if data[-1] == '1':
        to_return = receive_string(byte)

    return data, to_return


def calculate_send_frequencies(start_freq, freq_range, bytes_per_transmit):
    bits_to_send = 8 * bytes_per_transmit + 2  # 8 bits per byte, 2 bits for flags
    freq_interval = freq_range / (bits_to_send + 1)  # +1 to not include endpoints of range

    freq_list = []
    for i in range(bits_to_send):
        f = int(start_freq + (i + 1) * freq_interval)
        freq_list.append(f)

    return freq_list


def frequencies_to_bits(frequencies, expected_freqs):
    # get the interval between frequencies, so we can clamp the range around them
    freq_interval = expected_freqs[1] - expected_freqs[0]
    plus_minus = freq_interval // 2

    bit_list = ['0'] * len(expected_freqs)
    for freq in frequencies:
        for i in range(len(expected_freqs)):
            # clamp the range around the frequency to the frequency
            if expected_freqs[i] - plus_minus <= freq < expected_freqs[i] + plus_minus:
                bit_list[i] = '1'

    return bit_list


def play_data(data, start_freq, freq_step, bytes_per_transmit, stream):
    freq_list = calculate_send_frequencies(start_freq, freq_step, bytes_per_transmit)

    send_duration = 1.0

    flip_flag = 0  # TODO: make this global between plays
    for byte in data:
        byte = byte + str(flip_flag) + '1'
        print(byte)
        samples = None
        for i, bit in enumerate(byte):
            if bit == '1':
                print(freq_list[i])
                s = .125 * np.sin(2 * np.pi * np.arange(44100 * send_duration) * freq_list[i] / 44100)
                if samples is None:
                    samples = s
                else:
                    samples = np.add(samples, s)
        if samples is not None:
            stream.write(samples.astype(np.float32).tobytes())
        flip_flag = (flip_flag + 1) % 2


def receive_string(binary):
    binary_string = ''.join(binary)
    try:
        # print(chr(int(binary_string, 2)))
        return chr(int(binary_string, 2))
    except ValueError:
        print("Error: Invalid binary data")

def string_to_binary(data):
    data_list = []
    for char in data:
        binary_representation = format(ord(char), 'b').zfill(8)
        data_list.append(binary_representation)
    return data_list