import numpy as np

from app.ml.preprocess import (
    IMG_SIZE,
    K_FRAMES,
    center_crop_resize,
    frames_to_tensor,
    sample_frame_indices,
)


def test_samples_frames_uniformly_including_first_and_last():
    indices = sample_frame_indices(301)

    assert len(indices) == K_FRAMES
    assert indices[0] == 0
    assert indices[-1] == 300
    assert np.all(np.diff(indices) > 0)


def test_center_crop_resize_returns_square_frames():
    frames = np.zeros((2, 360, 640, 3), dtype=np.uint8)

    output = center_crop_resize(frames)

    assert output.shape == (2, IMG_SIZE, IMG_SIZE, 3)


def test_frames_to_tensor_returns_normalized_channels_first_tensor():
    frames = np.full((K_FRAMES, IMG_SIZE, IMG_SIZE, 3), 255, dtype=np.uint8)

    tensor = frames_to_tensor(frames)

    assert tuple(tensor.shape) == (K_FRAMES, 3, IMG_SIZE, IMG_SIZE)
    # A white pixel in the red channel: (1 - 0.485) / 0.229
    assert abs(tensor[0, 0, 0, 0].item() - (1 - 0.485) / 0.229) < 1e-5
