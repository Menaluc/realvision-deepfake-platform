import type { PredictionResult } from "./prediction";

// The video the user picked, before it is analyzed
export interface VideoSelection {
    file: File;
    duration: number | null;
}

// Client-side details about the analyzed video (not returned by the server)
export interface VideoInfo {
    file: File;
    name: string;
    type: string;
    size: number;
    duration: number | null;
}

// One of the frames the model sampled from the video
export interface SampledFrame {
    index: number;
    frameNumber: number;
    // Seconds from the start of the video (null if the frame rate is unknown)
    timestamp: number | null;
    imageUrl: string;
    // Grad-CAM heatmap for the predicted class (transparent PNG)
    heatmapUrl: string;
}

// Frames are fetched after the prediction is shown
export type FramesState =
    | { status: "loading" }
    | { status: "loaded"; frames: SampledFrame[] }
    | { status: "error"; error: string };

// Everything known about one finished analysis
export interface Analysis {
    video: VideoInfo;
    prediction: PredictionResult;
    frames: FramesState;
    // Frame opened in the viewer
    selectedFrameIndex: number | null;
}
