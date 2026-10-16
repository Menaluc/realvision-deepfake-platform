// Shape of GET /api/model (mirrors the backend's ModelResponse)
export interface ModelInfo {
    backbone: string;
    sampledFrames: number;
    inputSize: number;
    // Channels of the CNN's last feature maps
    featureSize: number;
    embeddingSize: number;
    classes: string[];
}

// Fetched once at startup; "unavailable" when the server has no model (503)
// or can't be reached
export type ModelInfoState =
    | { status: "loading" }
    | { status: "loaded"; info: ModelInfo }
    | { status: "unavailable" };
