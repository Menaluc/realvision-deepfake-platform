import { useEffect, useState } from "react";
import { getModelInfo } from "../api/model";
import type { ModelInfoState } from "../types/model";

// Loads the model's details once. The server's model can't change without a
// restart, so there is no retry: a degraded server stays degraded until then.
export function useModelInfo(): ModelInfoState {
    const [state, setState] = useState<ModelInfoState>({ status: "loading" });

    useEffect(() => {
        // Ignores the answer if the component unmounted while it was in flight
        let active = true;

        getModelInfo().then(
            (info) => { if (active) setState({ status: "loaded", info }); },
            () => { if (active) setState({ status: "unavailable" }); }
        );

        return () => { active = false; };
    }, []);

    return state;
}
