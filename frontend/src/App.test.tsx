import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import App from "./App";

const analysisId = "3f8e2a4c-1b6d-4e9a-8c7f-2d5b9e0a1c34";

function jsonResponse(body: unknown, status = 200) {
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

it("selects a video, analyzes it, opens a frame, and resets", async () => {
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
        if (url === "/api/model") {
            return jsonResponse({
                backbone: "tf_efficientnet_b0",
                sampledFrames: 16,
                inputSize: 224,
                featureSize: 1280,
                embeddingSize: 256,
                classes: ["real", "fake"]
            });
        }

        if (url === "/api/analyses") {
            return jsonResponse({
                id: analysisId,
                prediction: "real",
                confidence: 0.87,
                probabilities: { real: 0.87, fake: 0.13 }
            }, 201);
        }

        return jsonResponse({
            frames: Array.from({ length: 16 }, (_, i) => ({ index: i, frameNumber: i * 20, timestamp: i * 0.8 }))
        });
    }));
    const user = userEvent.setup();
    const video = new File(["fake video content"], "clip.mp4", { type: "video/mp4" });

    render(<App />);

    await user.upload(screen.getByLabelText("Video file"), video);
    expect(screen.getByText("clip.mp4")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Analyze Video" }));

    expect(await screen.findByText("Analysis Result")).toBeInTheDocument();
    expect(screen.getByText("Real", { selector: ".verdict-badge span" })).toBeInTheDocument();
    expect(screen.getByText("87%")).toBeInTheDocument();
    expect(screen.getByText("MP4")).toBeInTheDocument();

    const firstFrame = await screen.findByAltText("Frame 1");
    expect(firstFrame).toHaveAttribute("src", `/api/analyses/${analysisId}/frames/0`);
    expect(screen.getAllByRole("img", { name: /^Frame \d+$/ })).toHaveLength(16);
    expect(screen.getByText("0.8s")).toBeInTheDocument();

    expect(screen.getByText("How the model decided")).toBeInTheDocument();
    expect(screen.getByText("Real 87%")).toBeInTheDocument();
    // Model details come from /api/model
    expect(screen.getByText("tf_efficientnet_b0")).toBeInTheDocument();

    await user.click(screen.getByAltText("Frame 5"));
    expect(screen.getByRole("dialog")).toHaveTextContent("Frame 5 of 16");
    expect(screen.getByAltText("Grad-CAM heatmap")).toHaveAttribute(
        "src",
        `/api/analyses/${analysisId}/frames/4/attention`
    );

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Analyze another video/ }));

    expect(screen.getByText("Upload a video")).toBeInTheDocument();
    expect(screen.queryByText("Analysis Result")).not.toBeInTheDocument();
});

it("shows the server's message when the model is unavailable", async () => {
    const unavailable = { error: { code: "MODEL_UNAVAILABLE", message: "The detection model is not loaded. Try again later." } };
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(unavailable, 503)));
    const user = userEvent.setup();

    render(<App />);

    await user.upload(screen.getByLabelText("Video file"), new File(["x"], "clip.mp4", { type: "video/mp4" }));
    await user.click(screen.getByRole("button", { name: "Analyze Video" }));

    expect(await screen.findByText("The detection model is not loaded. Try again later.")).toBeInTheDocument();
    expect(screen.queryByText("Analysis Result")).not.toBeInTheDocument();
});
