import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { PredictionResult } from "../types/prediction";
import { useVideoAnalysis } from "./useVideoAnalysis";

const video = new File(["fake video content"], "clip.mp4", { type: "video/mp4" });

const analysisId = "3f8e2a4c-1b6d-4e9a-8c7f-2d5b9e0a1c34";

const fakePrediction: PredictionResult = {
    prediction: "fake",
    confidence: 0.92,
    probabilities: { real: 0.08, fake: 0.92 },
    analysisId
};

const fakeFrames = [
    { index: 0, frameNumber: 0, timestamp: 0 },
    { index: 1, frameNumber: 20, timestamp: 0.8 }
];

function jsonResponse(status: number, body: unknown) {
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

// Answers each API path with its own response
function stubFetch(routes: Record<string, () => Response>) {
    const fetchMock = vi.fn(async (url: string) => {
        const route = routes[url];
        if (!route) throw new Error("Unexpected request: " + url);
        return route();
    });
    vi.stubGlobal("fetch", fetchMock);
    return fetchMock;
}

describe("useVideoAnalysis", () => {
    it("starts idle with no selection", () => {
        const { result } = renderHook(() => useVideoAnalysis());

        expect(result.current.state).toEqual({ status: "idle", selection: null });
    });

    it("reports an error when analyzing without a file", async () => {
        const fetchMock = stubFetch({});
        const { result } = renderHook(() => useVideoAnalysis());

        await act(() => result.current.analyze());

        expect(result.current.state).toMatchObject({ status: "error", error: "Please select a video first" });
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it("uploads the selected file, stores the analysis and loads its frames", async () => {
        const fetchMock = stubFetch({
            "/api/predict": () => jsonResponse(200, fakePrediction),
            [`/api/analysis/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
        expect(url).toBe("/api/predict");
        expect((init.body as FormData).get("video")).toBe(video);

        expect(result.current.state).toEqual({
            status: "done",
            analysis: {
                video: { file: video, name: "clip.mp4", type: "video/mp4", size: video.size, duration: null },
                prediction: fakePrediction,
                frames: {
                    status: "loaded",
                    frames: [
                        {
                            ...fakeFrames[0],
                            imageUrl: `/api/analysis/${analysisId}/frames/0`,
                            heatmapUrl: `/api/analysis/${analysisId}/frames/0/attention`
                        },
                        {
                            ...fakeFrames[1],
                            imageUrl: `/api/analysis/${analysisId}/frames/1`,
                            heatmapUrl: `/api/analysis/${analysisId}/frames/1/attention`
                        }
                    ]
                },
                selectedFrameIndex: null
            }
        });
    });

    it("opens and closes a sampled frame", async () => {
        stubFetch({
            "/api/predict": () => jsonResponse(200, fakePrediction),
            [`/api/analysis/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        act(() => result.current.selectFrame(1));
        expect(result.current.state).toMatchObject({ analysis: { selectedFrameIndex: 1 } });

        act(() => result.current.closeFrame());
        expect(result.current.state).toMatchObject({ analysis: { selectedFrameIndex: null } });
    });

    it("keeps the result when the frames fail to load", async () => {
        stubFetch({
            "/api/predict": () => jsonResponse(200, fakePrediction),
            [`/api/analysis/${analysisId}/frames`]: () => jsonResponse(404, { error: "Analysis not found" })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        expect(result.current.state).toMatchObject({
            status: "done",
            analysis: {
                prediction: fakePrediction,
                frames: { status: "error", error: "Analysis not found" }
            }
        });
    });

    it("keeps the selection and shows the server error when the request fails", async () => {
        stubFetch({
            "/api/predict": () => jsonResponse(413, { error: "Maximum file size is 20MB" })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        expect(result.current.state).toMatchObject({
            status: "error",
            error: "Maximum file size is 20MB",
            selection: { file: video }
        });
    });

    it("returns to idle on reset", async () => {
        stubFetch({
            "/api/predict": () => jsonResponse(200, fakePrediction),
            [`/api/analysis/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());
        act(() => result.current.reset());

        expect(result.current.state).toEqual({ status: "idle", selection: null });
    });
});
