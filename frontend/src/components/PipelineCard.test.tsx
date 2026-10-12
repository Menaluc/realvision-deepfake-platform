import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Analysis, FramesState } from "../types/analysis";
import { PipelineCard } from "./PipelineCard";

const loadedFrames: FramesState = {
    status: "loaded",
    frames: Array.from({ length: 16 }, (_, i) => ({
        index: i,
        frameNumber: i * 26,
        timestamp: i * 0.88,
        imageUrl: `/frames/${i}`,
        heatmapUrl: `/frames/${i}/attention`
    }))
};

function makeAnalysis(duration: number | null, frames: FramesState): Analysis {
    return {
        video: { file: new File([""], "clip.mp4"), name: "clip.mp4", type: "video/mp4", size: 1, duration },
        prediction: {
            prediction: "fake",
            confidence: 0.78,
            probabilities: { real: 0.22, fake: 0.78 },
            analysisId: "3f8e2a4c-1b6d-4e9a-8c7f-2d5b9e0a1c34"
        },
        frames,
        selectedFrameIndex: null
    };
}

describe("PipelineCard", () => {
    it("shows each step with this analysis's values", () => {
        render(<PipelineCard analysis={makeAnalysis(13.24, loadedFrames)} />);

        expect(screen.getAllByRole("listitem")).toHaveLength(6);
        expect(screen.getByText("13.2s long")).toBeInTheDocument();
        expect(screen.getByText("16 frames")).toBeInTheDocument();
        expect(screen.getByText("Evenly spaced, 0.0s to 13.2s")).toBeInTheDocument();
        expect(screen.getByText("EfficientNet-B0")).toBeInTheDocument();
        expect(screen.getByText("Each 224×224 frame → 1,280 features")).toBeInTheDocument();
        expect(screen.getByText("16 × 1,280 → 1,280")).toBeInTheDocument();
        expect(screen.getByText("1,280 → 256 → 2")).toBeInTheDocument();
        expect(screen.getByText("Fake")).toBeInTheDocument();
        expect(screen.getByText("Real 22%")).toBeInTheDocument();
        expect(screen.getByText("Fake 78%")).toBeInTheDocument();
        expect(screen.getAllByRole("presentation")).toHaveLength(4);
    });

    it("falls back to the last frame's time without calling it the video length", () => {
        render(<PipelineCard analysis={makeAnalysis(null, loadedFrames)} />);

        expect(screen.getByText("Last frame at 13.2s")).toBeInTheDocument();
        expect(screen.getByText("Exact length unavailable in this browser")).toBeInTheDocument();
        expect(screen.queryByText(/long$/)).not.toBeInTheDocument();
    });

    it("shows placeholders while the frames load", () => {
        render(<PipelineCard analysis={makeAnalysis(null, { status: "loading" })} />);

        expect(screen.getAllByTestId("pipeline-thumb-placeholder")).toHaveLength(4);
        expect(screen.getByText("Evenly spaced across the video")).toBeInTheDocument();
        expect(screen.getByText("—")).toBeInTheDocument();
    });
});
