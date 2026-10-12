import { useState, type DragEvent } from "react";
import { UploadIcon } from "./icons";

interface DropzoneProps {
    fileName: string | null;
    onFile: (file: File) => void;
}

export function Dropzone({ fileName, onFile }: DropzoneProps) {
    const [isDragOver, setIsDragOver] = useState(false);

    function handleDragOver(e: DragEvent) {
        e.preventDefault();
        setIsDragOver(true);
    }

    function handleDragLeave(e: DragEvent) {
        e.preventDefault();
        setIsDragOver(false);
    }

    function handleDrop(e: DragEvent) {
        handleDragLeave(e);
        const file = e.dataTransfer.files[0];
        if (file) onFile(file);
    }

    return (
        <label
            className={"dropzone" + (isDragOver ? " dragover" : "")}
            onDragOver={handleDragOver}
            onDragEnter={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <span className="icon-circle">
                <UploadIcon />
            </span>
            <span className="title">{fileName ?? "Upload a video"}</span>
            <span className="hint">Drag &amp; drop or click to browse — MP4, MOV up to 20MB</span>
            <input
                type="file"
                accept="video/*"
                aria-label="Video file"
                onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) onFile(file);
                    // The selected file lives in state; clear the input so the same file can be picked again
                    e.target.value = "";
                }}
            />
        </label>
    );
}
