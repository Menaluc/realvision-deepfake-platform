import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MAX_UPLOAD_BYTES } from "../constants/upload";
import type { PredictionResult } from "../types/prediction";
import { useVideoAnalysis } from "./useVideoAnalysis";

const video = new File(["fake video content"], "clip.mp4", { type: "video/mp4" });

const analysisId = "3f8e2a4c-1b6d-4e9a-8c7f-2d5b9e0a1c34";

const fakePrediction: PredictionResult = {
    prediction: "fake",
    confidence: 0.92,
    probabilities: { real: 0.08, fake: 0.92 },
    id: analysisId
};

const fakeFrames = [
    { index: 0, frameNumber: 0, timestamp: 0 },
    { index: 1, frameNumber: 20, timestamp: 0.8 }
];

function jsonResponse(status: number, body: unknown) {
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

// The backend's error format
function apiError(code: string, message: string) {
    return { error: { code, message } };
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
            "/api/analyses": () => jsonResponse(201, fakePrediction),
            [`/api/analyses/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
        expect(url).toBe("/api/analyses");
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
                            imageUrl: `/api/analyses/${analysisId}/frames/0`,
                            heatmapUrl: `/api/analyses/${analysisId}/frames/0/attention`
                        },
                        {
                            ...fakeFrames[1],
                            imageUrl: `/api/analyses/${analysisId}/frames/1`,
                            heatmapUrl: `/api/analyses/${analysisId}/frames/1/attention`
                        }
                    ]
                },
                selectedFrameIndex: null
            }
        });
    });

    it("opens and closes a sampled frame", async () => {
        stubFetch({
            "/api/analyses": () => jsonResponse(201, fakePrediction),
            [`/api/analyses/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
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
            "/api/analyses": () => jsonResponse(201, fakePrediction),
            [`/api/analyses/${analysisId}/frames`]: () => jsonResponse(404, apiError("ANALYSIS_NOT_FOUND", "The analysis does not exist or has expired."))
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        expect(result.current.state).toMatchObject({
            status: "done",
            analysis: {
                prediction: fakePrediction,
                frames: { status: "error", error: "The analysis does not exist or has expired." }
            }
        });
    });

    it("keeps the selection and shows the server error when the request fails", async () => {
        stubFetch({
            "/api/analyses": () => jsonResponse(415, apiError("UNSUPPORTED_MEDIA_TYPE", "The file is not a video."))
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());

        expect(result.current.state).toMatchObject({
            status: "error",
            error: "The file is not a video.",
            selection: { file: video }
        });
    });

    it("rejects a file over the upload limit without sending it", async () => {
        const fetchMock = stubFetch({});
        const tooLarge = new File(["x"], "big.mp4", { type: "video/mp4" });
        Object.defineProperty(tooLarge, "size", { value: MAX_UPLOAD_BYTES + 1 });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(tooLarge); });
        await act(() => result.current.analyze());

        expect(fetchMock).not.toHaveBeenCalled();
        expect(result.current.state).toMatchObject({
            status: "error",
            error: "The video is larger than the 20 MB limit.",
            selection: { file: tooLarge }
        });
    });

    it("sends a file of exactly the upload limit", async () => {
        const fetchMock = stubFetch({
            "/api/analyses": () => jsonResponse(201, fakePrediction),
            [`/api/analyses/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
        });
        const atLimit = new File(["x"], "limit.mp4", { type: "video/mp4" });
        Object.defineProperty(atLimit, "size", { value: MAX_UPLOAD_BYTES });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(atLimit); });
        await act(() => result.current.analyze());

        expect(fetchMock).toHaveBeenCalledWith("/api/analyses", expect.anything());
        expect(result.current.state.status).toBe("done");
    });

    it("returns to idle on reset", async () => {
        stubFetch({
            "/api/analyses": () => jsonResponse(201, fakePrediction),
            [`/api/analyses/${analysisId}/frames`]: () => jsonResponse(200, { frames: fakeFrames })
        });
        const { result } = renderHook(() => useVideoAnalysis());

        act(() => { result.current.selectFile(video); });
        await act(() => result.current.analyze());
        act(() => result.current.reset());

        expect(result.current.state).toEqual({ status: "idle", selection: null });
    });
});
