import type { ReactNode } from "react";
import { MODEL } from "../constants/model";
import type { Analysis, SampledFrame } from "../types/analysis";
import { formatPercent, formatTimestamp } from "../utils/format";
import "../styles/pipeline.css";

const number = (value: number) => value.toLocaleString("en-US");

// Frames shown as thumbnails in the sampling step: first, two in between, last
const THUMBNAIL_POSITIONS = [0, 5, 10, 15];

interface PipelineStepProps {
    title: string;
    value: ReactNode;
    detail: ReactNode;
    children?: ReactNode;
}

function PipelineStep({ title, value, detail, children }: PipelineStepProps) {
    return (
        <li className="pipeline-step">
            <div className="pipeline-title">{title}</div>
            <div className="pipeline-value">{value}</div>
            <div className="pipeline-detail">{detail}</div>
            {children}
        </li>
    );
}

// The video's length: the browser's reading of the file when it has one,
// otherwise only how far into the video the sampled frames reach
function VideoStep({ duration, frames }: { duration: number | null; frames: SampledFrame[] | null }) {
    if (duration !== null && !isNaN(duration)) {
        return <PipelineStep title="Video" value={`${formatTimestamp(duration)} long`} detail="The uploaded clip" />;
    }

    const lastTimestamp = frames?.at(-1)?.timestamp ?? null;

    if (lastTimestamp !== null) {
        return (
            <PipelineStep
                title="Video"
                value={`Last frame at ${formatTimestamp(lastTimestamp)}`}
                detail="Exact length unavailable in this browser"
            />
        );
    }

    return <PipelineStep title="Video" value="—" detail="The uploaded clip" />;
}

// How the model reached its decision, step by step, with this analysis's values
export function PipelineCard({ analysis }: { analysis: Analysis }) {
    const { video, prediction, frames } = analysis;
    const loadedFrames = frames.status === "loaded" ? frames.frames : null;
    const firstTimestamp = loadedFrames?.at(0)?.timestamp ?? null;
    const lastTimestamp = loadedFrames?.at(-1)?.timestamp ?? null;
    const isFake = prediction.prediction === "fake";

    return (
        <section className="card pipeline-card">
            <div className="eyebrow">How the model decided</div>

            <ol className="pipeline">
                <VideoStep duration={video.duration} frames={loadedFrames} />

                <PipelineStep
                    title="Sampled frames"
                    value={`${MODEL.sampledFrames} frames`}
                    detail={loadedFrames
                        ? `Evenly spaced, ${formatTimestamp(firstTimestamp)} to ${formatTimestamp(lastTimestamp)}`
                        : "Evenly spaced across the video"}
                >
                    <div className="pipeline-thumbs">
                        {loadedFrames
                            ? THUMBNAIL_POSITIONS.map((i) => loadedFrames.at(i)).filter((frame) => frame !== undefined).map((frame) => (
                                <img key={frame.index} src={frame.imageUrl} alt="" />
                            ))
                            : frames.status === "loading" && THUMBNAIL_POSITIONS.map((i) => (
                                <div key={i} className="pipeline-thumb-placeholder" data-testid="pipeline-thumb-placeholder" />
                            ))}
                    </div>
                </PipelineStep>

                <PipelineStep
                    title="CNN"
                    value={MODEL.backbone}
                    detail={`Each ${MODEL.inputSize}×${MODEL.inputSize} frame → ${number(MODEL.featureSize)} features`}
                />

                <PipelineStep
                    title="Average"
                    value={`${MODEL.sampledFrames} × ${number(MODEL.featureSize)} → ${number(MODEL.featureSize)}`}
                    detail="One feature vector for the whole video"
                />

                <PipelineStep
                    title="Classifier"
                    value={`${number(MODEL.featureSize)} → ${MODEL.embeddingSize} → ${MODEL.classes}`}
                    detail="Two scores: real and fake"
                />

                <PipelineStep
                    title="Result"
                    value={<span className={isFake ? "pipeline-fake" : "pipeline-real"}>{isFake ? "Fake" : "Real"}</span>}
                    detail="Softmax probabilities"
                >
                    <div className="pipeline-bar" aria-hidden="true">
                        <div className="pipeline-bar-real" style={{ width: formatPercent(prediction.probabilities.real) }} />
                        <div className="pipeline-bar-fake" style={{ width: formatPercent(prediction.probabilities.fake) }} />
                    </div>
                    <div className="pipeline-probabilities">
                        <span>Real {formatPercent(prediction.probabilities.real)}</span>
                        <span>Fake {formatPercent(prediction.probabilities.fake)}</span>
                    </div>
                </PipelineStep>
            </ol>
        </section>
    );
}
