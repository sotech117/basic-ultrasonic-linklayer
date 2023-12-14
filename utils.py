
# given the cmdline arg, turns the byte sequencies into a list of frequencies, and vice versa

# 1875 1924 +24, -25, range/2, 1, flipping new info 2 sending or not


def make_frequencies_map(start_freq, freq_step, byte_per_transmit, is_sender=True):
    freq_list = [None] * (byte_per_transmit + 3)
    sender_range = freq_step // 2 
    plus_minus = sender_range // (byte_per_transmit + 3)
    
    for i in range(byte_per_transmit + 3):
        freq_list[i] = start_freq + i * plus_minus
        if not is_sender:
            freq_list[i] += sender_range

    return freq_list


def frequencies_to_bytes(frequencies, start_freq, freq_step, byte_per_transmit, is_sender=True):
    freq_list = make_frequencies_map(start_freq, freq_step, byte_per_transmit, is_sender)
    byte_list = [None] * len(frequencies)

    sender_range = freq_step // 2 
    plus_minus = sender_range // (byte_per_transmit + 3)

    for i in range(len(frequencies)):
        byte_list[i] = 0
        if frequencies[i] <= freq_list[i] < frequencies[i] + plus_minus - 1: byte_list[i] = 1

    return byte_list