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

    byte_list = [0] * len(frequencies)
    for freq in frequencies:
        for i in range(len(frequencies)):
            # clamp the range around the frequency to the frequency
            if expected_freqs[i] - plus_minus <= freq < expected_freqs[i] + plus_minus:
                byte_list[i] = 1

    return byte_list


def play_frequency(freq, p, duration=1.0, samplingRate=44100):
    amplitude = .1  # Maximum amplitude
    print(freq)
    samples = (amplitude * np.sin(2 * np.pi * np.arange(samplingRate * duration) * freq / samplingRate)).astype(
        np.float32).tobytes()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=samplingRate, output=True)
    stream.write(samples)

    # thread for listening here

    stream.stop_stream()
    stream.close()


# def play_data(data, start_freq, freq_step, byte_per_transmit):
#     p = pyaudio.PyAudio()
#     freq_list = make_frequencies_map(start_freq, freq_step, byte_per_transmit)
#     print(freq_list, data)

#     def play_thread(freq):
#         play_frequency(freq, p=p)

#     threads = []
#     for item in data:
#         for i, bit in enumerate(item):
#             if bit == '1':
#                 thread = threading.Thread(target=play_thread, args=(freq_list[i],))
#                 threads.append(thread)
#                 thread.start()

#     for thread in threads:
#         thread.join()

#     p.terminate()

def play_data(data, start_freq, freq_step, bytes_per_transmit, p):
    freq_list = calculate_send_frequencies(start_freq, freq_step, bytes_per_transmit)

    threads = []
    for item in data:
        for i, bit in enumerate(item):
            if bit == '1':
                thread = threading.Thread(target=play_frequency, args=(freq_list[i], p, 10.0))
                threads.append(thread)
                thread.start()

    for thread in threads:
        thread.join()

# def listen_for_confirmation(stream):
#     # Logic to listen and decode the confirmation data
#     # This function should run in its own thread

#     recieved_data = stream.read(1024)
