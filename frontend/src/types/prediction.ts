// Shape of the prediction returned by POST /api/analyses
// (mirrors the backend's AnalysisResponse)
export interface PredictionResult {
    // Id for fetching this analysis's sampled frames
    id: string;
    prediction: "real" | "fake";
    confidence: number;
    probabilities: {
        real: number;
        fake: number;
    };
}
