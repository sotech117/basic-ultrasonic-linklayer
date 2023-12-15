import utils as u
import time
from collections import Counter

def main():
    p = u.pyaudio.PyAudio()
    start_freq = 19800
    freq_range = 200
    bytes_per_transmit = 1

    stream = p.open(
        format=u.pyaudio.paInt32,
        channels=1,
        rate=44100,
        input=True,
        output=True,
        frames_per_buffer=2048 * 2,
    )

    char_counter = Counter()
    start_time = time.time()
    word = ''

    try:
        while True:
            current_time = time.time()
            if current_time - start_time >= 1:  # Every second
                # Find the most common character
                most_common_char, _ = char_counter.most_common(1)[0] if char_counter else ('', 0)
                print(f"Most common character in the last second: {most_common_char}")
                word += most_common_char
                print(f"Accumulated word: {word}")
                char_counter.clear()  # Reset for the next second
                start_time = current_time

            data, success = u.receive_data(stream, start_freq, freq_range, bytes_per_transmit)
            if success:
                char_counter[data] += 1

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
if __name__ == "__main__":
    main()