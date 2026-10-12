import { Dropzone } from "../components/Dropzone";
import "../styles/upload.css";

interface UploadViewProps {
    fileName: string | null;
    isAnalyzing: boolean;
    error: string | null;
    onFile: (file: File) => void;
    onAnalyze: () => void;
}

export function UploadView({ fileName, isAnalyzing, error, onFile, onAnalyze }: UploadViewProps) {
    return (
        <div className="hero" id="uploadHero">
            <div className="hero-text">
                <div className="eyebrow-hero">Deepfake Detection</div>
                <h1 className="hero-title">Detect<br /><span className="accent">Deepfakes</span></h1>
                <p className="hero-subtitle">Upload a video and let AI detect signs of manipulation.</p>
            </div>

            <div className="card" id="uploadCard">
                <Dropzone fileName={fileName} onFile={onFile} />

                <button id="predictBtn" className={isAnalyzing ? "loading" : undefined}
                    disabled={isAnalyzing} onClick={onAnalyze}>
                    <span className="spinner"></span>
                    <span>{isAnalyzing ? "Analyzing..." : "Analyze Video"}</span>
                </button>

                <div className="error">{error}</div>
            </div>
        </div>
    );
}
