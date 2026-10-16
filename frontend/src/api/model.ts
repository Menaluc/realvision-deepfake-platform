import { requestJson } from "./client";
import type { ModelInfo } from "../types/model";

// Facts about the model the server runs, read from the loaded model
export function getModelInfo(): Promise<ModelInfo> {
    return requestJson<ModelInfo>("/api/model", undefined, "Model details unavailable");
}
