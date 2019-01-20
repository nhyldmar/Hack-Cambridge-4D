"""Generates .wav file without chunking, so better audio quality, but no pose processing or realtime feed."""

import numpy as np
from scipy.io import wavfile
from scipy.ndimage.interpolation import shift
import wave
import struct

speed_of_sound = 343
framerate = 44100
head_width = 0.15
positions = np.array([[-3, 0], [2, 0]])
audio_files = ['1.wav', '5.wav']


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


# Get raw channels
channels = []
frames = 0
for file in audio_files:
    channel = np.array(pcm_channels(file))
    channel = np.sum(channel, axis=0)
    channel_frames = np.size(channel)
    if channel_frames > frames:
        frames = channel_frames
    channels.append(channel)

# Pad to length
channels = np.array([np.pad(channel, (0, frames - np.size(channel)), 'constant') for channel in channels])

theta = 0
head_pos = np.array([0, 0])
pos = head_pos + np.array([head_width / 2 * np.cos(theta), np.sin(theta)])
pos = np.multiply([[1, -1], [-1, 1]], pos)

r = np.array([np.subtract(position, pos) for position in positions])  # Find way to remove this
r = np.linalg.norm(r, axis=2)
print(r)
phase_side = np.array([Rx > Lx for [Rx, Lx] in r])
print(phase_side)

# Add phase delay between channels
phase_frames = np.int(np.diff(r, 0) * framerate / speed_of_sound)
print(phase_frames)

RL_phased = np.repeat(channels, 2)
# RL_phased = shift(RL_phased[], phase_frames, cval=0)

RL_channels = RL_phased / r ** 2

# Write .wav file
wavfile.write('output.wav', framerate, np.asarray(RL_channels, dtype=np.int16).transpose())
