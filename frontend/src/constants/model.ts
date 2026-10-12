// Fixed facts about the model the service runs. They are not sent by the
// server, so they must be updated here if the model changes.
export const MODEL = {
    // K_FRAMES in backend/app/ml/preprocess.py
    sampledFrames: 16,
    // IMG_SIZE in backend/app/ml/preprocess.py
    inputSize: 224,
    // backbone="tf_efficientnet_b0" in backend/app/ml/model_arch.py
    backbone: "EfficientNet-B0",
    // num_features of EfficientNet-B0 (channels of its last feature maps)
    featureSize: 1280,
    // emb_dim in backend/app/ml/model_arch.py
    embeddingSize: 256,
    // real, fake
    classes: 2
} as const;
