// Shape of the prediction returned by POST /api/predict
// (mirrors the backend's prediction response)
export interface PredictionResult {
    prediction: "real" | "fake";
    confidence: number;
    probabilities: {
        real: number;
        fake: number;
    };
    // Id for fetching this analysis's sampled frames
    analysisId: string;
}
