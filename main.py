"""This is the doc file.
All distances in m."""

import numpy as np
from scipy.io import wavfile
import wave
import struct

speed_of_sound = 343
framerate = 44100
head_width = 0.15
positions = [[3, 0]]
audio_files = ['5.wav']


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
channels = np.array([np.pad(channel, (0, frames - len(channel)), 'constant') for channel in channels])

theta = 0
head_pos = np.array([0, 0])
chunk_size = np.int(framerate / 100)
R_channel = np.array([])
L_channel = np.array([])
R_remnants = np.zeros((channels.shape[0], chunk_size))
L_remnants = np.zeros((channels.shape[0], chunk_size))

while chunk_size <= channels.shape[1]:
    R_pos = head_pos + [-head_width / 2 * np.cos(theta), np.sin(theta)]
    L_pos = head_pos + [head_width / 2 * np.cos(theta), np.sin(theta)]

    # Generate channels
    channels_chunk = channels[:, :chunk_size]
    channels = channels[:, chunk_size:]
    R_channel_chunk = np.zeros(chunk_size)
    L_channel_chunk = np.zeros(chunk_size)

    for position in positions:
        i = positions.index(position)
        channel_chunk = channels_chunk[i]
        R_phased_chunk = channel_chunk
        L_phased_chunk = channel_chunk

        R_r2 = (position[0] - R_pos[0]) ** 2 + (position[1] - R_pos[1]) ** 2
        L_r2 = (position[0] - L_pos[0]) ** 2 + (position[1] - L_pos[1]) ** 2

        # Add phase delay between channels
        phase_frames = np.int(np.abs(np.sqrt(R_r2) - np.sqrt(L_r2)) * framerate / speed_of_sound)
        if position[0] > 0:
            L_phased_chunk = np.concatenate((L_remnants[i, phase_frames:], L_phased_chunk[chunk_size - phase_frames:]))
            L_remnants[i] = np.pad(channel_chunk[:phase_frames], (0, chunk_size - phase_frames), 'constant')
        elif position[0] < 0:
            R_phased_chunk = np.concatenate((R_remnants[i, phase_frames:], R_phased_chunk[chunk_size - phase_frames:]))
            R_remnants[i] = np.pad(channel_chunk[:phase_frames], (0, chunk_size - phase_frames), 'constant')

        R_channel_chunk = R_channel_chunk + R_phased_chunk / R_r2
        L_channel_chunk = L_channel_chunk + L_phased_chunk / L_r2

    R_channel = np.append(R_channel, R_channel_chunk)
    L_channel = np.append(L_channel, L_channel_chunk)

    # Modifications
    theta += 0.03

# Write .wav file
wavfile.write('output.wav', framerate, np.asarray([R_channel, L_channel], dtype=np.int16).transpose())
