import { FrameStrip } from "../components/FrameStrip";
import { FrameViewer } from "../components/FrameViewer";
import { ArrowLeftIcon } from "../components/icons";
import { MetaGrid } from "../components/MetaGrid";
import { PipelineCard } from "../components/PipelineCard";
import { VerdictBadge } from "../components/VerdictBadge";
import { VideoPreview } from "../components/VideoPreview";
import type { Analysis } from "../types/analysis";
import { formatPercent } from "../utils/format";
import "../styles/result.css";

interface ResultViewProps {
    analysis: Analysis;
    onReset: () => void;
    onSelectFrame: (index: number) => void;
    onCloseFrame: () => void;
}

export function ResultView({ analysis, onReset, onSelectFrame, onCloseFrame }: ResultViewProps) {
    const { video, prediction, frames, selectedFrameIndex } = analysis;
    const selectedFrame = frames.status === "loaded" && selectedFrameIndex !== null
        ? frames.frames[selectedFrameIndex]
        : null;

    return (
        <>
            <div className="hero" id="resultHero">
                <VideoPreview file={video.file} />

                <div className="card" id="resultCard">
                    <div className="eyebrow">Analysis Result</div>

                    <VerdictBadge prediction={prediction.prediction} />

                    <div className="confidence-line">Confidence: <b>{formatPercent(prediction.confidence)}</b></div>

                    <hr className="divider" />

                    <MetaGrid video={video} />

                    <button id="resetBtn" onClick={onReset}>
                        Analyze another video
                        <ArrowLeftIcon />
                    </button>
                </div>
            </div>

            <FrameStrip frames={frames} onSelectFrame={onSelectFrame} />

            <PipelineCard analysis={analysis} />

            {selectedFrame && (
                <FrameViewer
                    key={selectedFrame.index}
                    frame={selectedFrame}
                    frameCount={frames.status === "loaded" ? frames.frames.length : 0}
                    prediction={prediction.prediction}
                    onClose={onCloseFrame}
                />
            )}
        </>
    );
}
