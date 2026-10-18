import random
from dataclasses import dataclass

import cv2
import numpy as np

# torch must be loaded before decord: on Windows, importing torch after
# decord fails with "DLL initialization routine failed" (WinError 1114)
import torch
from decord import VideoReader, cpu

IMG_SIZE = 224
K_FRAMES = 16

MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def sample_frame_indices(num_frames_total, k=K_FRAMES, strategy="uniform"):
    if num_frames_total <= 0:
        return np.zeros((k,), dtype=np.int64)

    if strategy == "uniform":
        indices = np.linspace(0, num_frames_total - 1, k).round().astype(np.int64)

        return indices

    if strategy == "random":
        if num_frames_total >= k:
            start = random.randint(0, num_frames_total - k)
            return np.arange(start, start + k, dtype=np.int64)

        indices = np.arange(num_frames_total, dtype=np.int64)

        padding = np.full((k - num_frames_total,), num_frames_total - 1, dtype=np.int64)

        return np.concatenate([indices, padding])

    raise ValueError("Unknown strategy")


def center_crop_resize(frames, out_size=IMG_SIZE):
    output = []

    for frame in frames:
        height, width, _ = frame.shape

        scale = out_size / min(height, width)

        new_height = int(height * scale)
        new_width = int(width * scale)

        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        height, width, _ = frame.shape

        y0 = (height - out_size) // 2
        x0 = (width - out_size) // 2

        frame = frame[y0 : y0 + out_size, x0 : x0 + out_size]

        output.append(frame)

    return np.stack(output, axis=0)


@dataclass
class SampledVideo:
    # Model input, normalized: (K_FRAMES, 3, IMG_SIZE, IMG_SIZE)
    tensor: torch.Tensor
    # The same frames as RGB images: (K_FRAMES, IMG_SIZE, IMG_SIZE, 3), uint8
    frames: np.ndarray
    # Position of each sampled frame in the original video
    frame_numbers: list[int]
    fps: float


def frames_to_tensor(frames):
    video_tensor = torch.from_numpy(frames).float() / 255.0

    video_tensor = video_tensor.permute(0, 3, 1, 2)

    mean = torch.tensor(MEAN).view(1, 3, 1, 1)
    std = torch.tensor(STD).view(1, 3, 1, 1)

    return (video_tensor - mean) / std


def preprocess_video(video_path):
    video_reader = VideoReader(video_path, ctx=cpu(0))

    number_of_frames = len(video_reader)

    indices = sample_frame_indices(number_of_frames, k=K_FRAMES, strategy="uniform")

    frames = video_reader.get_batch(indices).asnumpy()

    frames = center_crop_resize(frames, out_size=IMG_SIZE)

    return SampledVideo(
        tensor=frames_to_tensor(frames),
        frames=frames,
        frame_numbers=indices.tolist(),
        fps=float(video_reader.get_avg_fps()),
    )
