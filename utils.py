# given the cmdline arg, turns the byte sequencies into a list of frequencies, and vice versa

# 1875 1924 +24, -25, range/2, 1, flipping new info 2 sending or not
import numpy as np
import pyaudio
import threading


def calculate_send_frequencies(start_freq, freq_range, bytes_per_transmit):
    bits_to_send = 8 * bytes_per_transmit + 2  # 8 bits per byte, 2 bits for flags
    freq_interval = freq_range / (bits_to_send + 1)  # +1 to not include endpoints of range

    freq_list = []
    for i in range(bits_to_send):
        f = int(start_freq + (i + 1) * freq_interval)
        freq_list.append(f)

    print(freq_list)

    return freq_list


def frequencies_to_bytes(frequencies, expected_freqs):
    # get the interval between frequencies, so we can clamp the range around them
    freq_interval = expected_freqs[1] - expected_freqs[0]
    plus_minus = freq_interval // 2

    byte_list = ['0'] * len(expected_freqs)
    for freq in frequencies:
        for i in range(len(expected_freqs)):
            # clamp the range around the frequency to the frequency
            if expected_freqs[i] - plus_minus <= freq < expected_freqs[i] + plus_minus:
                byte_list[i] = '1'

    return byte_list

def play_data(data, start_freq, freq_step, bytes_per_transmit, p):
    freq_list = calculate_send_frequencies(start_freq, freq_step, bytes_per_transmit)

    for byte in data:
        print(byte)
        samples = None
        for i, bit in enumerate(byte):
            if bit == '1':
                print(freq_list[i])
                s = .125 * np.sin(2 * np.pi * np.arange(44100 * 10.0) * freq_list[i] / 44100)
                if samples is None:
                    samples = s
                else:
                    samples = np.add(samples, s)
        if samples is not None:
            print(samples)
            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)
            stream.write(samples.astype(np.float32).tobytes())
            stream.stop_stream()
            stream.close()

def receive_string(binary):
    binary_string = ''.join(binary)
    try:
        print(chr(int(binary_string, 2)))
    except ValueError:
        print("Error: Invalid binary data")