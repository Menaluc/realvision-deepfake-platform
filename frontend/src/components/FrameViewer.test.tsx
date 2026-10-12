import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { FrameViewer } from "./FrameViewer";

const frame = {
    index: 4,
    frameNumber: 33,
    timestamp: 1.32,
    imageUrl: "/api/analysis/abc/frames/4",
    heatmapUrl: "/api/analysis/abc/frames/4/attention"
};

function renderViewer(onClose = vi.fn()) {
    render(<FrameViewer frame={frame} frameCount={16} prediction="fake" onClose={onClose} />);
    return onClose;
}

describe("FrameViewer", () => {
    it("shows the enlarged frame with its heatmap", () => {
        renderViewer();

        expect(screen.getByRole("dialog")).toHaveTextContent("Frame 5 of 16 · 1.3s");
        expect(screen.getByAltText("Frame 5")).toHaveAttribute("src", frame.imageUrl);
        expect(screen.getByAltText("Grad-CAM heatmap")).toHaveAttribute("src", frame.heatmapUrl);
        expect(screen.getByText("Computing heatmap…")).toBeInTheDocument();

        fireEvent.load(screen.getByAltText("Grad-CAM heatmap"));

        expect(screen.getByText(/influenced the/)).toHaveTextContent("Highlighted areas influenced the Fake prediction.");
    });

    it("hides and shows the heatmap", async () => {
        const user = userEvent.setup();
        renderViewer();

        await user.click(screen.getByRole("button", { name: "Hide heatmap" }));
        expect(screen.queryByAltText("Grad-CAM heatmap")).not.toBeInTheDocument();

        await user.click(screen.getByRole("button", { name: "Show heatmap" }));
        expect(screen.getByAltText("Grad-CAM heatmap")).toBeInTheDocument();
    });

    it("closes with the close button and with Esc", async () => {
        const user = userEvent.setup();
        const onClose = renderViewer();

        expect(screen.getByRole("button", { name: "Close" })).toHaveFocus();

        await user.click(screen.getByRole("button", { name: "Close" }));
        await user.keyboard("{Escape}");

        expect(onClose).toHaveBeenCalledTimes(2);
    });

    it("explains when the heatmap could not be loaded", () => {
        renderViewer();

        fireEvent.error(screen.getByAltText("Grad-CAM heatmap"));

        expect(screen.getByText("Could not load the heatmap.")).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Hide heatmap" })).toBeDisabled();
    });
});
