import { Header } from "./components/Header";
import { useVideoAnalysis } from "./hooks/useVideoAnalysis";
import { ResultView } from "./views/ResultView";
import { UploadView } from "./views/UploadView";

export default function App() {
    const { state, selectFile, analyze, reset, selectFrame, closeFrame } = useVideoAnalysis();

    return (
        <>
            <Header />

            {state.status === "done" ? (
                <ResultView
                    analysis={state.analysis}
                    onReset={reset}
                    onSelectFrame={selectFrame}
                    onCloseFrame={closeFrame}
                />
            ) : (
                <UploadView
                    fileName={state.selection?.file.name ?? null}
                    isAnalyzing={state.status === "analyzing"}
                    error={state.status === "error" ? state.error : null}
                    onFile={selectFile}
                    onAnalyze={analyze}
                />
            )}
        </>
    );
}
