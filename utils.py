
# given the cmdline arg, turns the byte sequencies into a list of frequencies, and vice versa

# 1875 1924 +24, -25, range/2, 1, flipping new info 2 sending or not
import numpy as np
import pyaudio
import threading


def make_frequencies_map(start_freq, freq_step, byte_per_transmit, is_sender=True):
    # start_freq += 1500
    freq_list = []
    sender_range = freq_step // 2 
    plus_minus = sender_range // (byte_per_transmit + 3)
    
    for i in range(byte_per_transmit + 3):
        # print(start_freq + i * plus_minus, sender_range, plus_minus)
        freq_list.append(start_freq + i * plus_minus)
        if not is_sender:
            freq_list[i] += sender_range

    return freq_list


def frequencies_to_bytes(frequencies, start_freq, freq_step, byte_per_transmit, is_sender=True):
    freq_list = make_frequencies_map(start_freq, freq_step, byte_per_transmit, is_sender)
    byte_list = []

    sender_range = freq_step // 2 
    plus_minus = sender_range // (byte_per_transmit + 3)

    for i in range(len(frequencies)):
        if frequencies[i] <= freq_list[i] < frequencies[i] + plus_minus - 1: 
            byte_list.append("1")
        else:
            byte_list.append("0")

    return byte_list

def play_frequency(freq, p, duration=1.0, samplingRate=44100):
    amplitude = 1.0  # Maximum amplitude
    samples = (amplitude * np.sin(2 * np.pi * np.arange(samplingRate * duration) * freq / samplingRate)).astype(np.float32).tobytes()
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
    
def play_data(data, start_freq, freq_step, byte_per_transmit, p):
    freq_list = make_frequencies_map(start_freq, freq_step, byte_per_transmit)
    

    threads = []
    for item in data:
        for i, bit in enumerate(item):
            if bit == '1':
                thread = threading.Thread(target=play_frequency, args=(freq_list[i], p, 1.0))
                threads.append(thread)
                thread.start()

    for thread in threads:
        thread.join()


# def listen_for_confirmation(stream):
#     # Logic to listen and decode the confirmation data
#     # This function should run in its own thread
    
#     recieved_data = stream.read(1024)

