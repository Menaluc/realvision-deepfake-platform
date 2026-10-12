import type { PredictionResult } from "../types/prediction";
import { CheckIcon, WarningIcon } from "./icons";

export function VerdictBadge({ prediction }: { prediction: PredictionResult["prediction"] }) {
    const isFake = prediction === "fake";

    return (
        <div className={"verdict-badge " + (isFake ? "fake" : "real")}>
            {isFake ? <WarningIcon /> : <CheckIcon />}
            <span>{isFake ? "Fake" : "Real"}</span>
        </div>
    );
}
