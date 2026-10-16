import type { FramesState } from "../types/analysis";
import { formatTimestamp } from "../utils/format";

interface FrameStripProps {
    frames: FramesState;
    // From /api/model; null when unknown, then no placeholders are drawn
    sampledFrames: number | null;
    onSelectFrame: (index: number) => void;
}

export function FrameStrip({ frames, sampledFrames, onSelectFrame }: FrameStripProps) {
    return (
        <section className="card frames-card">
            <div className="eyebrow">Sampled Frames</div>
            <p className="frames-hint">The frames the model analyzed, cropped to its 224×224 input. Click a frame to see where the model looked.</p>

            {frames.status === "error" ? (
                <div className="frames-error">{frames.error}</div>
            ) : frames.status === "loading" && sampledFrames === null ? (
                <div className="frames-loading">Loading frames…</div>
            ) : (
                <div className="frames-grid">
                    {frames.status === "loading"
                        ? Array.from({ length: sampledFrames ?? 0 }, (_, i) => (
                            <div key={i} className="frame-placeholder" data-testid="frame-placeholder" />
                        ))
                        : frames.frames.map((frame) => (
                            <figure key={frame.index} className="frame">
                                <button type="button" className="frame-button" onClick={() => onSelectFrame(frame.index)}>
                                    <img src={frame.imageUrl} alt={`Frame ${frame.index + 1}`} />
                                </button>
                                <figcaption>{formatTimestamp(frame.timestamp)}</figcaption>
                            </figure>
                        ))}
                </div>
            )}
        </section>
    );
}
