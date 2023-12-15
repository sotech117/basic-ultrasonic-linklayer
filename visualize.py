# This is a sample Python script.
import struct

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from scipy.fftpack import fft
import numpy as np
import pyaudio
import matplotlib.pyplot as plt

import utils as u


class Test(object):

    def __init__(self):
        # stream constants
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

        self.seenvalues = set()

        self.sample_divs = 4

    # goal: returns the max frequency of waveform
    def get_fundamental_frequency(self, audio_waveform):
        spectrum = fft(audio_waveform)

        # scale and normalize the spectrum, some are imaginary
        scaled_spectrum = np.abs(spectrum)
        scaled_spectrum = scaled_spectrum / (np.linalg.norm(scaled_spectrum) + 1e-16)

        # FIXME: update to self values, given if ur a sender or receiver
        starting_freq = 19800
        end_freq = 20000
        freq_to_index_ratio = self.CHUNK / self.RATE
        # only accept the scaled spectrum from our starting range to 20000 Hz
        starting_range_index = int(starting_freq * freq_to_index_ratio)
        ending_range_index = int(end_freq * freq_to_index_ratio)
        print(starting_freq, end_freq, starting_range_index, ending_range_index)
        restricted_spectrum = scaled_spectrum[starting_range_index:ending_range_index + 1]

        # normalize the restricted spectrum
        indices = np.argwhere(restricted_spectrum > .125)
        print(indices)

        freqs = [int((indices[i] + starting_range_index) / freq_to_index_ratio) for i in range(len(indices))]
        print(freqs)

        p = u.frequencies_to_bytes(freqs, u.calculate_send_frequencies(19800, 200, 1))
        data = p[:8]
        print(data)
        u.receive_string(data)

        # get the n indices of the max peaks, within our confined spectrum
        # FIXME: update to self values
        bytes = 1
        num_bits = bytes * 8 + 2
        if num_bits > len(restricted_spectrum):
            print("ERROR: num_bits > len(restricted_spectrum)")

        # print(index_to_freq[max_index], max_index, max_index * self.RATE / (self.CHUNK - 1))
        return freqs, scaled_spectrum

    def read_audio_stream(self):
        data = self.stream.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK) + 'i', data)
        return data_int

    def open_loop(self, graphics=True):
        self.init_plots()
        while not self.pause:
            waveform = self.read_audio_stream()
            freq_max, scaled_spectrum = self.get_fundamental_frequency(waveform)

            # update figure canvas if wanted
            if graphics:
                # set top graph
                data_np = np.array(waveform) / (np.linalg.norm(waveform) + 1e-16) * 10
                self.line.set_ydata(data_np[0:len(data_np)// self.sample_divs])
                # set bottom graph
                self.line_fft.set_ydata(scaled_spectrum)

                # update figures
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()

    def init_plots(self):

        # x variables for plotting
        x = np.arange(0, self.CHUNK * 2 // self.sample_divs, 2)
        xf = np.linspace(0, self.RATE, self.CHUNK)

        # create matplotlib figure and axes
        self.fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))

        # create a line object with random data
        self.line, = ax1.plot(x, np.random.rand(self.CHUNK // self.sample_divs), '-', lw=2)

        # create semilogx line for spectrum
        self.line_fft, = ax2.semilogx(
            xf, np.random.rand(self.CHUNK), '-', lw=2)

        # format waveform axes
        ax1.set_title('AUDIO WAVEFORM')
        ax1.set_xlabel('samples')
        ax1.set_ylabel('volume')
        ax1.set_ylim(-1, 1)
        ax1.set_xlim(0, self.CHUNK // self.sample_divs)
        plt.setp(
            ax1,
            xticks=[0, self.CHUNK // self.sample_divs, self.CHUNK * 2 // self.sample_divs],
        )
        plt.setp(ax2, yticks=[0, 1], )

        # format spectrum axes
        ax2.set_xlim(20, self.RATE / 2)

        # show axes
        thismanager = plt.get_current_fig_manager()
        # thismanager.window.setGeometry(5, 120, 1910, 1070)
        plt.show(block=False)


if __name__ == '__main__':
    t = Test()
    t.open_loop()