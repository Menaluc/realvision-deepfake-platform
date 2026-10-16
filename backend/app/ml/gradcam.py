import cv2
import numpy as np
import torch
import torch.nn.functional as F


def compute_gradcam(model, video_tensor, target_class):
    """Grad-CAM heatmaps for every sampled frame of one video.

    Targets the output of model.cnn: the last convolutional block of
    EfficientNet-B0 (conv_head + BN + SiLU), shaped (T, 1280, 7, 7).

    video_tensor: (T, 3, H, W) normalized frames, as fed to the model
    target_class: index of the class to explain (0 = real, 1 = fake)

    Returns a (T, H, W) float32 array in [0, 1]. All frames share one
    normalization, so a weak frame stays weak next to a strong one.
    """
    captured = {}

    def save_features(module, inputs, output):
        captured["features"] = output

    handle = model.cnn.register_forward_hook(save_features)

    try:
        device = next(model.parameters()).device

        # Inference runs under no_grad elsewhere; Grad-CAM needs gradients
        with torch.enable_grad():
            logits = model(video_tensor.unsqueeze(0).to(device))
            features = captured["features"]

            # Gradients of the class score with respect to the feature maps only
            # (the model's own weights are left untouched)
            (gradients,) = torch.autograd.grad(logits[0, target_class], features)

    finally:
        handle.remove()

    # Channel importance: average gradient over each 7x7 map
    weights = gradients.mean(dim=(2, 3), keepdim=True)

    # Weighted sum of the feature maps; keep only positive evidence
    cam = F.relu((weights * features).sum(dim=1, keepdim=True))

    # Upsample 7x7 → frame size
    cam = F.interpolate(
        cam, size=video_tensor.shape[-2:], mode="bilinear", align_corners=False
    )[:, 0]

    # Joint normalization across all frames
    max_value = cam.max()

    if max_value > 0:
        cam = cam / max_value

    return cam.detach().cpu().numpy().astype(np.float32)


def heatmap_to_png(heatmap):
    """Encodes one (H, W) heatmap in [0, 1] as a colored, transparent PNG.

    Opacity follows the heat, so regions that didn't matter stay see-through
    when the PNG is laid over the frame.
    """
    intensity = (np.clip(heatmap, 0, 1) * 255).astype(np.uint8)

    colors = cv2.applyColorMap(intensity, cv2.COLORMAP_JET)

    # OpenCV writes BGRA
    ok, png = cv2.imencode(".png", np.dstack([colors, intensity]))

    if not ok:
        raise RuntimeError("Failed to encode heatmap")

    return png.tobytes()
