import { useEffect, useEffectEvent, useRef, useState } from "react";
import type { SampledFrame } from "../types/analysis";
import type { PredictionResult } from "../types/prediction";
import { formatTimestamp } from "../utils/format";
import { CloseIcon } from "./icons";

interface FrameViewerProps {
    frame: SampledFrame;
    frameCount: number;
    prediction: PredictionResult["prediction"];
    onClose: () => void;
}

type HeatmapStatus = "loading" | "loaded" | "error";

// One sampled frame, enlarged, with its Grad-CAM heatmap on top
export function FrameViewer({ frame, frameCount, prediction, onClose }: FrameViewerProps) {
    const [showHeatmap, setShowHeatmap] = useState(true);
    const [heatmapStatus, setHeatmapStatus] = useState<HeatmapStatus>("loading");
    const closeButtonRef = useRef<HTMLButtonElement>(null);

    // Reads the latest onClose without re-running the effect below
    const handleEscape = useEffectEvent(() => onClose());

    // Esc closes; focus starts on the close button; the page behind doesn't scroll
    useEffect(() => {
        function handleKeyDown(e: KeyboardEvent) {
            if (e.key === "Escape") handleEscape();
        }

        document.addEventListener("keydown", handleKeyDown);
        closeButtonRef.current?.focus();

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";

        return () => {
            document.removeEventListener("keydown", handleKeyDown);
            document.body.style.overflow = previousOverflow;
        };
    }, []);

    const label = prediction === "fake" ? "Fake" : "Real";

    return (
        <div className="viewer-backdrop">
            <div className="card viewer" role="dialog" aria-modal="true" aria-labelledby="viewer-title">
                <div className="viewer-header">
                    <div id="viewer-title" className="eyebrow">
                        Frame {frame.index + 1} of {frameCount} · {formatTimestamp(frame.timestamp)}
                    </div>
                    <button ref={closeButtonRef} type="button" className="viewer-close" aria-label="Close" onClick={onClose}>
                        <CloseIcon />
                    </button>
                </div>

                <div className="viewer-image">
                    <img src={frame.imageUrl} alt={`Frame ${frame.index + 1}`} />
                    {showHeatmap && heatmapStatus !== "error" && (
                        <img
                            className="viewer-heatmap"
                            src={frame.heatmapUrl}
                            alt="Grad-CAM heatmap"
                            onLoad={() => setHeatmapStatus("loaded")}
                            onError={() => setHeatmapStatus("error")}
                        />
                    )}
                </div>

                <p className="viewer-caption">
                    {heatmapStatus === "error"
                        ? <span className="frames-error">Could not load the heatmap.</span>
                        : showHeatmap && heatmapStatus === "loading"
                            ? "Computing heatmap…"
                            : <>Highlighted areas influenced the <b>{label}</b> prediction.</>}
                </p>

                <button
                    type="button"
                    className="viewer-toggle"
                    aria-pressed={showHeatmap}
                    disabled={heatmapStatus === "error"}
                    onClick={() => setShowHeatmap((value) => !value)}
                >
                    {showHeatmap ? "Hide heatmap" : "Show heatmap"}
                </button>
            </div>
        </div>
    );
}
