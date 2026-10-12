import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FrameStrip } from "./FrameStrip";

describe("FrameStrip", () => {
    it("shows placeholders while the frames load", () => {
        render(<FrameStrip frames={{ status: "loading" }} onSelectFrame={vi.fn()} />);

        expect(screen.getAllByTestId("frame-placeholder")).toHaveLength(16);
        expect(screen.queryByRole("img")).not.toBeInTheDocument();
    });

    it("shows the error when the frames could not be loaded", () => {
        render(<FrameStrip frames={{ status: "error", error: "Analysis not found" }} onSelectFrame={vi.fn()} />);

        expect(screen.getByText("Analysis not found")).toBeInTheDocument();
    });

    it("reports which frame was clicked", () => {
        const onSelectFrame = vi.fn();
        const frames = [0, 1].map((index) => ({
            index,
            frameNumber: index * 20,
            timestamp: index * 0.8,
            imageUrl: `/frames/${index}`,
            heatmapUrl: `/frames/${index}/attention`
        }));

        render(<FrameStrip frames={{ status: "loaded", frames }} onSelectFrame={onSelectFrame} />);
        fireEvent.click(screen.getByAltText("Frame 2"));

        expect(onSelectFrame).toHaveBeenCalledWith(1);
    });
});
