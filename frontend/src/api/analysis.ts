import { requestJson } from "./client";
import type { SampledFrame } from "../types/analysis";

type FrameInfo = Omit<SampledFrame, "imageUrl" | "heatmapUrl">;

// The frames the model sampled for an analysis, with a URL for each image
export async function getFrames(analysisId: string): Promise<SampledFrame[]> {
    const { frames } = await requestJson<{ frames: FrameInfo[] }>(
        `/api/analysis/${analysisId}/frames`,
        undefined,
        "Could not load frames"
    );

    return frames.map((frame) => {
        const imageUrl = `/api/analysis/${analysisId}/frames/${frame.index}`;
        return { ...frame, imageUrl, heatmapUrl: `${imageUrl}/attention` };
    });
}
