import type { ReactNode } from "react";
import type { Analysis, SampledFrame } from "../types/analysis";
import type { ModelInfoState } from "../types/model";
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

// Shown in the model steps when /api/model didn't answer
const MODEL_UNAVAILABLE = "Model details unavailable";

interface PipelineCardProps {
    analysis: Analysis;
    modelInfo: ModelInfoState;
}

// How the model reached its decision, step by step, with this analysis's values
export function PipelineCard({ analysis, modelInfo }: PipelineCardProps) {
    const { video, prediction, frames } = analysis;
    const model = modelInfo.status === "loaded" ? modelInfo.info : null;
    // While /api/model is in flight the steps show a dash; after a failure, why
    const missing = modelInfo.status === "unavailable" ? MODEL_UNAVAILABLE : "—";
    // The frames themselves say how many were sampled, even without model details
    const sampledFrames = model?.sampledFrames ?? loadedFramesCount(frames);
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
                    value={sampledFrames !== null ? `${sampledFrames} frames` : "—"}
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
                    value={model ? model.backbone : missing}
                    detail={model
                        ? `Each ${model.inputSize}×${model.inputSize} frame → ${number(model.featureSize)} features`
                        : "Features for each frame"}
                />

                <PipelineStep
                    title="Average"
                    value={model
                        ? `${model.sampledFrames} × ${number(model.featureSize)} → ${number(model.featureSize)}`
                        : missing}
                    detail="One feature vector for the whole video"
                />

                <PipelineStep
                    title="Classifier"
                    value={model
                        ? `${number(model.featureSize)} → ${model.embeddingSize} → ${model.classes.length}`
                        : missing}
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

function loadedFramesCount(frames: Analysis["frames"]): number | null {
    return frames.status === "loaded" ? frames.frames.length : null;
}
