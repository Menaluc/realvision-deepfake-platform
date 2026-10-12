import { requestJson } from "./client";
import type { PredictionResult } from "../types/prediction";

export function predictVideo(file: File): Promise<PredictionResult> {
    const formData = new FormData();
    formData.append("video", file);

    return requestJson<PredictionResult>("/api/predict", {
        method: "POST",
        body: formData
    }, "Analysis failed");
}
