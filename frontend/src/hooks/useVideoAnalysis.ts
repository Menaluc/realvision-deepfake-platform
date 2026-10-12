import { useReducer } from "react";
import { getFrames } from "../api/analysis";
import { predictVideo } from "../api/predict";
import type { PredictionResult } from "../types/prediction";
import { readDuration } from "../utils/video";
import { analysisReducer, initialAnalysisState } from "./analysisReducer";

// Owns the upload → analyze → result flow
export function useVideoAnalysis() {
    const [state, dispatch] = useReducer(analysisReducer, initialAnalysisState);

    async function selectFile(file: File) {
        dispatch({ type: "fileSelected", file });
        const duration = await readDuration(file);
        dispatch({ type: "durationRead", file, duration });
    }

    async function analyze() {
        if (state.status === "done" || state.status === "analyzing") return;

        const file = state.selection?.file;
        if (!file) {
            dispatch({ type: "analysisFailed", error: "Please select a video first" });
            return;
        }

        dispatch({ type: "analysisStarted" });

        let prediction: PredictionResult;

        try {
            prediction = await predictVideo(file);
            dispatch({ type: "analysisSucceeded", file, prediction });
        } catch (error) {
            dispatch({
                type: "analysisFailed",
                error: error instanceof Error ? error.message : "Analysis failed"
            });
            return;
        }

        await loadFrames(prediction.analysisId);
    }

    async function loadFrames(analysisId: string) {
        try {
            const frames = await getFrames(analysisId);
            dispatch({ type: "framesLoaded", analysisId, frames });
        } catch (error) {
            dispatch({
                type: "framesFailed",
                analysisId,
                error: error instanceof Error ? error.message : "Could not load frames"
            });
        }
    }

    function reset() {
        dispatch({ type: "reset" });
    }

    function selectFrame(index: number) {
        dispatch({ type: "frameSelected", index });
    }

    function closeFrame() {
        dispatch({ type: "frameClosed" });
    }

    return { state, selectFile, analyze, reset, selectFrame, closeFrame };
}
