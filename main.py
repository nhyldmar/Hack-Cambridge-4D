"""This is the doc file.
All distances in m."""

import numpy as np
from scipy.io import wavfile
import wave
import struct

speed_of_sound = 343
framerate = 44100
head_width = 0.15
positions = [[2, 2]]
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


# Get raw channels
channels = []
frames = 0
for file in audio_files:
    channel = pcm_channels(file)
    channel = channel[0] + channel[1]
    channel_frames = len(channel)
    if channel_frames > frames:
        frames = channel_frames
    channels.append(channel)

# Pad to length
channels = np.array([np.pad(channel, (0, frames - len(channel)), 'constant') for channel in channels])

theta = 0
head_pos = np.array([0, 0])
set_chunk_size = frames  # int(framerate / 100)
R_channel = np.array([])
L_channel = np.array([])
R_remnants = list(np.zeros((channels.shape[0], set_chunk_size)))
L_remnants = list(np.zeros((channels.shape[0], set_chunk_size)))
chunk_size = set_chunk_size

while chunk_size:
    R_pos = head_pos + [-head_width / 2 * np.cos(theta), np.sin(theta)]
    L_pos = head_pos + [head_width / 2 * np.cos(theta), np.sin(theta)]

    # Generate channels
    channels_chunk = channels[:, :chunk_size]
    channels = channels[:, chunk_size:]
    chunk_frames = len(channels_chunk)
    R_channel_chunk = np.zeros(chunk_frames)
    L_channel_chunk = np.zeros(chunk_frames)
    for position in positions:
        i = positions.index(position)
        channel_chunk = channels_chunk[i]
        R_phased_chunk = channel_chunk
        L_phased_chunk = channel_chunk
        R_r2 = (position[0] - R_pos[0]) ** 2 + (position[1] - R_pos[1]) ** 2
        L_r2 = (position[0] - L_pos[0]) ** 2 + (position[1] - L_pos[1]) ** 2
        phase_frames = int(abs(np.sqrt(R_r2) - np.sqrt(L_r2)) * framerate / speed_of_sound)
        if position[0] > 0:
            L_phased_chunk, L_remnants[i] = np.concatenate((L_remnants[i], L_phased_chunk[:-phase_frames])), \
                                            L_phased_chunk[chunk_size - phase_frames:]
        elif position[0] < 0:
            R_phased_chunk, R_remnants[i] = np.concatenate((R_remnants[i], R_phased_chunk[:-phase_frames])), \
                                            R_phased_chunk[chunk_size - phase_frames:]
        R_channel_chunk = R_channel_chunk + R_phased_chunk / R_r2
        L_channel_chunk = L_channel_chunk + L_phased_chunk / L_r2

    R_channel = np.concatenate((R_channel, R_channel_chunk))
    L_channel = np.concatenate((L_channel, L_channel_chunk))
    chunk_size = min(set_chunk_size, channels.shape[1])

    # Modifications
    theta += 0.03

# Write .wav file
wavfile.write('output.wav', framerate, np.asarray([R_channel, L_channel], dtype=np.int16).transpose())
