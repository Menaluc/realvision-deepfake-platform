import { describe, expect, it, vi } from "vitest";
import { requestJson } from "./client";

function stubResponse(response: Response) {
    vi.stubGlobal("fetch", vi.fn(async () => response));
}

function json(status: number, body: unknown) {
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("requestJson", () => {
    it("returns the body of a successful response", async () => {
        stubResponse(json(201, { id: "abc" }));

        await expect(requestJson("/api/x")).resolves.toEqual({ id: "abc" });
    });

    it("throws the message from the backend's error format", async () => {
        stubResponse(json(503, { error: { code: "MODEL_UNAVAILABLE", message: "The detection model is not loaded." } }));

        await expect(requestJson("/api/x", undefined, "Fallback")).rejects.toThrow("The detection model is not loaded.");
    });

    it("falls back when the error body is not JSON", async () => {
        // What the dev proxy returns when the backend is down
        stubResponse(new Response("<html>Bad Gateway</html>", { status: 502 }));

        await expect(requestJson("/api/x", undefined, "Fallback")).rejects.toThrow("Fallback");
    });

    it("falls back when the error body has no message", async () => {
        stubResponse(json(500, { detail: "something else" }));

        await expect(requestJson("/api/x", undefined, "Fallback")).rejects.toThrow("Fallback");
    });
});
