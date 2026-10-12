import { MODEL } from "../constants/model";
import type { FramesState } from "../types/analysis";
import { formatTimestamp } from "../utils/format";

interface FrameStripProps {
    frames: FramesState;
    onSelectFrame: (index: number) => void;
}

export function FrameStrip({ frames, onSelectFrame }: FrameStripProps) {
    return (
        <section className="card frames-card">
            <div className="eyebrow">Sampled Frames</div>
            <p className="frames-hint">The frames the model analyzed, cropped to its 224×224 input. Click a frame to see where the model looked.</p>

            {frames.status === "error" ? (
                <div className="frames-error">{frames.error}</div>
            ) : (
                <div className="frames-grid">
                    {frames.status === "loading"
                        ? Array.from({ length: MODEL.sampledFrames }, (_, i) => (
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
