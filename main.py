"""This is the doc file.
All distances in m."""

import numpy as np
from scipy.io import wavfile
import wave
import struct

speed_of_sound = 343
head_width = 0.15
theta = 0
head_pos = np.array([0, 0])
R_pos = head_pos + [-head_width / 2 * np.cos(theta), np.sin(theta)]
L_pos = head_pos + [head_width / 2 * np.cos(theta), np.sin(theta)]
positions = [[-3, 0]]
audio_files = ['1.wav']


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

    return channels


channels = []
frames = 0
for file in audio_files:
    channel = pcm_channels(file)[0]
    channel_frames = len(channel)
    if channel_frames > frames:
        frames = channel_frames
    channels.append(channel)

# Pad to length
channels = np.array([np.pad(channel, (0, frames - len(channel)), 'constant') for channel in channels])

# Generate channels
R_channel = np.zeros(frames)
L_channel = np.zeros(frames)
for position in positions:
    i = positions.index(position)
    R_r2 = (position[0] - R_pos[0]) ** 2 + (position[1] - R_pos[1]) ** 2
    L_r2 = (position[0] - L_pos[0]) ** 2 + (position[1] - L_pos[1]) ** 2
    phase_frames = int(abs(np.sqrt(R_r2) - np.sqrt(L_r2)) * 44100 / speed_of_sound)
    R_channel += channels[i] / R_r2
    L_channel += channels[i] / L_r2
    if position[0] >= 0:
        L_channel = np.concatenate((np.zeros(phase_frames), L_channel[:-phase_frames]))
    else:
        R_channel = np.concatenate((np.zeros(phase_frames), L_channel[:-phase_frames]))

# Write .wav file
wavfile.write('output.wav', 44100, np.asarray([R_channel, L_channel], dtype=np.int16).transpose())
