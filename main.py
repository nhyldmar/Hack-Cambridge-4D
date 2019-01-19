"""This is the doc file.
All distances in mm."""

import numpy as np
import matplotlib.pyplot as plt
import wave
import struct

head_width = 150
R_pos = [-head_width / 2, 0]
L_pos = [head_width / 2, 0]
theta = 0
positions = [[1000, 1000], [1000, 1000]]
audio_files = ['1.wav', '2.wav']


def pcm_channels(file_name):
    """Given a file-like object or file path representing a wave file,
    decompose it into its constituent PCM data streams.
    """
    stream = wave.open(file_name, "rb")

    num_channels = stream.getnchannels()
    sample_width = stream.getsampwidth()
    num_frames = stream.getnframes()

    raw_data = stream.readframes(num_frames)  # Returns byte data
    stream.close()

    total_samples = num_frames * num_channels

    if sample_width == 1:
        fmt = "%iB" % total_samples  # read unsigned chars
    elif sample_width == 2:
        fmt = "%ih" % total_samples  # read signed 2 byte shorts
    else:
        raise ValueError("Only supports 8 and 16 bit audio formats.")

    integer_data = struct.unpack(fmt, raw_data)
    del raw_data  # Keep memory tidy (who knows how big it might be)

    channels = [[] for time in range(num_channels)]

    for index, value in enumerate(integer_data):
        bucket = index % num_channels
        channels[bucket].append(value)

    return channels, num_frames


channels = np.array([])
frames = 0
for file in audio_files:
    channel, num_frames = pcm_channels(file)[0]
    if num_frames > frames:
        frames = num_frames
    np.append(channels, channel)

# Pad to length


# Add channels
R_channel = np.array([])
L_channel = np.zeros(len(channels))
for position in positions:
    R_r2 = (position[0] - R_pos[0]) ** 2 + (position[1] - R_pos[1]) ** 2
    L_r2 = (position[0] - R_pos[0]) ** 2 + (position[1] - R_pos[1]) ** 2
    R_channel += channels[0] / R_r2
    L_channel += channels[1] / L_r2


def signal_to_wav(channels, file_name):
    """"Given PCM channels and a file name,
    save a .wav file of the audio.
    """
    data = struct.pack('<' + ('h' * len(channels)), *channels)
    wav_file = wave.open(file_name, 'wb')
    wav_file.setnchannels(len(channels))
    wav_file.setsampwidth(2)
    wav_file.setframerate(44100)
    wav_file.writeframes(data)
    wav_file.close()


# Write .wav file
signal_to_wav([L_channel, R_channel], 'output.wav')
