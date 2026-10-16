import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useModelInfo } from "./useModelInfo";

const info = {
    backbone: "tf_efficientnet_b0",
    sampledFrames: 16,
    inputSize: 224,
    featureSize: 1280,
    embeddingSize: 256,
    classes: ["real", "fake"]
};

function json(status: number, body: unknown) {
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("useModelInfo", () => {
    it("loads the model details from /api/model", async () => {
        const fetchMock = vi.fn(async () => json(200, info));
        vi.stubGlobal("fetch", fetchMock);

        const { result } = renderHook(() => useModelInfo());

        expect(result.current).toEqual({ status: "loading" });
        await waitFor(() => expect(result.current).toEqual({ status: "loaded", info }));
        expect(fetchMock).toHaveBeenCalledWith("/api/model", undefined);
    });

    it("is unavailable when the server has no model", async () => {
        vi.stubGlobal("fetch", vi.fn(async () =>
            json(503, { error: { code: "MODEL_UNAVAILABLE", message: "The detection model is not loaded." } })
        ));

        const { result } = renderHook(() => useModelInfo());

        await waitFor(() => expect(result.current).toEqual({ status: "unavailable" }));
    });

    it("is unavailable when the server can't be reached", async () => {
        vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("Failed to fetch"); }));

        const { result } = renderHook(() => useModelInfo());

        await waitFor(() => expect(result.current).toEqual({ status: "unavailable" }));
    });
});
