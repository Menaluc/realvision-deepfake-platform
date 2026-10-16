import torch.nn as nn
import timm


class VideoOnlyBaseline(nn.Module):
    def __init__(self, backbone="tf_efficientnet_b0", emb_dim=256):
        super().__init__()

        # CNN feature extractor for each frame
        self.cnn = timm.create_model(
            backbone,
            pretrained=False,
            num_classes=0,
            global_pool=""
        )

        # Number of features returned by the CNN
        ch = self.cnn.num_features

        # Convert spatial feature maps into one feature vector
        self.pool = nn.AdaptiveAvgPool2d(1)

        # Reduce feature size to 256
        self.proj = nn.Linear(ch, emb_dim)

        # Final classifier: real / fake
        self.classifier = nn.Linear(emb_dim, 2)

    def forward(self, v):
        # v shape: (B, T, C, H, W)
        B, T, C, H, W = v.shape

        # Treat every frame as a separate image
        x = v.view(B * T, C, H, W)

        # Extract features from every frame
        feat = self.cnn(x)

        # Pool spatial feature maps if needed
        if feat.dim() == 4:
            feat = self.pool(feat).flatten(1)

        # Restore video structure and average the frame features
        feat = feat.view(B, T, -1).mean(dim=1)

        # Create video embedding
        feat = self.proj(feat)

        # Return two logits: real and fake
        return self.classifier(feat)
